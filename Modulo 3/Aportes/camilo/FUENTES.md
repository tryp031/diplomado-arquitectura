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
bajo cada caja y una leyenda de colores.

**Límites:**
- Dibuja el diseño de Danny; no lo modifica ni lo valida. Si el diseño cambia (por ejemplo, tras el encuentro
  del 27/10), hay que actualizar los diagramas.
- **Actualización 2026-10-25.** Las figuras se rehicieron con una paleta corta: marino = servicios de AWS del sistema, dorado = el router que
  decide el nivel, verde = el estado compartido (DynamoDB). La marca «✓ AWS» indica lo validado con el k6 oficial en **AWS real** (corridas del
  21 y 22/10/2026; ver la sección 11 del informe de avance, ficha más abajo). La versión anterior usaba el color como estado de validación
  (verde = LocalStack, ámbar = pendiente en AWS real); esa versión se reemplaza.
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

**Actualización 2026-10-25 (medición en AWS real).** Lo que el análisis dejaba como riesgo se midió en las corridas del 21 y 22/10:
- Arranque en frío del router: 257 ms de arranque y 1.386 ms de ejecución en la primera petición. Cada Lambda de nivel arrancó en unos 80 ms
  (máximo 81 a 84 ms) y ejecuta en unos 2 ms. El k6 vio un máximo de 2,12 s, en esa primera petición.
- El resumen del k6 dio 140 de 140 iteraciones y 35 respuestas fallidas, que son los 5 + 15 + 15 errores del script: **no hubo fallas
  inesperadas ni 503 por arranque en frío**. El riesgo del N1 que se enfría no se materializó: su arranque (~80 ms) está muy por debajo del
  `read_timeout` de 3 s.
- La decisión se mantiene: no hay calentador automático. Se calientan a mano las cuatro Lambdas justo antes de una carga (una prueba de cada nivel
  desde la consola y tres o cuatro peticiones sin error al API). Esas peticiones aparecen en CloudWatch; se excluyen acotando el rango de tiempo.
- Pendiente: la **medición oficial** de entrega, con calentamiento previo, el log y el `diff` del k6 guardados.

## `m3-informe-arquitectura-reto3-avance-camilo.docx`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón, con asistencia de IA. Documento del Grupo 2 sobre el diseño de Daniel Mazo |
| **Fecha de recepción** | 2026-10-25 |
| **Módulo** | 3 — Reto 3: Diseñando Arquitecturas Resilientes |
| **Tema** | Informe de arquitectura del Reto 3, versión de avance: atributos de calidad, tácticas, decisiones, opciones consideradas, modelo C4, despliegue en AWS y resultados de las corridas de prueba |
| **Tipo** | `investigacion` — borrador de un entregable; **no es material oficial** y todavía no pasó por `Consolidado/` |
| **Fuentes** | `Modulo 3/Ejercicios/Reto3-Resiliencia/` (código, `template.yaml`, README, panel) · `docs/superpowers/specs/2026-10-18-reto3-resiliencia-design.md` · `Modulo 3/Material-Clase/Actividad-Reto3.md`, `Discord-Aclaraciones-Docente.md` y `k6-script-profesor-reto3.js` · `Modulo 2/Entregables/documento-tecnico/informe_arquitectura_reto2_alerta_flota_grupo2.docx` (modelo de formato) · corridas en AWS del 21 y 22/10/2026 (resumen de k6 y CloudWatch Logs Insights, copiados en la sesión de trabajo; **no se guardaron los logs completos del k6**) · precios de lista de AWS (API Gateway, Lambda, DynamoDB y CloudWatch), consultados en octubre de 2026 |
| **Estado** | borrador · ⬜ sin consolidar |

**Qué contiene:** el informe de 13 secciones más un glosario, con las dos figuras del modelo C4 (las del diagrama de arriba). Compara la
arquitectura adoptada (router con estado en DynamoDB) con otra opción (una sola función) y registra los resultados de las corridas de prueba.

**Límites:**
- **La medición oficial está pendiente.** La sección 11 son resultados de **corridas de prueba** (21 y 22/10/2026). Falta la corrida de entrega,
  con calentamiento previo y con el log completo y el `diff` del k6 guardados. Los dos resultados vienen de corridas distintas (los cambios de
  nivel, del 21/10; el resumen de k6 y los tiempos, del 22/10) y hay que unificarlos con la corrida oficial.
- **Sigue el formato del informe del Módulo 2** (`informe_arquitectura_reto2_alerta_flota_grupo2.docx`): resumen ejecutivo, atributos de
  calidad, tácticas, decisiones, contrato HTTP, opciones, plano de control, C4, despliegue, resultados, disponibilidad y glosario.
- **No contempla material del Módulo 3.** Las tácticas y el análisis salen del Módulo 2 y de conocimiento complementario; no usa los contenidos
  de `Material-Clase` del Módulo 3 (Genially de estilos, técnicas ASR/QAW, ADD, análisis de riesgos y evaluación). Si se quiere incorporarlos,
  es un cambio aparte.
- **Costos estimados, no medidos:** precios de lista de us-east-1 (se asumen iguales en us-east-2), sin la calculadora de AWS; el tamaño de los
  logs por petición es una estimación.
- **Decisiones nuestras, por confirmar con el docente el 27/10:** la ventana (minuto de reloj), la recuperación de a un nivel por minuto y si el
  ruteo debe ocurrir dentro de API Gateway. El script oficial no produce la secuencia 1-2-3-3-2-1 que dijo el docente (produce 1-2-1-3-2-3-2-1);
  queda registrado en la sección 13.
- **Pendiente de validar en AWS:** el panel leyendo AWS con el usuario de solo lectura, y los widgets del dashboard (la versión final no se
  verificó). No incluye el video ni la exportación a PDF que pide el enunciado.
- La tabla de contenido del Word se actualiza en Word (clic derecho → Actualizar campo).
