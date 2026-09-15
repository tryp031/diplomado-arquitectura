/*
 * CONTROL Bc — cliente medidor sobre TCP crudo, en C.
 *
 * Traducción literal de variante-B-tcp/client.py. Todo igual salvo el lenguaje:
 * misma frontera F1 (ADR-001), mismo warmup, mismo array preasignado, mismo CSV.
 * El reloj viene de ../reloj.h, que es el mismo que usa la variante D (AC-3).
 */
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#ifdef __APPLE__
#include <pthread.h>
#endif

#include "../reloj.h"
#include "../clasificador.h"

#define PAYLOAD_MAX 4096

int main(int argc, char **argv)
{
    const char *host = "127.0.0.1";
    int port = 9111;
    size_t payload = 32;
    uint64_t warmup = 100000, iters = 1000000;
    const char *salida = NULL;
    int reintentos = 50;
    const char *ruta_tabla = "tabla-hosts.csv";

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--host") && i + 1 < argc)            host = argv[++i];
        else if (!strcmp(argv[i], "--port") && i + 1 < argc)       port = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--payload") && i + 1 < argc)    payload = (size_t)atol(argv[++i]);
        else if (!strcmp(argv[i], "--warmup") && i + 1 < argc)     warmup = strtoull(argv[++i], NULL, 10);
        else if (!strcmp(argv[i], "--iters") && i + 1 < argc)      iters = strtoull(argv[++i], NULL, 10);
        else if (!strcmp(argv[i], "--out") && i + 1 < argc)        salida = argv[++i];
        else if (!strcmp(argv[i], "--reintentos") && i + 1 < argc) reintentos = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--tabla") && i + 1 < argc)       ruta_tabla = argv[++i];
        else { fprintf(stderr, "argumento desconocido: %s\n", argv[i]); return 2; }
    }
    if (!salida) { fprintf(stderr, "error: falta --out\n"); return 2; }
    if (payload == 0 || payload > PAYLOAD_MAX) { fprintf(stderr, "--payload fuera de rango\n"); return 2; }
    if (payload < 8) { fprintf(stderr, "--payload debe ser >= 8 (host_id + seq)\n"); return 2; }

    /* FUERA de la ruta caliente. */
    if (clasificador_cargar(ruta_tabla) < 0) return 1;
    clasificador_resumen("cliente Bc", ruta_tabla);
    if (g_tabla_n != TABLA_MAX) {
        fprintf(stderr, "el ciclo exige exactamente %d hosts, hay %d\n", TABLA_MAX, g_tabla_n);
        return 1;
    }

    signal(SIGPIPE, SIG_IGN);
#ifdef __APPLE__
    pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
#endif

    /* ADR-003: verificar el instrumento antes de usarlo. p50 esperado ~5000 ns. */
    uint64_t gran = reloj_verificar("cliente Bc");
    reloj_avisar_si_grueso("cliente Bc", gran, 5000);

    /* --- Conexión con reintentos. Fuera de la medición (F1 excluye el handshake). */
    struct sockaddr_in dir;
    memset(&dir, 0, sizeof dir);
    dir.sin_family = AF_INET;
    dir.sin_port = htons((uint16_t)port);
    if (inet_pton(AF_INET, host, &dir.sin_addr) != 1) { fprintf(stderr, "host invalido\n"); return 2; }

    int s = -1;
    for (int i = 0; i < reintentos; i++) {
        s = socket(AF_INET, SOCK_STREAM, 0);
        if (s >= 0 && connect(s, (struct sockaddr *)&dir, sizeof dir) == 0) break;
        if (s >= 0) { close(s); s = -1; }
        usleep(50000);
    }
    if (s < 0) { fprintf(stderr, "error: no se pudo conectar a %s:%d\n", host, port); return 1; }

    int uno = 1;
    setsockopt(s, IPPROTO_TCP, TCP_NODELAY, &uno, sizeof uno);

    /*
     * Ciclo de 16 estímulos PRECONSTRUIDOS, recorrido con `i & 15`: un AND, sin
     * módulo (división) y sin construir nada dentro del bucle medido.
     * Mezcla: 10 LOCAL / 6 EXTERNO / 0 DESCONOCIDO — declarada en ADR-004 §4.
     * Que falte DESCONOCIDO no sesga nada: `clasificar` es de tiempo constante
     * (verificado: 16 csel, 0 saltos condicionales). Se ejercita en la autoprueba.
     */
    static unsigned char ciclo[TABLA_MAX][PAYLOAD_MAX];
    for (int i = 0; i < TABLA_MAX; i++)
        armar_estimulo(ciclo[i], payload, g_tabla_id[i], (uint32_t)i);

    unsigned char buf[PAYLOAD_MAX];

    uint64_t *lat = (uint64_t *)malloc(iters * sizeof(uint64_t));
    if (!lat) { fprintf(stderr, "sin memoria\n"); return 1; }
    memset(lat, 0, iters * sizeof(uint64_t));   /* pre-tocar: sin fallos de pagina al medir */

    uint64_t errores = 0;

