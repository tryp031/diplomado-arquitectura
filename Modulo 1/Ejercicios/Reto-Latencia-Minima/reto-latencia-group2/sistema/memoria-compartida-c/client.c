/*
 * Variante D — cliente medidor sobre memoria compartida.
 *
 * Contrato del harness (ver ../README.md):
 *   --host <ignorado> --port 9103 --payload 32
 *   --warmup 100000 --iters 1000000 --out <ruta CSV>
 *
 * Frontera de medición F1 (ADR-001), idéntica a la de la variante B:
 *   t0 = inmediatamente ANTES de escribir el estímulo
 *   t1 = inmediatamente DESPUÉS de tener la respuesta completa en buffer local
 *
 * Añade algo que las otras variantes no necesitan: mide el PISO DE MEDICIÓN
 * (el coste del propio par de llamadas al reloj). A esta escala el instrumento
 * ya no es despreciable frente a lo medido, y callarlo sería deshonesto.
 */
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#ifdef __APPLE__
#include <pthread.h>
#endif

#include "common.h"
#include "../clasificador.h"

static int cmp_u64(const void *a, const void *b)
{
    uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b;
    return (x > y) - (x < y);
}

int main(int argc, char **argv)
{
    const char *host = "127.0.0.1";
    int port = 9103;
    size_t payload = 32;
    uint64_t warmup = 100000, iters = 1000000;
    const char *salida = NULL;
    int reintentos = 50;
    uint64_t lote = 1000, lote_rondas = 200;   /* contraste por lotes, ver mas abajo */
    const char *ruta_tabla = "tabla-hosts.csv";
    int sin_clasificar = 0;                     /* corrida de control, ADR-004 §5 */

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--host") && i + 1 < argc)            host = argv[++i];
        else if (!strcmp(argv[i], "--port") && i + 1 < argc)       port = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--payload") && i + 1 < argc)    payload = (size_t)atol(argv[++i]);
        else if (!strcmp(argv[i], "--warmup") && i + 1 < argc)     warmup = strtoull(argv[++i], NULL, 10);
        else if (!strcmp(argv[i], "--iters") && i + 1 < argc)      iters = strtoull(argv[++i], NULL, 10);
        else if (!strcmp(argv[i], "--out") && i + 1 < argc)        salida = argv[++i];
        else if (!strcmp(argv[i], "--reintentos") && i + 1 < argc) reintentos = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--lote") && i + 1 < argc)        lote = strtoull(argv[++i], NULL, 10);
        else if (!strcmp(argv[i], "--lote-rondas") && i + 1 < argc) lote_rondas = strtoull(argv[++i], NULL, 10);
        else if (!strcmp(argv[i], "--tabla") && i + 1 < argc)        ruta_tabla = argv[++i];
        else if (!strcmp(argv[i], "--sin-clasificar"))               sin_clasificar = 1;
        else { fprintf(stderr, "argumento desconocido: %s\n", argv[i]); return 2; }
    }
    (void)host;

    if (!salida)  { fprintf(stderr, "error: falta --out\n"); return 2; }
    if (iters == 0) { fprintf(stderr, "error: --iters debe ser > 0\n"); return 2; }
    if (payload == 0 || payload > PAYLOAD_MAX) {
        fprintf(stderr, "error: --payload debe estar entre 1 y %zu\n", (size_t)PAYLOAD_MAX);
        return 2;
    }
    if (payload < 8) { fprintf(stderr, "error: --payload debe ser >= 8 (host_id + seq)\n"); return 2; }

    /* FUERA de la ruta caliente. */
    if (clasificador_cargar(ruta_tabla) < 0) return 1;
    clasificador_resumen("cliente D", ruta_tabla);
    if (g_tabla_n != TABLA_MAX) {
        fprintf(stderr, "el ciclo exige exactamente %d hosts, hay %d\n", TABLA_MAX, g_tabla_n);
        return 1;
    }

#ifdef __APPLE__
    if (pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0) != 0)
        fprintf(stderr, "[cliente D] aviso: no se pudo fijar la clase de QoS\n");
