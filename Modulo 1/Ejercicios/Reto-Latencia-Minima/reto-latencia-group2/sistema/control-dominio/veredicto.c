/* ¿Cuesta lo mismo decir LOCAL que decir EXTERNO?
 *
 * clasificador.h AFIRMA ser de tiempo constante: recorre siempre las 16 ranuras con
 * seleccion condicional, sin salida anticipada. Este programa lo MIDE, que es otra
 * cosa. La distincion es la misma que ya obligo a escribir micro.c: afirmar que el
 * clasificador es despreciable sin medirlo habria sido metodo, no resultado.
 *
 * POR QUE IMPORTA — dos razones independientes que apuntan a la misma propiedad:
 *
 *   1. Metodologica. Si el veredicto cambiara el coste, la latencia dependeria del
 *      dato: dos corridas con distinta mezcla de IPs darian numeros distintos y la
 *      comparacion entre transportes quedaria contaminada por que se pregunto.
 *
 *   2. Seguridad. Seria un canal lateral temporal: midiendo el tiempo de respuesta
 *      se podria deducir si un host esta en la lista negra, sin que el sistema lo
 *      diga. En un control de acceso real eso es una fuga.
 *
 * POR QUE AISLADO Y NO POR RTT: el efecto buscado es de ~2 ns y el RTT de la variante
 * mas rapida es 83 ns, el de B 13 400 ns. Medirlo por RTT es el error que este mismo
 * directorio ya documento: la varianza entre rondas se traga la senal y se reporta
 * ruido como resultado.
 *
 *   ./veredicto ../tabla-hosts.csv
 */
#include "clasificador.h"
#include "reloj.h"

#define N_LOTE   100000
#define N_RONDAS 500

static int cmp(const void *a, const void *b){
    uint64_t x=*(const uint64_t*)a, y=*(const uint64_t*)b; return (x>y)-(x<y);
}

/* Mide el coste por llamada de clasificar() sobre un ciclo dado de 16 entradas.
   Devuelve picosegundos; escribe tambien el p99 para poder hablar de dispersion. */
static uint64_t medir(const uint32_t *ciclo, uint64_t *m, uint64_t *p99_out)
{
    volatile uint64_t sumidero = 0;
    for (int k = 0; k < N_RONDAS; k++) {
        uint64_t acc = 0, t0 = ahora_ns();
        for (int j = 0; j < N_LOTE; j++) acc += clasificar(ciclo[j & 15]);
        uint64_t t1 = ahora_ns();
        sumidero += acc;
        m[k] = (t1 - t0) * 1000 / N_LOTE;
    }
    (void)sumidero;
    qsort(m, N_RONDAS, sizeof(uint64_t), cmp);
    *p99_out = m[(int)(N_RONDAS * 0.99)];
    return m[N_RONDAS / 2];
}

