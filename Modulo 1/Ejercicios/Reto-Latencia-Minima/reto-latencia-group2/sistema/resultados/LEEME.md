# `resultados/` — qué es cada corrida

Esta carpeta es la **evidencia del informe**. Lo que está aquí no se borra ni se
sobrescribe: `run.sh` archiva lo anterior con su fecha antes de escribir (ADR-005).

La nota 11 de la reunión del 21/09 pedía «pulirlo o removerlo». Lo que hacía falta no
era borrar sino **rotular**: saber cuál corrida sostiene el informe y cuál es histórico,
para que nadie cite la equivocada. Eso es este archivo. Los ~143 MB no viajan al ZIP del
código: los excluye `hacer-zip.sh` (ADR-010).

## La corrida oficial — 24/09/2026

**Es la que deben citar el informe, la presentación y las figuras.** Reemplaza a la del
17/09 por decisión del equipo del 24/09 (pedido de Freddy de refrescar las pruebas). El
método no cambió: mismo código del plano de datos, mismos parámetros
(`--warmup 100000 --iters 1000000`), misma máquina.

| Archivo | Tomada | Iteraciones |
|---|---|---|
| `resultados-tcp-python-1/2/3.csv` + `.log` | 2026-09-24 15:00 | 1 000 000 × 3 |
| `resultados-memoria-compartida-c-1/2/3.csv` + `.log` | 2026-09-24 15:01 | 1 000 000 × 3 |

Equipo de referencia, declarado en cada `.log`:
`Darwin 25.6.0 · arm64 · Apple M4 · Mac-mini.local`.
Carga de la máquina al empezar: 5,76 (1 min) sobre 10 núcleos; al del 17/09 no se le
registró la carga.

Cifras que salen de aquí (3 rondas agregadas):

| | p50 | p99.9 | máx | > 1 ms |
|---|---|---|---|---|
| TCP Python | 14 875 ns | 105 750 ns | 15 762 417 ns | 164 / 3 M |
| Memoria compartida C | **83 ns** | 209 ns | 41 792 ns | **0** / 3 M |

Se regeneran con `./analyze.py --md resultados/resultados-*-[123].csv`.

## Las corridas anteriores — se conservan y se citan como comparación

La tesis del informe (§7.1) es que el veredicto de TCP Python **cambia entre corridas con
el mismo código**. Por eso las anteriores no se borran: son la evidencia de esa variación.

| Corrida | TCP Python > 1 ms | Memoria compartida C > 1 ms | Dónde |
|---|---|---|---|
| 14/09 | **0** / 3 M | 0 / 3 M | `archivo/*--20260914-*` |
| 17/09 | **136** / 3 M | 0 / 3 M | `archivo/*--20260917-*` |
| 24/09 | **164** / 3 M | 0 / 3 M | `resultados/` — oficial |

## Lo que NO se cita

| Archivo | Qué es |
|---|---|
| `*-0.csv` / `.log` (08/09) | validación del harness, antes de fijar el método |
| `*-9.csv` / `.log` (14/09) | prueba rápida de 20 000 iteraciones |

**Convención de rondas:** 1-3 son las del informe · 0 es validación · 9 es prueba rápida.
`graficas.py` y `analyze.py` sólo agregan 1-3. Hasta el 17/09 la 9 se colaba en las
figuras y decían `n=3 020 000` mientras la tabla decía 3 000 000: no fallaba, mentía.

## Por qué los `.csv` no están en git y los `.log` sí

Los CSV pesan ~143 MB y el `.gitignore` los excluye. **Los `.log` sí se versionan**: son
lo único que dice en qué máquina se tomó cada corrida, y sin eso las cifras no son
verificables ni comparables (ADR-005).

Consecuencia práctica: **quien clone el repositorio tiene los logs pero no los CSV**, así
que `graficas.py` y `analyze.py` no reproducen las figuras sin volver a medir — y volver a
medir daría otros números, porque el cumplimiento depende del estado del sistema
operativo. Las figuras de `docs/graficas/` son **evidencia congelada**: se incrustan sin
modificar.

## Regla que el equipo adoptó el 21/09

> Ninguna cifra entra a un documento si su log no está versionado.

Es exactamente lo que falló el 17/09: el informe citaba una corrida del 10/09 que nunca
estuvo en el árbol. Hubo que volver a medir todo.
