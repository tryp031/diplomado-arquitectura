# ADR-001 — Permanencia mínima de 2 minutos tras degradar

**Estado:** **Reemplazada por ADR-002** (histéresis, v3) el 30/10/2026, por decisión del equipo. Se conserva como
histórico y sigue disponible con `Modo=reloj`. Antes: aceptada (se confirma con el docente el 27/10/2026).
**Fecha:** 2026-10-22
**Decisores:** Danny (Group 2), con el análisis de Claude. Lo propuso Camilo al compartir las notas del docente.
**Contexto del módulo / ejercicio:** Módulo 3, Reto 3 (resiliencia en 3 niveles). Modifica la regla de la spec
`docs/superpowers/specs/2026-10-18-reto3-resiliencia-design.md` §3.

## Contexto

- **[Curso]** El docente dice que los errores del minuto anterior deciden el nivel del minuto actual (17/09/2026) y que
  se degrada de inmediato (18/09/2026). En el mismo hilo afirma: «siempre vas a ver nivel 1-2-3-3-2-1» y «si te salta
  es problema del sistema» (`Material-Clase/Discord-Aclaraciones-Docente.md` §3 y §4).
- **[Curso]** El k6 oficial no inyecta «5 y 10 errores», como dice el docente. Inyecta **5 / 0 / 15 / 0 / 15 / 0 / 0**
  por minuto: cada minuto con errores va seguido de uno limpio.
- Con la regla de la spec (bajar de golpe, subir de a un nivel por minuto), el k6 produce **1-2-1-3-2-3-2-1**. En esa
  secuencia hay un salto de 1 a 3 en el minuto 4 y el sistema oscila entre 3 y 2. Es justo el síntoma que el docente
  llama «problema del sistema».
- **No existe una regla que use solo el minuto anterior y dé 1-2-3-3-2-1 con este script.** Los minutos 2 y 4 no tienen
  errores, así que cualquier regla sin memoria recupera en esos minutos.

## Problema

¿Qué regla de recuperación hace que el k6 oficial muestre la secuencia que espera el docente, sin inventar una regla
hecha a la medida del script?

## Opciones consideradas

| | Regla | Nivel por minuto (k6) | Secuencia | Diagrama de la sesión (0/5/10/5/0) |
|---|---|---|---|---|
| A | Pura del §3: solo el minuto anterior | 1,2,1,3,1,3,1,1 | 1-2-1-3-1-3-1 | ✅ |
| B | Spec §3: degrada de golpe, recupera 1 nivel/min | 1,2,1,3,2,3,2,1 | 1-2-1-3-2-3-2-1 | ✅ |
| **C** | **B + permanencia mínima de 2 min tras degradar** | **1,2,2,3,3,3,2,1** | **1-2-3-2-1** | ❌ en la ventana 4-5 da N3 y no N2 |
| D | Ventana deslizante de 2 minutos | 1,2,2,3,3,3,3,1 | 1-2-3-1 | ❌ y además salta de 3 a 1 |

## Decisión

Se elige la **C**. Cuando el sistema se degrada, el nivel nuevo se mantiene **al menos 2 minutos**. Pasado ese
plazo, si el minuto anterior quedó limpio, se recupera de a un nivel por minuto. La degradación sigue siendo inmediata.

```
meta = objetivo(errores(m-1))                       # ≥ 10 → N3 · ≥ 5 → N2 · si no, N1
si meta > nivel(m-1):  nivel(m) = meta; degradado_en = m          # se degrada de inmediato
si meta = nivel(m-1):  se mantiene (no reinicia la permanencia)
si meta < nivel(m-1):  si m - degradado_en < permanencia → se mantiene
                       si no → nivel(m) = max(meta, nivel(m-1) - 1)
```

El parámetro es `PermanenciaMinutos` en `template.yaml` (variable `PERMANENCIA_MINUTOS`, valor por defecto 2). Con 1
vuelve a la regla B **sin cambiar el código**.

## Justificación

