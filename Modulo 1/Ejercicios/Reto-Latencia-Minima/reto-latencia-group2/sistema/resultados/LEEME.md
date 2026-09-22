# `resultados/` — qué es cada corrida

Esta carpeta es la **evidencia del informe**. Lo que está aquí no se borra ni se
sobrescribe: `run.sh` archiva lo anterior con su fecha antes de escribir (ADR-005).

La nota 11 de la reunión del 21/09 pedía «pulirlo o removerlo». Lo que hacía falta no
era borrar sino **rotular**: saber cuál corrida sostiene el informe y cuál es histórico,
para que nadie cite la equivocada. Eso es este archivo. Los ~143 MB no viajan al ZIP del
código: los excluye `hacer-zip.sh` (ADR-010).

## La corrida oficial — 17/09/2026

**Es la única que se cita en el informe, la presentación y las figuras.**

| Archivo | Tomada | Iteraciones |
|---|---|---|
| `resultados-tcp-python-1/2/3.csv` + `.log` | 2026-09-17 11:01 | 1 000 000 × 3 |
| `resultados-memoria-compartida-c-1/2/3.csv` + `.log` | 2026-09-17 11:02 | 1 000 000 × 3 |

Equipo de referencia, declarado en cada `.log`:
`Darwin 25.6.0 · arm64 · Apple M4 · Mac-mini.local`.

Cifras que salen de aquí:

| | p50 | p99.9 | máx | > 1 ms |
|---|---|---|---|---|
| TCP Python | 13 458 ns | 116 209 ns | 13 649 750 ns | 136 / 3 M |
| Memoria compartida C | **83 ns** | 167 ns | 37 125 ns | **0** / 3 M |

Se regeneran con `./analyze.py --md resultados/resultados-*.csv`.

## Lo que NO es la corrida oficial

| Archivo | Qué es | ¿Se cita? |
|---|---|---|
| `*-0.csv` / `.log` (08/09) | validación del harness, antes de fijar el método | **no** |
| `*-9.csv` / `.log` (14/09) | prueba rápida de 20 000 iteraciones | **no** |
| `archivo/` — 12 archivos (14/09) | corrida anterior, archivada automáticamente por `run.sh` | **no** |

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