#define INTERCAMBIO(EST)                                                       \
    do {                                                                       \
        const unsigned char *_e = (EST);                                       \
        size_t env = 0;                                                        \
        while (env < payload) {                                                \
            ssize_t k = send(s, _e + env, payload - env, 0);                   \
            if (k <= 0) { errores++; break; }                                  \
            env += (size_t)k;                                                  \
        }                                                                      \
        size_t rec = 0;                                                        \
        while (rec < payload) {                                                \
            ssize_t k = recv(s, buf + rec, payload - rec, 0);                  \
            if (k <= 0) { errores++; break; }                                  \
            rec += (size_t)k;                                                  \
        }                                                                      \
    } while (0)

    /* ---- AUTOPRUEBA: verificar que el sistema CLASIFICA antes de medir nada ----
       Sin esto, el harness podría estar midiendo un transporte que transporta basura. */
    for (int i = 0; i < TABLA_MAX; i++) {
        INTERCAMBIO(ciclo[i]);
        uint32_t eco;
        memcpy(&eco, buf + OFF_ECO_ID, sizeof eco);
        if (buf[OFF_VEREDICTO] != g_tabla_ver[i] || eco != g_tabla_id[i]) {
            fprintf(stderr, "[cliente Bc] error de integridad en la entrada %d\n", i);
            return 1;
        }
    }
    {   /* El caso DESCONOCIDO — el "pepito5" de las notas del equipo. */
        unsigned char e[PAYLOAD_MAX];
        armar_estimulo(e, payload, id_de_ip("203.0.113.77"), 0);  /* TEST-NET-3, RFC 5737 */
        INTERCAMBIO(e);
        if (buf[OFF_VEREDICTO] != VEREDICTO_DESCONOCIDO) {
            fprintf(stderr, "[cliente Bc] un host fuera de tabla devolvio %u\n", buf[OFF_VEREDICTO]);
            return 1;
        }
    }
    printf("[cliente Bc] autoprueba OK: %d hosts de tabla + 1 desconocido\n", TABLA_MAX);
    fflush(stdout);

    printf("[cliente Bc] warmup %llu iteraciones...\n", (unsigned long long)warmup);
    fflush(stdout);
    for (uint64_t i = 0; i < warmup; i++) INTERCAMBIO(ciclo[i & 15]);

    printf("[cliente Bc] midiendo %llu iteraciones...\n", (unsigned long long)iters);
    fflush(stdout);
    for (uint64_t i = 0; i < iters; i++) {
        const unsigned char *est = ciclo[i & 15];
        uint64_t t0 = ahora_ns();
        INTERCAMBIO(est);
        uint64_t t1 = ahora_ns();
        lat[i] = t1 - t0;
    }

    if (errores) fprintf(stderr, "[cliente Bc] AVISO: %llu errores de E/S\n",
                         (unsigned long long)errores);
    else printf("[cliente Bc] integridad OK: %llu/%llu intercambios completos\n",
                (unsigned long long)iters, (unsigned long long)iters);
    close(s);

    FILE *fh = fopen(salida, "w");
    if (!fh) { perror("fopen"); free(lat); return 1; }
    fputs("iteracion,latencia_ns\n", fh);
    for (uint64_t i = 0; i < iters; i++)
        fprintf(fh, "%llu,%llu\n", (unsigned long long)(i + 1), (unsigned long long)lat[i]);
    fclose(fh);
    free(lat);

    printf("[cliente Bc] %llu muestras -> %s\n", (unsigned long long)iters, salida);
    return 0;
}
