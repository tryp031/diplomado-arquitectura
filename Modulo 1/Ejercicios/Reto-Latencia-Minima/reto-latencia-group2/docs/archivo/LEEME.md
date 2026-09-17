# Archivo — lo que se retiró del camino, y por qué sigue aquí

Nada de esta carpeta está vigente. Está aquí por **trazabilidad**: son documentos que
sostuvieron decisiones reales, y borrarlos dejaría el proyecto sin explicación de cómo
llegó a ser lo que es.

**Ninguno se usa como guía.** El estado actual vive en `../../README.md` y en `../ADR/`.

## Qué hay

| Documento | Qué era | Por qué se archivó |
|---|---|---|
| `control-Bc-tcp-c.md` | control TCP en C, 3 M de muestras (10/09) | su código se retiró del árbol el 16/09 ([ADR-007](../ADR/ADR-007-reduccion-de-alcance.md)). **Las mediciones son reales**: de aquí sale la descomposición 9 % lenguaje / 91 % transporte |
| `variante-E-icmp.md` | línea base ICMP + red real a internet | ídem. Aquí está la barra de 17 ms contra internet |
| `PLAN-DE-TRABAJO.md` | plan de tareas T1…T13 | ejecutado |
| `PLAN-EQUIPO.md` | reparto previo al 15/09 | superado por el reparto del 15/09 |
| `OPCIONES-SISTEMA.md` | análisis de qué sistema construir | la decisión se tomó y está en ADR-002 y ADR-004 |

## Los dos primeros no son lo mismo que los otros tres

`control-Bc-tcp-c.md` y `variante-E-icmp.md` **contienen datos medidos que el informe
usa**. Que su código ya no esté no invalida las cifras: se tomaron el 10 y el 13/09 sobre
el equipo de referencia, y los logs de aquellas corridas existieron.

Lo que sí cambia es que **hoy no se pueden recalcular desde el árbol**. Si el informe cita
una de esas cifras, tiene que decir de dónde sale. Si alguien necesita reproducirlas:

```bash
git log --all -- "**/control-Bc-tcp-c"     # encontrar el commit
git checkout <sha> -- "**/control-Bc-tcp-c"  # recuperar el código
```

Los otros tres son planeación cumplida: se leen para entender cómo se decidió, nunca para
saber qué hacer ahora.
