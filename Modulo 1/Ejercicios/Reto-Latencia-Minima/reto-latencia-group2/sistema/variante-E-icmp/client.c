/*
 * Variante E — ICMP echo.  LA IDEA DEL EQUIPO, HECHA BIEN.
 *
 * ═══════════════════════════════════════════════════════════════════════════════
 * ESTA VARIANTE NO CUMPLE EL ENUNCIADO. ESE ES EXACTAMENTE SU VALOR.
 *
 * El enunciado exige un sistema que «escuche permanentemente» y «retorne una respuesta
 * especifica». Aqui quien escucha y responde es EL KERNEL del sistema operativo, no un
 * proceso nuestro. El kernel devuelve el payload VERBATIM: no puede clasificar, porque
 * no ejecuta nuestro codigo. No hay veredicto. No hay sistema propio que disenar ni
 * herramientas que justificar.
 *
 * Por eso E es una LINEA BASE, no una variante del estudio. Y es la demostracion, con
 * numeros, de por que la idea original del equipo —«usar ping»— no habria servido como
 * entrega: no porque sea lenta, sino porque no hay nada nuestro en la ruta.
 *
 * Lo que si aporta, y ninguna otra variante aporta:
 *   1. Es el UNICO punto donde el respondedor es el kernel. Mide la pila de red del SO
 *      sin ningun proceso de usuario del otro lado.
 *   2. Con --destino a un host de internet da la LINEA BASE DE RED REAL (~40 ms), que
 *      es lo que hace visible el supuesto S3: medir en loopback elimina la red, y la
 *      red es el componente dominante en cualquier sistema real.
 * ═══════════════════════════════════════════════════════════════════════════════
 *
 * POR QUE UN SOCKET PROPIO Y NO EL COMANDO `ping`
 *
 * Invocar /sbin/ping por iteracion pagaria un fork+exec: 1-5 ms solo en arrancar el
 * proceso. Eso es la frontera F4 de ADR-001 («incluye el arranque del proceso»), que el
 * diseno descarta por medir el lanzador de procesos en vez del sistema. Con un socket
 * propio la frontera sigue siendo F1, igual que en A, B, C y D, y los numeros son
 * comparables.
 *
 * SOCK_DGRAM + IPPROTO_ICMP no requiere root en macOS. En Linux depende de
 * net.ipv4.ping_group_range; si falla, el programa lo dice y explica como habilitarlo.
 */
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <netinet/ip_icmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>

#include "../reloj.h"
#include "../clasificador.h"

#define PAYLOAD_MAX 4096
#define ICMP_CAB 8            /* tipo(1) codigo(1) suma(2) id(2) seq(2) */

/* Suma de verificacion de Internet (RFC 1071). El kernel la recalcula en algunos
   sistemas, pero calcularla aqui hace el programa correcto en todos. */
static uint16_t suma_internet(const void *datos, size_t n)
{
    const uint16_t *p = (const uint16_t *)datos;
    uint32_t s = 0;
    while (n > 1) { s += *p++; n -= 2; }
    if (n) s += *(const uint8_t *)p;
    while (s >> 16) s = (s & 0xFFFF) + (s >> 16);
    return (uint16_t)~s;
}

