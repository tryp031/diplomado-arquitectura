# ADR-012 — Se retira el warmup de 100 000 iteraciones de los clientes medidores

- **Estado:** **Propuesta** — decidida por Daniel Mazo el 2026-09-29. **Pendiente de
  ratificación por Freddy y Camilo**, porque cambia el protocolo experimental con el que se
  tomaron las cifras del informe.
- **Fecha:** 2026-09-29
- **Decide:** Daniel Mazo. Ejecuta Daniel Mazo.
- **Supersede parcialmente:** [ESPEC-MEDICION](../ESPEC-MEDICION.md) §2 (fila «Warmup») y la
  mención al warmup en [ADR-001](ADR-001-frontera-de-medicion.md) §Excluye y en
  [ADR-009](ADR-009-plano-de-control-que-muestra.md).
- **No afecta:** la frontera F1 ([ADR-001](ADR-001-frontera-de-medicion.md)) ·
  el reloj ([ADR-003](ADR-003-resolucion-del-reloj.md)) · el dominio de hosts
  ([ADR-004](ADR-004-dominio-listas-de-hosts.md)).

## Contexto

Hasta hoy los dos clientes medidores (`tcp-python/client.py` y
`memoria-compartida-c/client.c`) ejecutaban, antes del bucle medido, 100 000 intercambios
descartados (`--warmup 100000` por defecto). El 28/09 ya se había quitado desde el plano de
control, que pasaba `--warmup 0`; `run.sh` lo conservaba para las mediciones del informe.

## Decisión

Se elimina el warmup por completo: desaparece el parámetro `--warmup` y el bucle de
intercambios descartados en ambos clientes. El plano de control deja de pasarlo.

Motivo declarado por quien decide: ya no es necesario que se ejecute. Este ADR no añade una
justificación técnica que no se haya dado.

## Qué se mantiene

- **La conexión sigue fuera del tramo medido.** En TCP el *handshake* ocurre en
  `conectar()`, antes de la autoprueba y del bucle medido; nunca dependió del warmup.
- **La autoprueba de integridad** (16 hosts + 1 desconocido) sigue corriendo antes de medir.
- **La barrera entre hilos** de `tcp-python` sigue: ahora espera a que todos los hilos estén
  conectados y autoprobados, no a que terminen un warmup.

## Consecuencias

| Consecuencia | Impacto |
|---|---|
| Las primeras muestras de cada corrida incluyen cachés fríos, JIT sin compilar y CPU en baja frecuencia | Sube la cola (p99.9, máximo); el p50 de un millón de muestras debería moverse poco |
| Las corridas nuevas **no son comparables** con las de `resultados/` tomadas con warmup | Igual que ADR-005/006: no se mezclan en una misma tabla |
| Los comandos de reproducción del `INFORME.md` usan `--warmup 100000` | Ahora fallan con «argumento desconocido»: el informe describe cómo se midió entonces y no se reescribe |
| `resultados/` conserva su evidencia | No se borra ni se regenera nada |

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Alguien compara una corrida nueva con una del informe y concluye que la arquitectura empeoró | Media | Alto | Este ADR y la advertencia en `sistema/README.md` |
| Se pregunta en la sustentación por qué el código no hace warmup si el informe sí | Media | Medio | Las cifras del informe se tomaron con el protocolo de ESPEC §2 vigente entonces; este ADR fecha el cambio |

## Cómo revertir

Restaurar el parámetro y el bucle desde el commit anterior a este ADR. Es un cambio local a
los dos clientes y a `app/servidor.py`.