- **Es una táctica real, no un ajuste al script.** Es histéresis contra el *flapping*. Se usa lo mismo en el cooldown
  de un autoscaler y en el tiempo de espera de un circuit breaker abierto antes de pasar a semiabierto. Un sistema que
  acaba de degradarse no se recupera con un solo minuto bueno: si fuera así, oscilaría al ritmo de la falla.
- **El atributo priorizado es la disponibilidad bajo falla (estabilidad).** Un nivel que cambia cada minuto le da al
  cliente un contrato distinto en cada minuto. Eso es peor que sostener un nivel degradado un minuto de más.
- **Coincide con lo observable que pide el docente:** sin saltos 1 → 3, sin saltos 3 → 1 y la forma 1-2-3-(3)-2-1.
- **Respeta la regla del docente:** la meta del minuto la deciden los errores del minuto anterior. La permanencia
  solo retrasa la recuperación. Nunca retrasa la degradación.

## Evidencia (22/10/2026)

| Corrida | Regla | Secuencia | Coherencia | 503 «mantenimiento» | Latencia media |
|---|---|---|---|---|---|
| LocalStack, `logs/evidencia-local-20261023T010346Z/` | C (permanencia 2) | **1-2-3-2-1**, termina en N1 | 8/8 min cliente = servidor = regla | **15** | 88 ms |
| AWS de Camilo, `logs/k6-aws-20261023T010353Z.log` | B (despliegue anterior) | 1-2-1-3-2-3-2-1, termina en N1 | sin lectura del servidor | 1 | 178 ms |

**Efecto adicional:** con la regla C, los 15 errores del minuto 5 caen en un minuto en N3 y el sistema responde
«Nivel 3: Sistema bajo mantenimiento, intente más tarde». Con la regla B ese mensaje no aparecía en LocalStack. Era la
pregunta 4 de la spec §13, que el enunciado pide. En AWS apareció una sola vez y solo porque la latencia corrió el
borde del minuto.

## Ventajas

- La demo con el k6 oficial da **1-2-3-2-1**. Por minuto: 1,2,2,3,3,3,2,1.
- El mensaje de mantenimiento de N3 aparece con el script oficial: 15 veces en la corrida de LocalStack.
- El cambio es pequeño y local: una función pura en `src/reglas.py` y un atributo más en la misma escritura
  condicional de DynamoDB. La concurrencia entre instancias no cambia.
- Es reversible con un parámetro del despliegue.

## Desventajas

- **Se aparta del diagrama de la sesión en una fila.** Con 0/5/10/5/0 errores, la ventana 4-5 da N3 en vez de N2. Queda
  documentado en `test_diagrama_de_la_sesion_con_permanencia_se_desvia_en_la_ventana_4_5`.
- Después de una falla real y breve, el sistema opera degradado un minuto más de lo estrictamente necesario.
- Agrega estado: `degradado_en` se guarda en el ítem del minuto.

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| El docente quiere la regla B (el diagrama manda) | Media | Medio | `PermanenciaMinutos=1` y redesplegar. Se pregunta el 27/10 |
| R1 (latencia < ~25 ms → la prueba termina en N2) | Baja en AWS | Alto | Sin cambios respecto de la spec. `test_riesgo_r1_latencia_cero_termina_en_n2` lo sigue documentando |
| Ítems viejos sin `degradado_en` | Baja (TTL de 24 h) | Bajo | Sin el atributo no hay permanencia: se comporta como la regla B |

## Consecuencias

- El panel cambia el criterio «sin saltos 3 → 1» por «sin saltos de nivel» y agrega «secuencia 1-2-3-2-1». También
  verifica la regla con los errores que ve el propio k6, aunque no haya permiso de lectura del servidor.
- El despliegue de AWS (cuenta de Camilo) **tiene que redesplegarse** para que la permanencia tenga efecto.
- La pregunta 1 de la spec §13 cambia a: «¿Se acepta la permanencia de 2 min aunque se aparte de la fila 4-5 del
  diagrama?».