int main(int argc, char **argv)
{
    const char *destino = "127.0.0.1";
    size_t payload = 32;
    uint64_t warmup = 1000, iters = 10000;
    const char *salida = NULL;
    int timeout_ms = 2000;

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--destino") && i + 1 < argc)        destino = argv[++i];
        else if (!strcmp(argv[i], "--host") && i + 1 < argc)      destino = argv[++i];
        else if (!strcmp(argv[i], "--port") && i + 1 < argc)      (void)argv[++i]; /* por contrato */
        else if (!strcmp(argv[i], "--tabla") && i + 1 < argc)     (void)argv[++i]; /* por contrato */
        else if (!strcmp(argv[i], "--payload") && i + 1 < argc)   payload = (size_t)atol(argv[++i]);
        else if (!strcmp(argv[i], "--warmup") && i + 1 < argc)    warmup = strtoull(argv[++i], NULL, 10);
        else if (!strcmp(argv[i], "--iters") && i + 1 < argc)     iters = strtoull(argv[++i], NULL, 10);
        else if (!strcmp(argv[i], "--out") && i + 1 < argc)       salida = argv[++i];
        else if (!strcmp(argv[i], "--timeout-ms") && i + 1 < argc) timeout_ms = atoi(argv[++i]);
        else { fprintf(stderr, "argumento desconocido: %s\n", argv[i]); return 2; }
    }
    if (!salida) { fprintf(stderr, "error: falta --out\n"); return 2; }
    if (payload < 8 || payload > PAYLOAD_MAX) { fprintf(stderr, "--payload fuera de rango\n"); return 2; }

    uint64_t gran = reloj_verificar("cliente E");
    reloj_avisar_si_grueso("cliente E", gran, 30000);

    int s = socket(AF_INET, SOCK_DGRAM, IPPROTO_ICMP);
    if (s < 0) {
        fprintf(stderr,
            "error: no se pudo abrir el socket ICMP sin privilegios: %s\n"
            "  macOS: deberia funcionar sin root.\n"
            "  Linux: hace falta  sudo sysctl -w net.ipv4.ping_group_range=\"0 2147483647\"\n",
            strerror(errno));
        return 1;
    }

    struct timeval tv = { timeout_ms / 1000, (timeout_ms % 1000) * 1000 };
    setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv);

    struct sockaddr_in dir;
    memset(&dir, 0, sizeof dir);
    dir.sin_family = AF_INET;
    if (inet_pton(AF_INET, destino, &dir.sin_addr) != 1) {
        fprintf(stderr, "error: --destino debe ser una IPv4 literal (recibi '%s')\n", destino);
        return 2;
    }

    size_t n_paq = ICMP_CAB + payload;
    unsigned char paq[ICMP_CAB + PAYLOAD_MAX];
    unsigned char rx[2048];

    uint32_t id_destino = id_de_ip(destino);

    uint64_t *lat = malloc(iters * sizeof(uint64_t));
    if (!lat) { fprintf(stderr, "sin memoria\n"); return 1; }
    memset(lat, 0, iters * sizeof(uint64_t));

    uint64_t perdidos = 0;
    uint16_t seq = 0;

#define ECO()                                                                        \
    do {                                                                             \
        memset(paq, 0, n_paq);                                                       \
        paq[0] = ICMP_ECHO;  /* tipo 8 */                                            \
        paq[1] = 0;                                                                  \
        uint16_t _s = htons(seq++);                                                  \
        memcpy(paq + 6, &_s, 2);                                                     \
        /* El payload del reto viaja dentro del eco. El kernel lo devuelve TAL CUAL: \
           no lo clasifica, porque no ejecuta nuestro codigo. */                      \
        armar_estimulo(paq + ICMP_CAB, payload, id_destino, (uint32_t)seq);          \
        uint16_t _c = suma_internet(paq, n_paq);                                     \
        memcpy(paq + 2, &_c, 2);                                                     \
        if (sendto(s, paq, n_paq, 0, (struct sockaddr *)&dir, sizeof dir) < 0)       \
            { perdidos++; break; }                                                    \
        ssize_t _k = recv(s, rx, sizeof rx, 0);                                       \
        if (_k < 0) { perdidos++; }                                                   \
    } while (0)

    printf("[cliente E] ICMP echo hacia %s, payload=%zuB (paquete ICMP=%zuB)\n",
           destino, payload, n_paq);
    printf("[cliente E] AVISO: quien responde es el KERNEL, no un proceso nuestro.\n"
           "            Esta variante NO clasifica y NO cumple el enunciado. Es linea base.\n");
    fflush(stdout);

    for (uint64_t i = 0; i < warmup; i++) ECO();
    if (perdidos >= warmup) {
        fprintf(stderr, "[cliente E] error: ninguna respuesta en el warmup. "
                        "Destino inalcanzable o ICMP filtrado.\n");
        return 1;
    }
    perdidos = 0;

    printf("[cliente E] midiendo %llu iteraciones...\n", (unsigned long long)iters);
    fflush(stdout);
    for (uint64_t i = 0; i < iters; i++) {
        uint64_t t0 = ahora_ns();
        ECO();
        uint64_t t1 = ahora_ns();
        lat[i] = t1 - t0;
    }

    if (perdidos)
        fprintf(stderr, "[cliente E] AVISO: %llu de %llu sin respuesta (%.2f%%)\n",
                (unsigned long long)perdidos, (unsigned long long)iters,
                100.0 * (double)perdidos / (double)iters);
    close(s);

    FILE *fh = fopen(salida, "w");
    if (!fh) { perror("fopen"); return 1; }
    fputs("iteracion,latencia_ns\n", fh);
    for (uint64_t i = 0; i < iters; i++)
        fprintf(fh, "%llu,%llu\n", (unsigned long long)(i + 1), (unsigned long long)lat[i]);
    fclose(fh);
    free(lat);
    printf("[cliente E] %llu muestras -> %s\n", (unsigned long long)iters, salida);
    return 0;
}
