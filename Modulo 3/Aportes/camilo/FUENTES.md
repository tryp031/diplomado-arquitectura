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
| **Fecha de recepción** | 2026-10-25 (primera versión) · 2026-10-27 (actualización con la corrida oficial) |
| **Módulo** | 3 — Reto 3: Diseñando Arquitecturas Resilientes |
| **Tema** | Informe de arquitectura del Reto 3: atributos de calidad, restricciones, matriz de riesgos, tácticas, decisiones, opciones consideradas, modelo C4, despliegue en AWS y resultados de la **corrida oficial del 26/10/2026** |
| **Tipo** | `investigacion` — borrador de un entregable; **no es material oficial** y todavía no pasó por `Consolidado/` |
| **Fuentes** | `Modulo 3/Ejercicios/Reto3-Resiliencia/` (código, `template.yaml`, README, panel) · `Modulo 3/Material-Clase/Actividad-Reto3.md`, `Discord-Aclaraciones-Docente.md` y `k6-script-profesor-reto3.js` · `Modulo 2/Entregables/documento-tecnico/informe_arquitectura_reto2_alerta_flota_grupo2.docx` (modelo de formato) · `Modulo 3/Aportes/danny/m3-presentacion-reto3-danny.html` (matriz de riesgos, modificabilidad, restricciones y tácticas con nombre) · **evidencia de la corrida oficial** en `Modulo 3/Ejercicios/Reto3-Resiliencia/logs/evidencia-aws-20261027T004938Z/` (log del k6, diff, minutos, resumen y eventos del servidor), de donde salen las Figuras 3 y 4 |
| **Estado** | borrador · ⬜ sin consolidar |

**Qué contiene:** el informe con las dos figuras del modelo C4 (las del diagrama de arriba) y dos figuras nuevas hechas con la corrida oficial
(nivel y errores por minuto; latencia del router por minuto). Compara la arquitectura adoptada (router con estado en DynamoDB) con otra opción
(una sola función), incorpora la permanencia mínima de 2 minutos tras degradar y cierra con una conclusión.

