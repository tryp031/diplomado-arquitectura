# Aportes de Camilo — Módulo 3

> Ficha de origen. Se llena **al recibir** el aporte, no después.

## `diagrama-contenedores-reto3.html`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón, con asistencia de IA |
| **Fecha de recepción** | 2026-10-19 |
| **Módulo** | 3 — Reto 3: Diseñando Arquitecturas Resilientes |
| **Tema** | Diagramas de la propuesta de Danny: vista general (zoom-out) y detalle de AWS, con el «qué hace» de cada pieza |
| **Tipo** | `investigacion` — representación visual de un diseño ajeno (el de Danny); **no es material oficial** |
| **Fuentes** | `docs/superpowers/specs/2026-10-18-reto3-resiliencia-design.md` · `Modulo 3/Ejercicios/Reto3-Resiliencia/` (`template.yaml`, `src/router.py`, `src/reglas.py`, `panel/`, `tests/test_k6_oficial.py`, README) · `Modulo 3/Material-Clase/k6-script-profesor-reto3.js` · `Modulo 3/Material-Clase/Discord-Aclaraciones-Docente.md` · `Modulo 3/Aportes/danny/FUENTES.md` |
| **Estado** | borrador · ⬜ sin consolidar |

**Qué contiene:** una página con dos figuras en SVG. La primera es la vista general: el panel de control
(k6 oficial y panel de estado) frente a AWS, con DynamoDB y CloudWatch dentro del plano de AWS. El panel lee
DynamoDB y los logs de CloudWatch, y además puede enviar una petición a mano al API Gateway. La segunda es el
detalle de AWS: API Gateway, Lambda router, las tres Lambdas de nivel, DynamoDB y CloudWatch, con el «qué hace»
bajo cada caja y una leyenda de estado.

**Límites:**
- Dibuja el diseño de Danny; no lo modifica ni lo valida. Si el diseño cambia (por ejemplo, tras el encuentro
  del 27/10), hay que actualizar los diagramas.
- El color indica el estado de validación: **verde** = validado con el k6 oficial en **LocalStack**;
  **ámbar** = pendiente de confirmar en AWS real (métricas EMF y dashboard); **gris** = actor externo.
  Todavía **no hay corrida en AWS real**.
- **Decisión por confirmar:** recuperar de a un nivel por minuto es decisión del equipo, pendiente de confirmar
  con el docente el 27/10 (riesgo R3 de la spec). Por eso la regla se escribe `nivel(m) = f(nivel(m−1), errores(m−1))`
  y no solo en función de los errores.
- El panel no es de solo lectura en todo: lee DynamoDB y logs (`filter_log_events`), envía una petición a mano que
  cuenta en el estado y, solo en LocalStack, puede borrar el estado. No lee métricas ni el dashboard.
- Los timeouts de la figura siguen al código (`read_timeout=3` hacia las Lambdas de nivel), no a la spec, que decía 2 s.

**Por qué no se agrega un calentador de Lambdas.** Es un análisis, no una medición, y deja un riesgo identificado:
- **Qué cuenta como error.** En `router.py`, si DynamoDB no responde en 1 s el router responde Nivel 3 **sin contar**
  el error (falla segura). Pero si la Lambda de nivel no responde en 3 s (`read_timeout`, un solo intento), emite
  `FALLA_NIVEL`, responde 503 y **sí cuenta** como error (`es_error = statusCode >= 500`). Un arranque en frío lento
  de una Lambda de nivel sí puede sumar un error.
- **El caso que importa es el Nivel 1.** En la simulación del k6 con pasos de 3,2 s, N1 atiende las iteraciones 1 a 19
  y 39 a 57, queda sin uso unos 4 minutos (iteraciones 58 a 132) y la corrida cierra con 8 peticiones en N1, que son la
  prueba de que «termina en N1». Si su arranque en frío superara los 3 s, saldrían 503 y el mensaje final no sería
  «Nivel 1: OK». Es improbable con Python 3.12 en arm64 (`template.yaml`), pero es el riesgo que hay que nombrar.
- **N2 y N3 pesan menos.** Un error de más en un minuto sin errores (2, 4 y 6) no llega al umbral de 5, y en los minutos
  con errores del k6 oficial (5, 15 y 15 de 20 peticiones) ya se está en el umbral o por encima. No se midió su
  arranque en frío en AWS.
- **Lo que sí sostiene la decisión.** `tests/test_k6_oficial.py` reproduce el k6 con pasos de 3,05 a 4,0 s y la
  secuencia siempre recorre los tres niveles y termina en N1. El riesgo R1 de la spec va en el sentido contrario
  (una latencia menor de ~25 ms termina en N2), así que una latencia mayor por arranque en frío es la dirección
  segura **respecto a los límites de minuto**. Eso no cubre el caso del timeout de 3 s de arriba.
- **Si se agregara.** Debería invocar directamente `reto3-nivel{1,2,3}`, como el del Reto 2, que calentaba el notifier
  y no la ingesta. Así no toca el conteo ni exige modificar `router.py`. Si pasara por el router, inflaría
  `peticiones` en la evidencia y ensuciaría los logs; el nivel de un minuto no se vería alterado, porque es una
  función determinista del minuto anterior (salvo la carrera del segundo 59,9, riesgo R6).
- **Mitigación sin calentador.** Antes de la corrida, invocar a mano cada `reto3-nivel{1,2,3}` desde la consola. No
  cubre el N1 que se enfría durante la corrida; ese riesgo se asume.
- **Se confirma en la primera corrida en AWS real**, revisando la duración de inicio (`Init Duration`) en los logs y
  si hay 503 en la primera petición o en el tramo final en N1. Si aparece, se reevalúa: subir el `read_timeout` o
  agregar un calentador que invoque directo los niveles.
