/*
 * CONTROL Bc — servidor de eco sobre TCP crudo, en C.
 *
 * NO es una quinta variante del estudio: es un EXPERIMENTO DE CONTROL.
 *
 * Problema que resuelve: la comparación B (TCP/Python) vs D (shm/C) mezcla dos
 * variables —transporte y lenguaje— y por tanto no permite atribuir el factor 161x
 * a ninguna de las dos. Este binario mantiene el transporte de B y cambia solo el
 * lenguaje, así que la diferencia B vs Bc aísla el efecto del lenguaje y la
 * diferencia Bc vs D aísla el efecto del transporte.
 *
 * Traducción literal de variante-B-tcp/server.py. Mismas decisiones:
 * TCP_NODELAY, conexión persistente, buffer preasignado.
 *
 * Dominio (ADR-004): recibe 32 B con un identificador de host y responde 32 B con un
 * veredicto LOCAL/EXTERNO/DESCONOCIDO. La clasificación es de tiempo constante y la
 * tabla cabe en una línea de caché: ver ../clasificador.h.
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

#include "../clasificador.h"

#ifdef __APPLE__
#include <pthread.h>
#endif

#define PAYLOAD_MAX 4096

int main(int argc, char **argv)
{
    const char *host = "127.0.0.1";
    int port = 9111;
    size_t payload = 32;
    const char *ruta_tabla = "tabla-hosts.csv";

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--host") && i + 1 < argc)          host = argv[++i];
        else if (!strcmp(argv[i], "--port") && i + 1 < argc)     port = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--payload") && i + 1 < argc)  payload = (size_t)atol(argv[++i]);
        else if (!strcmp(argv[i], "--tabla") && i + 1 < argc)    ruta_tabla = argv[++i];
        else { fprintf(stderr, "argumento desconocido: %s\n", argv[i]); return 2; }
    }
    if (payload == 0 || payload > PAYLOAD_MAX) { fprintf(stderr, "--payload fuera de rango\n"); return 2; }
    if (payload < 8) { fprintf(stderr, "--payload debe ser >= 8 (host_id + seq)\n"); return 2; }

    /* FUERA de la ruta caliente: una sola vez, al arrancar. */
    if (clasificador_cargar(ruta_tabla) < 0) return 1;
    clasificador_resumen("servidor Bc", ruta_tabla);

    signal(SIGPIPE, SIG_IGN);
#ifdef __APPLE__
    pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
#endif

    int srv = socket(AF_INET, SOCK_STREAM, 0);
    if (srv < 0) { perror("socket"); return 1; }
    int uno = 1;
    setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &uno, sizeof uno);

    struct sockaddr_in dir;
    memset(&dir, 0, sizeof dir);
    dir.sin_family = AF_INET;
    dir.sin_port = htons((uint16_t)port);
    if (inet_pton(AF_INET, host, &dir.sin_addr) != 1) { fprintf(stderr, "host invalido\n"); return 2; }
    if (bind(srv, (struct sockaddr *)&dir, sizeof dir) != 0) { perror("bind"); return 1; }
    if (listen(srv, 1) != 0) { perror("listen"); return 1; }

    printf("[servidor Bc] escuchando en %s:%d, payload=%zuB (control: TCP en C)\n",
           host, port, payload);
    fflush(stdout);

    unsigned char respuesta[PAYLOAD_MAX];
    memset(respuesta, 0, payload);
    unsigned char buf[PAYLOAD_MAX];

    for (;;) {
        int c = accept(srv, NULL, NULL);
        if (c < 0) { if (errno == EINTR) continue; perror("accept"); break; }
        setsockopt(c, IPPROTO_TCP, TCP_NODELAY, &uno, sizeof uno);
        printf("[servidor Bc] conexion aceptada\n"); fflush(stdout);

        for (;;) {
            /* TCP es un flujo: hay que leer el estimulo completo, igual que en Python. */
            size_t leidos = 0;
            int roto = 0;
            while (leidos < payload) {
                ssize_t k = recv(c, buf + leidos, payload - leidos, 0);
                if (k <= 0) { roto = 1; break; }
                leidos += (size_t)k;
            }
            if (roto) break;

            /* ---- EL DOMINIO: tiempo constante, sin E/S, sin asignar ---- */
            uint32_t host_id;
            memcpy(&host_id, buf + OFF_HOST_ID, sizeof host_id);
            respuesta[OFF_VEREDICTO] = clasificar(host_id);
            memcpy(respuesta + OFF_ECO_ID, &host_id, sizeof host_id);

            size_t enviados = 0;
            while (enviados < payload) {
                ssize_t k = send(c, respuesta + enviados, payload - enviados, 0);
                if (k <= 0) { roto = 1; break; }
                enviados += (size_t)k;
            }
            if (roto) break;
        }
        close(c);
        printf("[servidor Bc] conexion cerrada\n"); fflush(stdout);
    }
    close(srv);
    return 0;
}
