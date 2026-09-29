/*
 * clasificador.h — EL DOMINIO del reto, compartido por todas las variantes compiladas.
 *   Estimulo  = identificador de host (IPv4, 4 bytes) + numero de secuencia.
 *   Respuesta = veredicto LOCAL / EXTERNO / DESCONOCIDO. 32 bytes en ambos sentidos.
 *
 * Invariantes de la ruta caliente:
 *  1. La tabla cabe en UNA linea de cache (16 x 4 B = 64 B): vive en L1, sin fallos
 *     de cache que metan varianza en los percentiles altos.
 *  2. Tiempo constante: recorre SIEMPRE las 16 ranuras con seleccion condicional
 *     (csel/cmov), sin salida anticipada. LOCAL, EXTERNO y DESCONOCIDO cuestan lo
 *     mismo; si no, la latencia dependeria del dato (sesgo y canal lateral temporal).
 *  3. Sin asignar memoria, sin llamadas al sistema, sin E/S: el CSV se lee una vez.
 *
 * NO convertir la tabla en constantes del codigo: con la tabla conocida en compilacion
 * el optimizador pliega el bucle y el clasificador desaparece del binario (comprobado
 * con `cc -O2 -S`). Cargarla del CSV en tiempo de ejecucion es lo que lo impide.
 */
#ifndef LATM_CLASIFICADOR_H
#define LATM_CLASIFICADOR_H

#include <arpa/inet.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TABLA_MAX 16

#define VEREDICTO_EXTERNO     0u
#define VEREDICTO_LOCAL       1u
#define VEREDICTO_DESCONOCIDO 2u

/* Ranura libre: 255.255.255.255 (broadcast) nunca es un host consultado. Las ranuras
   vacias participan del barrido sin acertar, y el coste no depende de cuantas haya. */
#define RANURA_LIBRE 0xFFFFFFFFu

/* 16 x 4 B = 64 B alineados: UNA linea de cache, nunca falla. */
static _Alignas(64) uint32_t g_tabla_id[TABLA_MAX];
static _Alignas(16) uint8_t  g_tabla_ver[TABLA_MAX];
static int g_tabla_n = 0;

/*
 * RUTA CALIENTE. Tiempo constante: 16 iteraciones siempre, sin salida anticipada.
 * `id` y la tabla estan en orden de red (como inet_pton): sin conversiones aqui.
 */
static inline uint8_t clasificar(uint32_t id)
{
    uint8_t v = (uint8_t)VEREDICTO_DESCONOCIDO;
    for (int i = 0; i < TABLA_MAX; i++) {
        /* Seleccion condicional, no salto: el compilador emite csel/cmov. */
        v = (g_tabla_id[i] == id) ? g_tabla_ver[i] : v;
    }
    return v;
}

/* ─── Todo lo que sigue corre UNA VEZ al arrancar. Nunca en la ruta caliente. ─── */

static inline int clasificador_cargar(const char *ruta)
{
    for (int i = 0; i < TABLA_MAX; i++) {
        g_tabla_id[i]  = RANURA_LIBRE;
        g_tabla_ver[i] = (uint8_t)VEREDICTO_DESCONOCIDO;
    }
    g_tabla_n = 0;

    FILE *fh = fopen(ruta, "r");
    if (!fh) {
        fprintf(stderr, "clasificador: no se pudo abrir la tabla '%s': %s\n",
                ruta, strerror(errno));
        return -1;
    }

    char linea[256];
    while (fgets(linea, sizeof linea, fh)) {
        if (linea[0] == '#' || linea[0] == '\n' || linea[0] == '\r') continue;

        char nombre[64], ip[64], ver[32];
        if (sscanf(linea, "%63[^,],%63[^,],%31[^\r\n]", nombre, ip, ver) != 3) continue;
        if (!strcmp(nombre, "nombre")) continue;   /* cabecera */

        if (g_tabla_n >= TABLA_MAX) {
            fprintf(stderr, "clasificador: la tabla excede %d filas. El limite es una\n"
                            "              DECISION de diseno (64 B = 1 linea de cache),\n"
                            "              no un detalle: subirlo invalida la comparacion.\n", TABLA_MAX);
            fclose(fh);
            return -1;
        }

        struct in_addr a;
        if (inet_pton(AF_INET, ip, &a) != 1) {
            fprintf(stderr, "clasificador: IP invalida en la tabla: '%s' (host %s)\n", ip, nombre);
            fclose(fh);
            return -1;
        }

        uint8_t v;
        if      (!strcmp(ver, "local"))   v = (uint8_t)VEREDICTO_LOCAL;
        else if (!strcmp(ver, "externo")) v = (uint8_t)VEREDICTO_EXTERNO;
        else {
            fprintf(stderr, "clasificador: veredicto invalido '%s' (host %s)\n", ver, nombre);
            fclose(fh);
            return -1;
        }

        g_tabla_id[g_tabla_n]  = (uint32_t)a.s_addr;   /* orden de red, sin convertir */
        g_tabla_ver[g_tabla_n] = v;
        g_tabla_n++;
    }
    fclose(fh);

    if (g_tabla_n == 0) {
        fprintf(stderr, "clasificador: la tabla '%s' no tiene ninguna entrada valida\n", ruta);
        return -1;
    }
    return g_tabla_n;
}

static inline uint32_t id_de_ip(const char *ip)
{
    struct in_addr a;
    if (inet_pton(AF_INET, ip, &a) != 1) return RANURA_LIBRE;
    return (uint32_t)a.s_addr;
}

static inline const char *nombre_veredicto(uint8_t v)
{
    switch (v) {
        case VEREDICTO_LOCAL:   return "LOCAL";
        case VEREDICTO_EXTERNO: return "EXTERNO";
        default:                return "DESCONOCIDO";
    }
}

static inline void clasificador_resumen(const char *etiqueta, const char *ruta)
{
    int loc = 0, ext = 0;
    for (int i = 0; i < g_tabla_n; i++)
        (g_tabla_ver[i] == VEREDICTO_LOCAL) ? loc++ : ext++;
    printf("[%s] tabla '%s': %d hosts (%d locales, %d externos), %zu B = %.0f linea(s) de cache\n",
           etiqueta, ruta, g_tabla_n, loc, ext,
           TABLA_MAX * sizeof(uint32_t), (double)(TABLA_MAX * sizeof(uint32_t)) / 64.0);
    fflush(stdout);
}

/* ───────────────────────── Formato de cable — 32 B fijos ─────────────────────────
 *
 *   ESTIMULO                                RESPUESTA
 *   0..3   host_id  (uint32, orden de red)  0      veredicto (uint8)
 *   4..7   seq      (uint32)                1..3   relleno
 *   8..31  relleno                          4..7   host_id (eco, para verificar)
 *                                           8..31  relleno
 *
 * Binario de tamano fijo, no texto: serializar y parsear costaria mas que el
 * transporte en las variantes rapidas.
 */
#define OFF_HOST_ID   0
#define OFF_SEQ       4
#define OFF_VEREDICTO 0
#define OFF_ECO_ID    4

static inline void armar_estimulo(unsigned char *b, size_t n, uint32_t host_id, uint32_t seq)
{
    memset(b, 0, n);
    memcpy(b + OFF_HOST_ID, &host_id, sizeof host_id);
    memcpy(b + OFF_SEQ,     &seq,     sizeof seq);
}

#endif /* LATM_CLASIFICADOR_H */
