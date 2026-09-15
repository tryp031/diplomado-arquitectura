/* Microbenchmark AISLADO de clasificar(): sin sockets, sin shm, sin planificador.
   Tecnica de lotes (ADR-003): un par de llamadas al reloj por cada N iteraciones. */
#include "clasificador.h"
#include "reloj.h"

#define N_LOTE   100000
#define N_RONDAS 500

static int cmp(const void *a, const void *b){
    uint64_t x=*(const uint64_t*)a, y=*(const uint64_t*)b; return (x>y)-(x<y);
}

int main(int argc, char **argv){
    if (clasificador_cargar(argc>1?argv[1]:"tabla-hosts.csv") < 0) return 1;

    uint32_t ciclo[16];
    for (int i=0;i<16;i++) ciclo[i]=g_tabla_id[i];

    volatile uint64_t sumidero = 0;   /* impide que el optimizador borre el bucle */
    uint64_t *m = malloc(N_RONDAS*sizeof(uint64_t));

    /* Referencia: el MISMO bucle sin clasificar. La diferencia es el clasificador. */
    for (int k=0;k<N_RONDAS;k++){
        uint64_t acc=0, t0=ahora_ns();
        for (int j=0;j<N_LOTE;j++) acc += ciclo[j & 15];
        uint64_t t1=ahora_ns(); sumidero += acc;
        m[k] = (t1-t0)*1000/N_LOTE;            /* picosegundos */
    }
    qsort(m,N_RONDAS,sizeof(uint64_t),cmp);
    uint64_t base = m[N_RONDAS/2];

    for (int k=0;k<N_RONDAS;k++){
        uint64_t acc=0, t0=ahora_ns();
        for (int j=0;j<N_LOTE;j++) acc += clasificar(ciclo[j & 15]);
        uint64_t t1=ahora_ns(); sumidero += acc;
        m[k] = (t1-t0)*1000/N_LOTE;
    }
    qsort(m,N_RONDAS,sizeof(uint64_t),cmp);
    uint64_t con = m[N_RONDAS/2];

    printf("  bucle de referencia (sin clasificar) : %6.3f ns/llamada\n", base/1000.0);
    printf("  bucle con clasificar()               : %6.3f ns/llamada\n", con/1000.0);
    printf("  COSTE DEL CLASIFICADOR               : %6.3f ns  (p50 de %d rondas x %d)\n",
           (con-base)/1000.0, N_RONDAS, N_LOTE);
    printf("  (sumidero=%llu, solo para que el optimizador no borre el bucle)\n",
           (unsigned long long)sumidero);
    return 0;
}
