/*
 * clasificador.h — EL DOMINIO del reto, compartido por todas las variantes compiladas.
 *
 * Que hace el sistema (decision registrada en ADR-004):
 *   Estimulo  = un identificador de host (direccion IPv4, 4 bytes) + numero de secuencia.
 *   Respuesta = un veredicto: LOCAL / EXTERNO / DESCONOCIDO.
 *
 * Esto sustituye al eco puro. NO cambia el transporte, NO cambia la frontera de
 * medicion F1 (ADR-001), NO cambia el tamano del payload: siguen siendo 32 bytes
 * en ambos sentidos. Solo cambia que significan esos bytes.
 *
 * ───────────────────────────────────────────────────────────────────────────────
 * LAS TRES PROPIEDADES QUE HACEN DEFENDIBLE ESTE DOMINIO
 *
 *  1. CABE EN UNA LINEA DE CACHE.  16 entradas x 4 B = 64 B exactos.
 *     La objecion clasica contra clasificar dentro de la ruta caliente es que una
 *     busqueda en tabla no es O(1) constante: los fallos de cache meten varianza en
 *     los percentiles altos y contaminan la comparacion de transportes. Con 64 bytes
 *     la tabla vive en L1 permanentemente y esa objecion desaparece por construccion.
 *
 *  2. ES DE TIEMPO CONSTANTE.  Sin salida anticipada, sin ramas dependientes del dato.
 *     El bucle recorre SIEMPRE las 16 ranuras y acumula el resultado con una seleccion
 *     condicional (csel en arm64, cmov en x86), no con un salto. Por tanto clasificar
 *     LOCAL, EXTERNO o DESCONOCIDO cuesta exactamente lo mismo.
 *
 *     Esto no lo pide el enunciado. Se hace porque sin ello la latencia dependeria del
 *     dato, y entonces: (a) la comparacion entre variantes quedaria sesgada por la
 *     mezcla de veredictos de cada corrida, y (b) en un sistema real de autorizacion
 *     seria un canal lateral temporal. La primera razon es metodologica y la segunda
 *     es de seguridad; ambas apuntan a la misma decision.
 *
 *  3. NO ASIGNA MEMORIA, NO HACE LLAMADAS AL SISTEMA, NO HACE E/S.
 *     El CSV se parsea una sola vez al arrancar. La ruta caliente solo lee memoria.
 *
 * ───────────────────────────────────────────────────────────────────────────────
 * TRAMPA VERIFICADA — NO convertir la tabla en constantes del codigo
 *
 * La tabla se carga de un ARCHIVO en tiempo de ejecucion. Eso no es comodidad: es
 * lo que impide que el compilador conozca su contenido.
 *
 * Comprobado con `cc -O2 -S` en Apple Silicon:
 *   - Tabla cargada del CSV  -> emite 16 `csel` consecutivos, 0 saltos condicionales.
 *                               El barrido existe y es de tiempo constante. CORRECTO.
 *   - Tabla conocida en compilacion -> el optimizador PLIEGA EL BUCLE ENTERO y lo
 *                               reduce a `cmp w0,#0 ; csel`. El clasificador
 *                               DESAPARECE del binario.
 *
 * Consecuencia: si alguien "simplifica" esto poniendo las IPs como literales en el
 * codigo, la corrida de control que mide el coste del clasificador medira CERO — y
 * la conclusion "clasificar es despreciable" seria un artefacto del optimizador, no
 * un resultado. El experimento se invalidaria en silencio.
 *
 * Esto es un ejemplo, medible, de que la frontera del sistema medido no la fija solo
 * el codigo fuente: la fija el codigo DESPUES del compilador.
 * ───────────────────────────────────────────────────────────────────────────────
 *
 * Coste esperado: 16 comparaciones + 16 selecciones sobre una linea de cache caliente.
 * Del orden de 1-3 ns en Apple Silicon. El informe lo MIDE (corrida con y sin tabla),
 * no lo afirma: ver ADR-004 §5.
 * ───────────────────────────────────────────────────────────────────────────────
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

/* Ranura libre: 0xFFFFFFFF es 255.255.255.255 (broadcast limitado), que nunca puede
   ser un host consultado. Asi las ranuras vacias participan del barrido sin acertar
   jamas, y el coste no depende de cuantas entradas reales haya. */
#define RANURA_LIBRE 0xFFFFFFFFu

/* 16 x 4 B = 64 B alineados: UNA linea de cache, nunca falla. */
static _Alignas(64) uint32_t g_tabla_id[TABLA_MAX];
static _Alignas(16) uint8_t  g_tabla_ver[TABLA_MAX];
static int g_tabla_n = 0;

/*
 * RUTA CALIENTE. Tiempo constante: 16 iteraciones siempre, sin salida anticipada.
 * `id` llega en orden de red, igual que lo produce inet_pton, y la tabla se guarda
 * en ese mismo orden: cero conversiones de endianness aqui.
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
                            "              no un detalle: subirlo invalida ADR-004.\n", TABLA_MAX);
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
 * transporte en las variantes rapidas. Mismo tamano en ambos sentidos que el eco
 * puro anterior, asi que las mediciones previas siguen siendo comparables en forma.
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
