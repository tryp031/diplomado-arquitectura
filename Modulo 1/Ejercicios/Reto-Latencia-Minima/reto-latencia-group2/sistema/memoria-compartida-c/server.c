/*
 * Variante Memoria compartida C — servidor de eco sobre memoria compartida con espera activa.
 *
 * Contrato del harness (ver ../README.md):
 *   --host <ignorado>  --port <9103>  --payload <32>
 *
 * Cumple los requisitos del enunciado:
 *   - Escucha permanentemente: gira sobre la bandera de petición, sin fin.
 *   - Ante un estímulo retorna una respuesta ESPECÍFICA: un veredicto
 *     LOCAL/EXTERNO/DESCONOCIDO que depende del host recibido (dominio, ADR-004).
 *   - Cero llamadas al sistema en la ruta caliente. Cero intervención del planificador.
 *
 * El precio, que hay que decir en voz alta: este proceso consume un núcleo al 100 %
 * de forma permanente, haga o no trabajo útil. Ver ADR-002.
 */
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
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

static char g_nombre[64];
static volatile sig_atomic_t g_salir = 0;

static void al_terminar(int sig) { (void)sig; g_salir = 1; }

static void limpiar(void)
{
    if (g_nombre[0]) shm_unlink(g_nombre);
}

int main(int argc, char **argv)
{
    const char *host = "127.0.0.1";  /* aceptado por contrato, sin uso aquí */
    int port = 9103;
    size_t payload = 32;
    const char *ruta_tabla = "tabla-hosts.csv";
    int sin_clasificar = 0;

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--host") && i + 1 < argc)          host = argv[++i];
        else if (!strcmp(argv[i], "--port") && i + 1 < argc)     port = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--payload") && i + 1 < argc)  payload = (size_t)atol(argv[++i]);
        else if (!strcmp(argv[i], "--tabla") && i + 1 < argc)    ruta_tabla = argv[++i];
        else if (!strcmp(argv[i], "--sin-clasificar"))           sin_clasificar = 1;
        else { fprintf(stderr, "argumento desconocido: %s\n", argv[i]); return 2; }
    }
    (void)host;

    if (payload == 0 || payload > PAYLOAD_MAX) {
        fprintf(stderr, "error: --payload debe estar entre 1 y %zu (cabe en una linea de cache)\n",
                (size_t)PAYLOAD_MAX);
        return 2;
    }
    if (payload < 8) { fprintf(stderr, "error: --payload debe ser >= 8 (host_id + seq)\n"); return 2; }

    /* FUERA de la ruta caliente: una sola vez, al arrancar. */
    if (clasificador_cargar(ruta_tabla) < 0) return 1;
    clasificador_resumen("servidor D", ruta_tabla);

    /*
     * --sin-clasificar es la CORRIDA DE CONTROL de ADR-004 §5: responde un veredicto
     * fijo, sin consultar la tabla. La diferencia contra la corrida normal es el coste
     * real del dominio. Sin esta medida, "clasificar es despreciable" seria una
     * afirmacion sin respaldo — y a 83 ns de p50, 2 ns ya es el 2,4 %.
     */
    if (sin_clasificar)
        printf("[servidor D] MODO CONTROL: sin clasificar (veredicto fijo). Solo para medir\n"
               "             el coste del dominio. NO usar como resultado del sistema.\n");

    /*
     * Sin afinidad de núcleo: thread_policy_set(THREAD_AFFINITY_POLICY) devuelve
     * KERN_NOT_SUPPORTED en macOS/arm64 (verificado). La clase de QoS es lo único
     * disponible: SUGIERE al planificador usar núcleos de rendimiento. No lo garantiza,
     * y por eso la cola de latencia seguirá mostrando migraciones. Ver ADR-002.
     */
#ifdef __APPLE__
    if (pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0) != 0)
        fprintf(stderr, "[servidor D] aviso: no se pudo fijar la clase de QoS\n");
#endif

    snprintf(g_nombre, sizeof g_nombre, NOMBRE_SHM_FMT, port);

    /* Recrear siempre: en macOS ftruncate sobre un objeto ya dimensionado falla. */
    shm_unlink(g_nombre);
    int fd = shm_open(g_nombre, O_CREAT | O_EXCL | O_RDWR, 0600);
    if (fd < 0) { perror("shm_open"); return 1; }
    if (ftruncate(fd, (off_t)sizeof(region_t)) != 0) { perror("ftruncate"); limpiar(); return 1; }

    region_t *r = mmap(NULL, sizeof(region_t), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    close(fd);
    if (r == MAP_FAILED) { perror("mmap"); limpiar(); return 1; }

    memset(r, 0, sizeof *r);
    atomic_store_explicit(&r->peticion.seq, 0, memory_order_release);
    atomic_store_explicit(&r->respuesta.seq, 0, memory_order_release);

    signal(SIGINT, al_terminar);
    signal(SIGTERM, al_terminar);

    unsigned char respuesta[PAYLOAD_MAX];  /* buffer local, preasignado en la pila */
    memset(respuesta, 0, payload);
    unsigned char recibido[PAYLOAD_MAX];

    printf("[servidor D] shm=%s payload=%zuB region=%zuB — girando (un nucleo al 100%%)\n",
           g_nombre, payload, sizeof(region_t));
    fflush(stdout);

    uint64_t ultima = 0;

    /* ---- RUTA CALIENTE: sin llamadas al sistema, sin asignaciones, sin ramas extra ---- */
    while (!g_salir) {
        uint64_t s;
        /* Espera activa sobre la bandera. acquire: garantiza que el payload escrito
           por el cliente antes de su store(release) ya es visible aquí. */
        while ((s = atomic_load_explicit(&r->peticion.seq, memory_order_acquire)) == ultima) {
            if (g_salir) goto fin;
            pausa_spin();
        }
        ultima = s;

        /* Leer el estímulo: el dato tiene que cruzar de verdad, igual que en la
           variante TCP Python el servidor hace recv del payload completo. */
        memcpy(recibido, r->peticion.dato, payload);

        /* ---- EL DOMINIO. Tiempo constante: 16 csel, cero saltos condicionales.
                Sin llamadas al sistema, sin asignar, sin E/S. ~1-3 ns. ---- */
        uint32_t host_id;
        memcpy(&host_id, recibido + OFF_HOST_ID, sizeof host_id);
        respuesta[OFF_VEREDICTO] = sin_clasificar ? (uint8_t)VEREDICTO_LOCAL
                                                  : clasificar(host_id);
        memcpy(respuesta + OFF_ECO_ID, &host_id, sizeof host_id);

        memcpy(r->respuesta.dato, respuesta, payload);
        /* release: publica el payload ANTES de la bandera. Sin esta barrera el cliente
           puede ver seq actualizada y leer datos viejos. En arm64 eso ocurre de verdad. */
        atomic_store_explicit(&r->respuesta.seq, s, memory_order_release);
    }

fin:
    printf("[servidor D] fin, %llu peticiones atendidas\n", (unsigned long long)ultima);
    munmap(r, sizeof(region_t));
    limpiar();
    return 0;
}
