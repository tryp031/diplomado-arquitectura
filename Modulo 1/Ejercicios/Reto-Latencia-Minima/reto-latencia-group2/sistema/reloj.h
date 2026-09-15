/*
 * reloj.h — instrumento de medición COMPARTIDO por todas las variantes compiladas.
 *
 * Está aquí y no dentro de una variante por la misma razón que analyze.py está aquí:
 * el atributo AC-3 (comparabilidad) exige que las variantes usen el MISMO instrumento,
 * no uno equivalente. Si cada una define su propio reloj, la diferencia entre dos
 * resultados incluye la diferencia entre dos relojes.
 *
 * ───────────────────────────────────────────────────────────────────────────────
 * DESVIACIÓN DELIBERADA DE ESPEC §2 — ver ADR-003
 *
 * Granularidad real medida en el equipo de referencia (Apple M4, macOS 26.6, arm64):
 *
 *     CLOCK_MONOTONIC        1000 ns   <- lo que ESPEC §2 nombraba primero
 *     CLOCK_MONOTONIC_RAW      41 ns
 *     CLOCK_UPTIME_RAW         41 ns   <- menor sobrecoste, el elegido
 *     contador de hardware   41.67 ns  <- piso físico (timebase 125/3 = 24 MHz)
 *
 * "Resolución de ns" describe las UNIDADES del valor devuelto, no la GRANULARIDAD
 * con la que avanza. CLOCK_MONOTONIC devuelve nanosegundos y salta de microsegundo
 * en microsegundo. Confundir ambas cosas fue el error de la especificación original.
 * ───────────────────────────────────────────────────────────────────────────────
 */
#ifndef LATM_RELOJ_H
#define LATM_RELOJ_H

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static inline uint64_t ahora_ns(void)
{
#if defined(__APPLE__)
    return clock_gettime_nsec_np(CLOCK_UPTIME_RAW);
#else
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ull + (uint64_t)ts.tv_nsec;
#endif
}

/*
 * Pausa dentro de un bucle de espera activa. NO cede el núcleo: ceder significaría
 * volver al planificador. Solo indica a la CPU que está girando.
 */
static inline void pausa_spin(void)
{
#if defined(__aarch64__)
    __asm__ __volatile__("isb sy" ::: "memory");
#elif defined(__x86_64__) || defined(__i386__)
    __builtin_ia32_pause();
#else
    __asm__ __volatile__("" ::: "memory");
#endif
}

static int latm_cmp_u64(const void *a, const void *b)
{
    uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b;
    return (x > y) - (x < y);
}

/*
 * Verifica y reporta la granularidad real del reloj y el sobrecoste de un par de
 * lecturas. ADR-003 lo vuelve OBLIGATORIO para toda variante: sin esto no se sabe
 * si el instrumento alcanza al fenómeno.
 *
 * Devuelve la granularidad en ns (menor delta no nulo entre lecturas consecutivas).
 */
static inline uint64_t reloj_verificar(const char *etiqueta)
{
    enum { N = 100000 };
    uint64_t *d = (uint64_t *)malloc(N * sizeof(uint64_t));
    if (!d) return 0;
    memset(d, 0, N * sizeof(uint64_t));

    for (int i = 0; i < N; i++) {
        uint64_t a = ahora_ns();
        uint64_t b = ahora_ns();
        d[i] = b - a;
    }
    qsort(d, N, sizeof(uint64_t), latm_cmp_u64);

    uint64_t gran = 0;
    for (int i = 0; i < N; i++) if (d[i]) { gran = d[i]; break; }
    int ceros = 0;
    for (int i = 0; i < N; i++) if (!d[i]) ceros++;

    printf("[%s] reloj: granularidad=%llu ns  sobrecoste(par de lecturas) p50=%llu ns "
           "p99=%llu ns  deltas-cero=%.1f%%\n",
           etiqueta, (unsigned long long)gran,
           (unsigned long long)d[N / 2], (unsigned long long)d[(N * 99) / 100],
           100.0 * ceros / N);
    free(d);
    return gran;
}

/* Regla de ADR-003: la granularidad debe ser >=10x menor que el p50 esperado. */
static inline void reloj_avisar_si_grueso(const char *etiqueta, uint64_t gran, uint64_t p50_esperado_ns)
{
    if (gran && p50_esperado_ns && gran * 10 > p50_esperado_ns)
        printf("[%s] AVISO: granularidad %llu ns frente a p50 esperado %llu ns: las muestras\n"
               "        estaran CUANTIZADAS. ADR-003 exige contraste por lotes.\n",
               etiqueta, (unsigned long long)gran, (unsigned long long)p50_esperado_ns);
}

#endif /* LATM_RELOJ_H */