int main(int argc, char **argv)
{
    if (clasificador_cargar(argc > 1 ? argv[1] : "../tabla-hosts.csv") < 0) return 1;

    /* Tres ciclos de 16 entradas cada uno. El TAMANO es el mismo en los tres para que
       la unica diferencia sea el veredicto que producen, no cuanta memoria se recorre. */
    uint32_t solo_local[16], solo_externo[16], solo_desconocido[16];
    int nl = 0, ne = 0;
    uint32_t locales[TABLA_MAX], externos[TABLA_MAX];

    for (int i = 0; i < g_tabla_n; i++) {
        if (g_tabla_ver[i] == VEREDICTO_LOCAL)   locales[nl++]  = g_tabla_id[i];
        if (g_tabla_ver[i] == VEREDICTO_EXTERNO) externos[ne++] = g_tabla_id[i];
    }
    if (nl == 0 || ne == 0) {
        fprintf(stderr, "la tabla necesita al menos un host local y uno externo\n");
        return 1;
    }
    for (int i = 0; i < 16; i++) {
        solo_local[i]   = locales[i % nl];
        solo_externo[i] = externos[i % ne];
        /* 203.0.113.0/24 es RFC 5737 TEST-NET-3 y no esta en la tabla: DESCONOCIDO
           garantizado sin tocar el dominio. */
        char ip[16]; snprintf(ip, sizeof ip, "203.0.113.%d", i + 1);
        solo_desconocido[i] = id_de_ip(ip);
    }

    uint64_t *m = malloc(N_RONDAS * sizeof(uint64_t));
    uint64_t p99_l, p99_e, p99_d;
    /* Una ronda en vacio antes de medir: la primera toca frio la cache de los ciclos. */
    medir(solo_local, m, &p99_l);

    uint64_t loc = medir(solo_local,       m, &p99_l);
    uint64_t ext = medir(solo_externo,     m, &p99_e);
    uint64_t des = medir(solo_desconocido, m, &p99_d);
    free(m);

    uint64_t max = loc > ext ? loc : ext; if (des > max) max = des;
    uint64_t min = loc < ext ? loc : ext; if (des < min) min = des;
    double dispersion = (max - min) / 1000.0;

    printf("\n  Coste de clasificar() segun el veredicto que produce\n");
    printf("  tabla: %d hosts (%d locales, %d externos) · %d rondas x %d iteraciones\n\n",
           g_tabla_n, nl, ne, N_RONDAS, N_LOTE);
    printf("    veredicto        p50 (ns)   p99 (ns)\n");
    printf("    LOCAL            %8.3f   %8.3f\n", loc / 1000.0, p99_l / 1000.0);
    printf("    EXTERNO          %8.3f   %8.3f\n", ext / 1000.0, p99_e / 1000.0);
    printf("    DESCONOCIDO      %8.3f   %8.3f\n", des / 1000.0, p99_d / 1000.0);
    printf("\n    diferencia maxima entre veredictos: %.3f ns\n", dispersion);

    /* El criterio NO es un umbral elegido a dedo —eso seria decidir el resultado
       antes de medirlo—. Es una comparacion entre dos dispersiones:
     *
     *   entre veredictos : cuanto se separan los tres p50 entre si
     *   dentro de uno    : cuanto se mueve UN mismo veredicto entre rondas (p99 - p50)
     *
     * Si la primera es menor que la segunda, la diferencia atribuida al veredicto es
     * mas pequena que el ruido que el mismo veredicto produce al repetirse: no se
     * puede afirmar que exista. Es el mismo razonamiento que invalido el primer
     * intento de micro.c, donde 7 ns de "senal" resultaron ser varianza entre rondas. */
    double ruido_l = (p99_l - loc) / 1000.0;
    double ruido_e = (p99_e - ext) / 1000.0;
    double ruido_d = (p99_d - des) / 1000.0;
    double ruido = ruido_l > ruido_e ? ruido_l : ruido_e;
    if (ruido_d > ruido) ruido = ruido_d;

    printf("    dispersion dentro de un mismo veredicto (p99-p50): %.3f ns\n\n", ruido);

    if (dispersion < ruido)
        printf("    -> INDISTINGUIBLES: los veredictos se separan menos entre si (%.3f ns)\n"
               "       que lo que uno solo varia al repetirlo (%.3f ns). El tiempo no\n"
               "       revela el veredicto: no hay canal lateral temporal, y la latencia\n"
               "       no depende de que IP se pregunte.\n\n", dispersion, ruido);
    else
        printf("    -> HAY DIFERENCIA: los veredictos se separan (%.3f ns) mas que el\n"
               "       ruido de repetir uno solo (%.3f ns). El tiempo revela el veredicto:\n"
               "       canal lateral temporal, y la mezcla de IPs de cada corrida sesga la\n"
               "       medicion. Revisar si clasificar() adquirio una salida anticipada.\n\n",
               dispersion, ruido);
    return 0;
}