#endif

    /* --- "Conexión": abrir la región que creó el servidor, con reintentos --------
       Equivale al connect() de la variante B y, como allí, se paga fuera de la
       medición (ADR-001: la frontera F1 excluye el establecimiento). */
    char nombre[64];
    snprintf(nombre, sizeof nombre, NOMBRE_SHM_FMT, port);

    int fd = -1;
    for (int i = 0; i < reintentos; i++) {
        fd = shm_open(nombre, O_RDWR, 0600);
        if (fd >= 0) break;
        usleep(50000);
    }
    if (fd < 0) {
        fprintf(stderr, "error: no se pudo abrir %s — ¿esta corriendo el servidor D?\n", nombre);
        return 1;
    }

    region_t *r = mmap(NULL, sizeof(region_t), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    close(fd);
    if (r == MAP_FAILED) { perror("mmap"); return 1; }

    /* Ciclo de 16 estimulos PRECONSTRUIDOS, recorrido con `i & 15` (ADR-004 §4).
       Mezcla en el bucle medido: 10 LOCAL / 6 EXTERNO / 0 DESCONOCIDO. Que falte
       DESCONOCIDO no sesga: `clasificar` es de tiempo constante (16 csel, 0 saltos). */
    static unsigned char ciclo[TABLA_MAX][PAYLOAD_MAX];
    for (int i = 0; i < TABLA_MAX; i++)
        armar_estimulo(ciclo[i], payload, g_tabla_id[i], (uint32_t)i);

    unsigned char recibido[PAYLOAD_MAX];

    /* --- Array de muestras PREASIGNADO y PRE-TOCADO --------------------------
       calloc no falla las páginas hasta el primer acceso. Si el primer write
       ocurriera dentro del bucle caliente, cada página nueva provocaría un fallo
       de página — una llamada al kernel, justo lo que esta variante evita.
       Escribirlo entero aquí lo saca de la medición. */
    uint64_t *latencias = malloc(iters * sizeof(uint64_t));
    if (!latencias) { fprintf(stderr, "error: sin memoria para %llu muestras\n",
                              (unsigned long long)iters); return 1; }
    memset(latencias, 0, iters * sizeof(uint64_t));

    /* --- Piso de medición: cuánto cuesta el instrumento ----------------------- */
    {
        enum { N_PISO = 100000 };
        uint64_t *piso = malloc(N_PISO * sizeof(uint64_t));
        if (piso) {
            memset(piso, 0, N_PISO * sizeof(uint64_t));
            for (int i = 0; i < N_PISO; i++) {
                uint64_t a = ahora_ns();
                uint64_t b = ahora_ns();
                piso[i] = b - a;
            }
            qsort(piso, N_PISO, sizeof(uint64_t), cmp_u64);
            printf("[cliente D] piso de medicion (par de llamadas al reloj): "
                   "min=%llu ns  p50=%llu ns  p99=%llu ns\n",
                   (unsigned long long)piso[0],
                   (unsigned long long)piso[N_PISO / 2],
                   (unsigned long long)piso[(N_PISO * 99) / 100]);
            printf("[cliente D] granularidad del reloj ~41.67 ns (contador de 24 MHz): las medidas\n"
                   "            individuales estan CUANTIZADAS en multiplos de ese valor. Reportarlo.\n");
            free(piso);
        }
    }

    /* Base monótona: soporta reinicios del cliente sin confundirse con valores viejos. */
    uint64_t base = atomic_load_explicit(&r->peticion.seq, memory_order_acquire);
    uint64_t base_resp = atomic_load_explicit(&r->respuesta.seq, memory_order_acquire);
    if (base_resp > base) base = base_resp;

    uint64_t n = base;
    uint64_t desajustes = 0, giros_perdidos = 0;

    /* --- El intercambio. Es toda la variante: 4 líneas. --------------------- */
#define INTERCAMBIO(EST)                                                                  \
    do {                                                                                  \
        memcpy(r->peticion.dato, (EST), payload);                                         \
        atomic_store_explicit(&r->peticion.seq, ++n, memory_order_release);               \
        uint64_t giros = 0;                                                               \
        while (atomic_load_explicit(&r->respuesta.seq, memory_order_acquire) != n) {      \
            if (++giros > LIMITE_SPIN) { giros_perdidos++; break; }                       \
            pausa_spin();                                                                 \
        }                                                                                 \
        memcpy(recibido, r->respuesta.dato, payload);                                     \
    } while (0)

    /* --- WARMUP: descartado (ESPEC §2) -------------------------------------- */
    /* ---- AUTOPRUEBA: verificar que el sistema CLASIFICA antes de medir nada ---- */
    for (int i = 0; i < TABLA_MAX; i++) {
        INTERCAMBIO(ciclo[i]);
        uint32_t eco;
        memcpy(&eco, recibido + OFF_ECO_ID, sizeof eco);
        if (eco != g_tabla_id[i]) {
            fprintf(stderr, "[cliente D] eco incorrecto en la entrada %d — revisar barreras\n", i);
            return 1;
        }
        if (!sin_clasificar && recibido[OFF_VEREDICTO] != g_tabla_ver[i]) {
            fprintf(stderr, "[cliente D] veredicto incorrecto en la entrada %d\n", i);
            return 1;
        }
    }
    if (!sin_clasificar) {   /* El caso DESCONOCIDO — el "pepito5" de las notas del equipo. */
        unsigned char e[PAYLOAD_MAX];
        armar_estimulo(e, payload, id_de_ip("203.0.113.77"), 0);  /* TEST-NET-3, RFC 5737 */
        INTERCAMBIO(e);
        if (recibido[OFF_VEREDICTO] != VEREDICTO_DESCONOCIDO) {
            fprintf(stderr, "[cliente D] un host fuera de tabla devolvio %u\n", recibido[OFF_VEREDICTO]);
            return 1;
        }
        printf("[cliente D] autoprueba OK: %d hosts de tabla + 1 desconocido\n", TABLA_MAX);
    } else {
        printf("[cliente D] MODO CONTROL (--sin-clasificar): solo se verifica el eco.\n");
    }
    fflush(stdout);

    printf("[cliente D] warmup %llu iteraciones...\n", (unsigned long long)warmup);
    fflush(stdout);
    for (uint64_t i = 0; i < warmup; i++) INTERCAMBIO(ciclo[i & 15]);

    /* --- MEDICIÓN ------------------------------------------------------------ */
    printf("[cliente D] midiendo %llu iteraciones...\n", (unsigned long long)iters);
    fflush(stdout);

    for (uint64_t i = 0; i < iters; i++) {
        const unsigned char *est = ciclo[i & 15];
        uint64_t t0 = ahora_ns();
        INTERCAMBIO(est);
        uint64_t t1 = ahora_ns();
        latencias[i] = t1 - t0;

        /* Validación FUERA de la sección cronometrada (ADR-002, riesgo de barreras
           mal puestas): si las barreras fallaran, el eco no coincidiría. Se comprueba
           el eco y no el veredicto porque el eco vale en ambos modos. */
        uint32_t eco;
        memcpy(&eco, recibido + OFF_ECO_ID, sizeof eco);
        if (eco != g_tabla_id[i & 15]) desajustes++;
    }

    if (giros_perdidos) fprintf(stderr, "[cliente D] AVISO: %llu esperas agotaron el limite de giro\n",
                                (unsigned long long)giros_perdidos);
    if (desajustes)     fprintf(stderr, "[cliente D] AVISO: %llu respuestas con contenido inesperado "
                                "— revisar barreras de memoria\n", (unsigned long long)desajustes);
    if (!desajustes && !giros_perdidos)
        printf("[cliente D] integridad OK: %llu/%llu respuestas correctas\n",
               (unsigned long long)iters, (unsigned long long)iters);

    /* --- CONTRASTE POR LOTES ------------------------------------------------
       Con ~41.67 ns de granularidad, una latencia de unos cientos de ns cabe en
       3-5 tics del reloj: la mediana por muestra sale cuantizada. Cronometrar un
       LOTE de N intercambios con un solo par de llamadas al reloj y dividir da una
       media con precision muy por debajo del tic.

       NO sustituye a los percentiles: una media por lote no tiene cola, y la cola es
       justo lo que interesa (AC-2). Es un CONTRASTE: si la media por lotes y el p50
       por muestra no coinciden, una de las dos mediciones esta mal. Se reportan las
       dos, etiquetadas, nunca una en lugar de la otra. */
    if (lote > 0 && lote_rondas > 0) {
        uint64_t *medias = malloc(lote_rondas * sizeof(uint64_t));
        if (medias) {
            memset(medias, 0, lote_rondas * sizeof(uint64_t));
            for (uint64_t k = 0; k < lote_rondas; k++) {
                uint64_t t0 = ahora_ns();
                for (uint64_t j = 0; j < lote; j++) INTERCAMBIO(ciclo[j & 15]);
                uint64_t t1 = ahora_ns();
                medias[k] = (t1 - t0) / lote;
            }
            qsort(medias, lote_rondas, sizeof(uint64_t), cmp_u64);
            printf("[cliente D] contraste por lotes (%llu intercambios x %llu rondas): "
                   "min=%llu ns  mediana=%llu ns  max=%llu ns por intercambio\n",
                   (unsigned long long)lote, (unsigned long long)lote_rondas,
                   (unsigned long long)medias[0],
                   (unsigned long long)medias[lote_rondas / 2],
                   (unsigned long long)medias[lote_rondas - 1]);
            printf("[cliente D] (media por lote: sin cola. Los percentiles salen de las "
                   "muestras individuales del CSV.)\n");
            free(medias);
        }
    }

    munmap(r, sizeof(region_t));

    /* --- VOLCADO: al final, nunca dentro del bucle (ESPEC §5) ---------------- */
    FILE *fh = fopen(salida, "w");
    if (!fh) { perror("fopen"); free(latencias); return 1; }
    fputs("iteracion,latencia_ns\n", fh);
    for (uint64_t i = 0; i < iters; i++)
        fprintf(fh, "%llu,%llu\n", (unsigned long long)(i + 1),
                (unsigned long long)latencias[i]);
    fclose(fh);
    free(latencias);

    printf("[cliente D] %llu muestras -> %s\n", (unsigned long long)iters, salida);
    return 0;
}