**Qué cambia frente a la primera versión (PR #58):**
- Resultados de la **corrida oficial** (140 de 140 peticiones, secuencia 1-2-3-2-1, 8 de 8 minutos coherentes) en lugar de las corridas de prueba.
- Se agregan la matriz de riesgos (sección 2.2), las restricciones (2.1), el atributo de modificabilidad, las tácticas con nombre y la analogía con un circuit breaker.
- Se quita el ADR del texto, la sección de límites y preguntas pendientes y la tabla de tiempos por función de la primera versión.
- Los comentarios de Daniel sobre el PR #58 se aplicaron: la regla con permanencia, el pie de la Figura 2 y la cita del Discord.

**Límites:**
- **Las Figuras 1 y 2 siguen mostrando la regla anterior** («recupera de a un nivel»), sin la permanencia. Están pendientes de rehacer.
- **No usa todo el material del Módulo 3.** La matriz de riesgos y las tácticas con nombre vienen de la presentación de Daniel; no se incorporaron el escenario de calidad completo de ADD, el nivel de componentes de C4 ni la secuencia UML.
- **Las calificaciones de la matriz de riesgos son una primera versión**, pendientes de validar en consenso entre los tres integrantes.
- **Decisiones nuestras, por confirmar con el docente el 27/10:** la ventana (minuto de reloj), la permanencia de 2 minutos y si el ruteo debe ocurrir dentro de API Gateway. El docente dijo que se vería 1-2-3-3-2-1; el sistema produjo 1-2-3-2-1.
- **El documento y la presentación de Daniel no coinciden en dos puntos:** si el despliegue se hizo con infraestructura como código o a mano (el Word dice que a mano) y la latencia del router (la presentación dice 34 ms; el Word, 37 ms medidos).
- El arranque en frío (sección 10.2) usa cifras de una corrida de prueba anterior, no de la oficial.
- No incluye el video ni la exportación a PDF que pide el enunciado.
- La tabla de contenido del Word se actualiza en Word (clic derecho → Actualizar campo).
- **Actualización 2026-11-02:** la versión con la v3 (histéresis) es `m3-informe-arquitectura-reto3-histeresis-camilo.docx`, más abajo. Este documento se conserva como histórico de la v1.

## `m3-informe-arquitectura-reto3-histeresis-camilo.docx`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón, con asistencia de IA. Documento del Grupo 2 sobre el diseño de Daniel Mazo |
| **Fecha de recepción** | 2026-11-02 |
| **Módulo** | 3 — Reto 3: Diseñando Arquitecturas Resilientes |
| **Tema** | El informe de arquitectura actualizado a la **v3 (histéresis)**, la versión oficial del equipo desde el 30/10/2026, con la **corrida oficial del 02/11/2026** |
| **Tipo** | `investigacion` — borrador de un entregable; **no es material oficial** y todavía no pasó por `Consolidado/` |
| **Fuentes** | `Modulo 3/Ejercicios/Reto3-Resiliencia/` (`src/histeresis.py`, `src/router.py`, `src/estado.py`, `docs/ADR/ADR-002-histeresis-v3.md`, README) · `Modulo 3/Aportes/danny/m3-guia-despliegue-v3-camilo-danny.md` · la evidencia de `evidencia-corrida-oficial-v3-20261102/` (esta carpeta) · el informe anterior, `m3-informe-arquitectura-reto3-avance-camilo.docx` |
| **Estado** | borrador · ⬜ sin consolidar |

**Qué cambia frente a `m3-informe-arquitectura-reto3-avance-camilo.docx` (v1, que se conserva):**
- **La regla.** El «minuto» es un bloque de 20 peticiones numeradas y no el minuto de reloj; para recuperar se exigen rachas de 30 y 40 peticiones sin error en lugar de la permanencia de 2 minutos; el estado vive en un solo ítem `V3` de DynamoDB.
- **Resultados (sección 11).** Corrida oficial del 02/11/2026, 12:32 hora de Colombia: 140 de 140 peticiones, 35 con error, cambios de nivel en las peticiones 21, 61, 126 y 136, secuencia 1-2-3-2-1. El k6 midió 167 ms de promedio y el router, 52,8 ms. Las Figuras 4 y 5 se rehicieron con el servidor.
- **Figuras.** La Figura 3 es nueva (secuencia de una petición) y las Figuras 1 y 2 se actualizaron a la v3.
- **Matriz de riesgos.** R1 a R4 se ajustaron a la v3 y se agregaron R5 (los umbrales 30 y 40 dependen del script) y R6 (el ítem único de estado es un punto caliente).
- **Conclusión y glosario.** Se agregan los términos *Histéresis* y *Racha de éxitos*.

**Límites:**
- **Las calificaciones de la matriz de riesgos siguen pendientes de consenso** entre los tres integrantes; las de R5 y R6 son de Camilo.
- **La v3 cuesta más por petición.** El router pasó de unos 37 ms a unos 53 ms por las lecturas y escrituras adicionales en DynamoDB.
- **El panel todavía calcula la regla de la v1.** Su regla y su coherencia por minuto no aplican a la v3; la evidencia es el log del k6 y los eventos del router (sección 8 del informe).
- **Los datos de arranque en frío (sección 10.2) son de una prueba anterior**, no de la corrida oficial.
- **Otras corridas de prueba del mismo día no se incluyen.**
- **Pregunta abierta:** el docente dijo que se vería 1-2-3-3-2-1; con el script oficial esta regla produce 1-2-3-2-1.
- No incluye el video ni la exportación a PDF que pide el enunciado.
- La tabla de contenido del Word se actualiza en Word (clic derecho → Actualizar campo).

## `evidencia-corrida-oficial-v3-20261102/`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón. La corrida se lanzó desde el panel de control de Daniel Mazo |
| **Fecha de recepción** | 2026-11-02 (corrida a las 12:32 hora de Colombia, 17:32 UTC) |
| **Módulo** | 3 — Reto 3: Diseñando Arquitecturas Resilientes |
| **Tema** | Evidencia de la corrida oficial de la v3 en AWS (us-east-2) con el script de k6 del docente |
| **Tipo** | `dato medido propio` |
| **Fuentes** | Exportación del panel (log del k6, diff, minutos y resumen) y eventos del router en CloudWatch Logs (`/aws/lambda/reto3-router`) de la ventana 17:33:00 a 17:40:30 UTC, filtrados a `PETICION`, `CAMBIO_NIVEL` y `CORRIDA_NUEVA` |
| **Estado** | evidencia usada por el informe de esta carpeta |

**Qué contiene:** `…-k6.log` (salida cruda del k6, 140 iteraciones), `…-k6-diff.txt` (el script solo cambia la URL), `…-servidor.jsonl` (140 `PETICION`, 4 `CAMBIO_NIVEL` y 1 `CORRIDA_NUEVA`, de la petición 1 a la 140 sin repetidas), `…-minutos.csv` y `…-resumen.json`.

**Límites:**
- **`minutos.csv` y `resumen.json` no son evidencia de la v3.** El panel los calcula con la regla de la v1 (marca «NO» en varios minutos y `regla_se_cumple: false`) y, sin credenciales de lectura, `coherencia_cliente_servidor` sale vacía. Se guardan porque el panel los exporta junto con el resto.
- El `CORRIDA_NUEVA` trae `peticiones_previas: 49` y `nivel_previo: 3`: el estado venía de pruebas anteriores y la regla de 15 s sin tráfico lo reinició.
- Es una sola corrida. Hubo otras de prueba el mismo día, que no se incluyen.

## `codigo-v3-histeresis-comentado/`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón, con asistencia de IA, sobre el código de Daniel Mazo |
| **Fecha de recepción** | 2026-11-02 |
| **Módulo** | 3 — Reto 3: Diseñando Arquitecturas Resilientes |
| **Tema** | Los seis módulos de `src/` de la v3 con comentarios explicativos; es lo que se subió a mano a las cuatro Lambdas |
| **Tipo** | `investigacion` — copia comentada; **el código oficial es `Modulo 3/Ejercicios/Reto3-Resiliencia/src/`** |
| **Fuentes** | `Modulo 3/Ejercicios/Reto3-Resiliencia/src/` (checkout `795c948`) |
| **Estado** | borrador · ⬜ sin consolidar |

**Qué contiene:** `router.py`, `histeresis.py`, `estado.py`, `reglas.py`, `niveles.py` y `observabilidad.py`. Solo cambian los comentarios y las descripciones de los módulos; el código es idéntico al de `src/` (se comparó el árbol sintáctico sin contar las descripciones).

**Límites:**
- El zip desplegado no se versiona (`*.zip` está ignorado). Su `CodeSha256` en las cuatro Lambdas es `hPWUcyOR142EWDxW65X2OpDufGf6AiSWxnZYFhDFcz4=`.
- `scripts/verificar-aws.sh` compara con el `CodeSha256` del zip de `scripts/empaquetar.py` (`ufr+zGjlSYZb6qK+CiKl2Ylrx99kgZFOnNcFkDB/KO0=`), así que marca una diferencia aunque el código sea el mismo.
- Si `src/` cambia, esta copia queda desactualizada.

## `diagrama-contenedores-reto3-histeresis.html`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón, con asistencia de IA |
| **Fecha de recepción** | 2026-11-02 |
| **Módulo** | 3 — Reto 3: Diseñando Arquitecturas Resilientes |
| **Tema** | Las dos figuras del modelo C4 (vista general y detalle de AWS) actualizadas a la v3; el original, `diagrama-contenedores-reto3.html`, se conserva |
| **Tipo** | `investigacion` — representación visual de un diseño ajeno (el de Daniel); **no es material oficial** |
| **Fuentes** | `diagrama-contenedores-reto3.html` · `Modulo 3/Ejercicios/Reto3-Resiliencia/docs/ADR/ADR-002-histeresis-v3.md` |
| **Estado** | borrador · ⬜ sin consolidar |

**Qué cambia:** el router dice «decide por bloque de 20 peticiones» y «sube con rachas»; DynamoDB muestra «un solo ítem (V3)» y lo que guarda; la nota al pie dice que las rachas de 30 y 40 son decisión del equipo; el panel muestra «respuestas del k6 y logs de cambios».

**Límites:** dibuja el diseño de Daniel y no lo valida. Las figuras del informe salen de este archivo.
