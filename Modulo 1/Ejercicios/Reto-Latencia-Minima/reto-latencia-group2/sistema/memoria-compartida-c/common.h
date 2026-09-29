/*
 * Variante Memoria compartida C — memoria compartida + busy-spin.  Definiciones comunes.
 *
 *  - Una ranura por sentido, alineada a 128 B (línea de caché en Apple Silicon). Si
 *    petición y respuesta compartieran línea habría false sharing (~100 ns -> ~1 µs).
 *  - La bandera de secuencia vive en la MISMA línea que su payload: una sola
 *    transferencia de línea entre núcleos, no dos.
 *  - _Atomic + acquire/release, nunca `volatile`: arm64 es débilmente ordenado y sin
 *    barreras el otro núcleo puede ver la bandera antes que el payload.
 *  - Sin ring buffer: con una sola petición en vuelo no reduciría latencia.
 */
#ifndef LATM_COMMON_H
#define LATM_COMMON_H

#include <stdatomic.h>
#include <stdint.h>
#include <stddef.h>

/* Reloj y pausa de spin compartidos: mismo instrumento para todas las variantes. */
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

/* Nombre del objeto de memoria compartida, derivado del puerto (9103): permite
   correr varias rondas en paralelo sin colisión. */
#define NOMBRE_SHM_FMT "/latm-D-%d"

/* Límite de giro antes de rendirse: evita que un fallo del otro proceso cuelgue la
   corrida para siempre. ~segundos en la práctica. */
#define LIMITE_SPIN 5000000000ull

#endif /* LATM_COMMON_H */
