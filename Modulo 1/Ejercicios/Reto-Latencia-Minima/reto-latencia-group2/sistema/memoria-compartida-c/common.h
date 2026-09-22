/*
 * Variante Memoria compartida C — memoria compartida + busy-spin.  Definiciones comunes.
 *
 * Decisiones que se materializan en este archivo (ver ADR-002):
 *
 *  - Una ranura por sentido, cada una ALINEADA A 128 BYTES y de exactamente ese tamaño.
 *    128 B es el tamaño de línea de caché en Apple Silicon. Si petición y respuesta
 *    compartieran línea, cada escritura de un proceso invalidaría la caché del otro
 *    (false sharing) y la latencia se multiplicaría. Esto NO es microoptimización:
 *    es la diferencia entre ~100 ns y ~1 µs.
 *
 *  - La bandera de secuencia vive en la MISMA línea que su payload. Así el dato viaja
 *    entre núcleos en una sola transferencia de línea de caché, no en dos.
 *
 *  - Sincronización con _Atomic + acquire/release, nunca con `volatile`.
 *    arm64 tiene modelo de memoria DÉBILMENTE ORDENADO: sin barreras, el otro núcleo
 *    puede ver la bandera actualizada ANTES que el payload. El código funcionaría en
 *    x86 (que es fuertemente ordenado) y estaría roto aquí. `volatile` no impone
 *    ninguna barrera: es una garantía sobre el compilador, no sobre la CPU.
 *
 *  - Sin ring buffer. Con una sola petición en vuelo (ESPEC §2) un anillo añade
 *    índices, aritmética modular y razonamiento sobre envoltura sin reducir latencia.
 *    Sería sobreingeniería, y el módulo la penaliza.
 */
#ifndef LATM_COMMON_H
#define LATM_COMMON_H

#include <stdatomic.h>
#include <stdint.h>
#include <stddef.h>

/* El reloj y la pausa de spin son del HARNESS, no de esta variante: mismo instrumento
   para todas (AC-3). Incluye la desviacion de ESPEC §2 justificada en ADR-003. */
#include "../reloj.h"

#define LINEA_CACHE 128
#define PAYLOAD_MAX (LINEA_CACHE - sizeof(uint64_t))  /* 120 B */

/* Una ranura = bandera de secuencia + payload, en una única línea de caché. */
typedef struct {
    _Alignas(LINEA_CACHE) _Atomic uint64_t seq;
    unsigned char dato[LINEA_CACHE - sizeof(uint64_t)];
} ranura_t;

_Static_assert(sizeof(ranura_t) == LINEA_CACHE,
               "ranura_t debe ocupar exactamente una linea de cache");

/* La región compartida: un sentido por ranura, en líneas distintas. */
typedef struct {
    ranura_t peticion;    /* cliente escribe, servidor lee */
    ranura_t respuesta;   /* servidor escribe, cliente lee */
} region_t;

_Static_assert(sizeof(region_t) == 2 * LINEA_CACHE, "region_t inesperada");

/* Nombre del objeto de memoria compartida, derivado del puerto (contrato del harness:
   D=9103). Permite correr varias variantes o rondas en paralelo sin colisión. */
#define NOMBRE_SHM_FMT "/latm-D-%d"

/* Límite de giro antes de rendirse: evita que un fallo del otro proceso cuelgue la
   corrida para siempre. ~segundos en la práctica. */
#define LIMITE_SPIN 5000000000ull

#endif /* LATM_COMMON_H */
