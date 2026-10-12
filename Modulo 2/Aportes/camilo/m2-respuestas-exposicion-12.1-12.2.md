# Reto 2 — Respuestas a 12.1 y 12.2 (preparación de exposición), camino AWS

| Campo | Valor |
|---|---|
| **Tema** | Puntos 12.1 y 12.2 de `Modulo 2/Aportes/danny/m2-preguntas-encuentro-0610-danny.md` — cómo los cubre el diseño AWS (opción B) y la capa de control planeada |
| **Fecha** | 2026-10-12 |
| **Tipo** | `investigacion` — elaborado con IA, apoyado en mediciones reales de esta sesión; **no es material oficial** |
| **Fuentes** | `arquitectura-aws-opcion-b.md` (diseño y evidencia de los 5 pasos) · `medir-aws.py` (mediciones vía CloudWatch) · `m2-preguntas-encuentro-0610-danny.md` (preguntas originales) · sistema local `Reto2-Alerta-Flota/` (comparación) |
| **Estado** | borrador, para repasar antes de la exposición |

> **Etiquetas de origen:** **Curso** = lo dice el material del diplomado · **Complementario** = conocimiento general de arquitectura/cloud · **Recomendación** = criterio propio de arquitecto.
> **Etiquetas de confianza:** **Seguro** = medido o verificado en esta sesión · **Probable** = razonado a partir de cómo funciona AWS, sin verificarlo directamente · **Suposición** = no confirmado, dicho a título informativo.
>
> **Sobre la "capa de control":** el panel de control (`panel/`) hoy solo existe para el entorno **local** (lee Docker/Redis directamente). Para AWS está **planeado, no construido**. Mientras no exista, su función la cumple `medir-aws.py` (CloudWatch Logs Insights por `boto3`) y la consola de AWS directamente — se marca con 🛠️ en cada respuesta donde aplica.
>
> **Cómo leer cada respuesta de 12.2:** primero la respuesta directa (en negrita), luego la justificación técnica, y cuando existe, una línea **Evidencia:** con el dato medido — no una cifra inventada ni "debería funcionar".

---

## 12.1 — Temas de teoría: cómo los cubrimos

| Tema | Cómo lo cubrimos en el camino AWS | Evidencia / justificación |
|---|---|---|
| **Atributos de calidad** | Priorizamos **disponibilidad/confiabilidad** del camino `Emergency` (que la alerta nunca se pierda en silencio) por encima de latencia mínima o costo. Seguridad como restricción dura (TLS 1.3, IAM de mínimo privilegio), no como objetivo a maximizar. | *Recomendación*: SQS como buffer, DLQ explícito, y la decisión documentada de "duplicado antes que pérdida" (ver tema de entrega de mensajes) son consecuencia directa de esa priorización. |
| **Tácticas de arquitectura** | Una táctica es una decisión de diseño reusable para lograr un atributo de calidad, distinta de un patrón (que es una composición de tácticas). Aplicamos: *intermediario/broker* (SQS), *limitación de demanda* (rate/burst en API Gateway), *timeout + reintento acotado* (notifier), *recursos dedicados* (concurrencia reservada). | *Curso + Complementario*. Cada una mapea a un componente concreto — ver pregunta 3 de 12.2. |
| **Procesamiento síncrono y asíncrono** | La petición HTTP **termina cuando `reto2-ingesta` responde** (200/503) — antes de que exista cualquier intento de envío de correo. El envío ocurre después, de forma asíncrona, disparado por el trigger de SQS. | *Seguro*, es el propio código: `ingesta.py` nunca invoca a `notifier`, solo publica en SQS y responde. |
| **Colas y sobrecarga** | SQS desacopla productor (ingesta) de consumidor (notifier). Si notifier no da abasto, los mensajes se **acumulan en la cola** (no se pierden ni bloquean a ingesta) hasta que hay capacidad — visibilidad de 90 s como ventana de reintento. | *Seguro*, validado en el paso 3 del diseño (mensaje esperando en la cola hasta que se activó el trigger). |
| **Limitación de solicitudes** | Diferenciamos **tasa** (peticiones/s sostenidas, limitada en el *stage* de API Gateway: 15 r/s) de **concurrencia** (cuántas a la vez, limitada en Lambda con "Simultaneidad reservada": 10 en ingesta) de **capacidad de procesamiento** (cuántas completa la Lambda por segundo, función de su propia latencia). Son tres mecanismos distintos, en capas distintas. | *Seguro*: medimos las dos primeras por separado — preguntas 4 y 10 de 12.2. |
| **Rate y burst** | *Rate* = velocidad de recarga del "balde de tokens" (15/s); *burst* = tamaño máximo del balde (2000), absorbe ráfagas cortas sin rechazar. Con 1000 peticiones del test (< 2000), el balde nunca se vacía. | *Curso + Seguro*: 1000/1000 sin ningún `429` en las corridas con la concurrencia ya corregida. |
| **Escalabilidad y paralelismo** | Horizontal = más instancias de Lambda ejecutando a la vez. Vertical = más memoria/CPU por instancia (no lo tocamos: 128 MB por defecto). Paralelismo = ejecución simultánea real (los 10 VUs de k6). Respetamos el máximo de instancias con "Simultaneidad reservada", mecanismo **nativo** de AWS para ese límite. | *Seguro*: ver el hallazgo de throttling corregido (pregunta 10). |
| **HTTP y HTTPS** | `200` = aceptado y válido (y, si es `Emergency`, ya encolado); `429` = rechazado por el *rate limit* del *stage*; `5xx` = error de servidor o *throttle* de Lambda no manejado como respuesta de negocio. No usamos `202` (decisión de simplicidad). HTTPS: API Gateway fuerza TLS 1.3 únicamente, modo de acceso Estricto con SNI obligatorio. | *Curso + Seguro*: política verificada en consola; `200`/`503` verificado en los pasos 2 y 3. |
| **Entrega y procesamiento de mensajes** | SQS estándar entrega **al menos una vez** → posibles duplicados. Decisión: preferir un correo duplicado a una alerta perdida. `event_id` único habilitaría deduplicar si hiciera falta — hoy no se filtra, un duplicado no rompe nada. | *Recomendación*, documentada en la sección 6 del diseño, mismo criterio que el sistema local con Redis Streams. |
| **Medición y trazabilidad** | *Latencia* = tiempo de una operación puntual. *Rendimiento* = throughput agregado. Correlacionamos ambas vía `event_id` y timestamps ISO 8601 en cada log JSON. | *Seguro*, con `medir-aws.py` 🛠️ como la herramienta que hace esa correlación — el panel para AWS sigue pendiente. |
| **Ubicación de componentes** | Región (`us-east-2`) elegida con **evidencia medida**, no por defecto. Gmail, como dependencia externa, no se mide con la misma certeza. | *Seguro*: metodología y datos en la sección 8 del diseño. |
| **Pruebas con k6** | El script oficial reparte 1000 peticiones entre 10 VUs. Por un defecto conocido de `shared-iterations`, no garantiza cuántos `Emergency` genera (vimos 0, 1 y hasta 3 simultáneos). | *Seguro*, verificado varias veces en esta sesión. |
| **Envío de correo** | *Entregado al servidor* = SES acepta sin excepción (`EMAIL_SENT`, bajo control). *Llega al destinatario* = aparece en Gmail (fuera de control). | *Seguro*: logs de CloudWatch para lo primero, verificación manual para lo segundo. |

---

## 12.2 — Respuestas a las posibles preguntas

### 1. ¿Por qué escogieron nube o local? ¿Qué cambiaría al desplegar en otro entorno?

**Empezamos en local y migramos a AWS por una razón de fidelidad al enunciado, no de preferencia tecnológica.**

Local (Docker Compose) primero porque el enunciado es condicional ("si se usa API Gateway...") y permite iterar sin depender de una cuenta en la nube *(Recomendación)*. AWS (opción B, serverless) después porque el diplomado es de *Cloud Computing* y porque ofrece los servicios administrados que el enunciado nombra literalmente, en vez de imitarlos con nginx + Redis + Mailpit *(Curso)*.

Si se desplegara en otro proveedor (Azure, GCP), cambiarían los **nombres** de los servicios (API Management, Service Bus/Pub-Sub, un SMTP distinto) pero el **patrón arquitectónico** (gateway con límite → cola → procesador asíncrono → correo) se mantiene igual *(Complementario, Probable)*. La lógica de negocio no depende de ningún proveedor — solo los adaptadores cambiarían.

**Evidencia:** las dos versiones (local y AWS) implementan la misma arquitectura lógica (ingesta → cola → notifier → DLQ), documentada en la tabla de equivalencia de `diagrama-contenedores-opcion-b.html`.

### 2. ¿Cuál es el atributo de calidad más importante y dónde se refleja?

**Disponibilidad/confiabilidad de la alerta `Emergency`: que el intento de envío nunca se pierda en silencio, aunque cueste un duplicado ocasional.** *(Recomendación)*

Se refleja en tres decisiones concretas: SQS como amortiguador entre ingesta y notifier, el DLQ como respaldo explícito (el código manda a la DLQ él mismo, sin esperar el redrive automático), y la decisión documentada de tolerar duplicados antes que arriesgar una pérdida.

**Evidencia:** sección 6 de `arquitectura-aws-opcion-b.md`, y el comportamiento real observado — en ningún momento de la sesión un `Emergency` quedó sin intento de envío, aun cuando fallaba (siempre terminó en `EMAIL_DLQ`).

### 3. ¿Qué tácticas aplicaron y qué componente implementa cada una?

*(Curso + Complementario)* — una táctica logra un atributo de calidad; un patrón es una composición de tácticas.

| Táctica | Componente | Para qué atributo |
|---|---|---|
| Intermediario / broker | SQS (`reto2-emergencias`) | Disponibilidad bajo picos |
| Limitación de demanda | *Stage* de API Gateway (rate 15, burst 2000) | Cumplimiento del límite, protección de capacidad |
| Timeout + reintento acotado | Lambda `reto2-notifier` (2 intentos, ≤12 s) | Disponibilidad del envío sin violar el tiempo |
| Recursos dedicados | Concurrencia reservada (10 / 2) | Cumplimiento del límite de instancias |
| Redundancia de respaldo | DLQ explícito + redrive (maxReceiveCount 3) | Confiabilidad — no perder eventos fallidos |

**Evidencia:** las cinco están configuradas y validadas en los pasos 1-5 del despliegue (`arquitectura-aws-opcion-b.md`, sección 9).

### 4. ¿Dónde se limita el backend a 15 solicitudes por segundo y cómo verificaron ese límite?

**En el *stage* `prod` de API Gateway (rate=15, burst=2000) — antes de que la petición llegue a cualquier Lambda.** *(Curso + Seguro)*

**Evidencia:** k6 oficial (1000 peticiones / 10 VUs / ~22.5 s ≈ **44.7 req/s** sostenidos) sin ningún `429`.

**Limitación honesta** *(Probable, no verificado directamente)*: esto confirma que el *burst* absorbe el volumen del test (1000 < 2000), no que se probó el *rate* de 15/s bajo una carga sostenida lo bastante larga como para agotarlo.

### 5. ¿Qué sucede si llegan más solicitudes de las que el backend puede procesar?

**Depende de en qué capa se agote la capacidad — son dos mecanismos distintos con dos respuestas distintas.**

- Si se agota el *burst* de API Gateway: responde `429` nativamente *(Curso, Seguro)*.
- Si se supera la concurrencia reservada de Lambda: AWS la frena (*throttle*) y API Gateway lo traduce en un error de servidor *(Complementario, Seguro)*.

**Evidencia:** con la reservada de `reto2-ingesta` en 8 y 10 VUs de carga, fallaron exactamente 2 de 1000 peticiones, coincidiendo con `AWS/Lambda Throttles = 2` del mismo minuto. Al subir la reservada a 10, el resultado fue 1000/1000.

### 6. ¿Qué garantiza exactamente el `200 OK` en su implementación?

**Que el payload es válido y, si es `Emergency`, que el evento ya quedó encolado en SQS — no que el correo se envió ni que llegó.** *(Seguro, es el propio código)*

Si el encolado falla, responde `503` explícitamente; nunca confirma una alerta que no quedó guardada en ningún lado.

**Evidencia:** en el paso 2 del despliegue, antes de que existiera la cola, cualquier `Emergency` devolvía `503` a propósito — comportamiento reproducido y confirmado, no teórico.

### 7. ¿Cómo demuestran que se procesaron 1.000 mensajes únicos y no solamente que se recibieron 1.000 peticiones?

**Contando `event_id` (UUID) distintos en los logs, no peticiones HTTP.** *(Seguro)*

Cada evento recibe un `event_id` generado en `reto2-ingesta`, registrado en `EVENT_RECEIVED`/`EMERGENCY_RECEIVED`.

**Evidencia:** `medir-aws.py` 🛠️ (CloudWatch Logs Insights) dio `eventos_recibidos: 1000` en la corrida de referencia, exacto a las 1000 del k6.

**Capa de control:** el panel que haría esto visualmente en vivo solo existe para local (lee Docker/Redis); para AWS, hoy lo cumple este script — adaptar `panel/infra.py` a `boto3` sigue pendiente.

### 8. ¿Qué ocurre si una instancia falla después de responder `200 OK` y antes de procesar el mensaje?

**El mensaje no se pierde: SQS lo vuelve a ofrecer a otra instancia.** *(Complementario, Probable — comportamiento documentado de SQS, no forzado a fallar en esta sesión para verlo en vivo)*

Si la instancia de `reto2-notifier` muere a medio procesar (antes de confirmar/eliminar el mensaje de SQS), el mensaje vuelve a ser visible tras 90 s y otra instancia lo reintenta — es *at-least-once* nativo de SQS. Si falla 3 veces, el redrive lo manda automáticamente al DLQ.

**Evidencia parcial:** sí se validó que el código manda a la DLQ explícitamente en ≤12 s (más rápido que el redrive de 90 s × 3) — eso sí es *Seguro*, con el caso de `EMAIL_DLQ` en 2.05 s del paso 4.

### 9. ¿Cómo manejan los mensajes duplicados, los reintentos y los fallos de procesamiento?

**Tres decisiones distintas, cada una documentada:**

- **Duplicados** *(Recomendación)*: posibles por el *at-least-once* de SQS; aceptados (duplicado > pérdida), riesgo bajo con un presupuesto de 12 s.
- **Reintentos** *(Seguro)*: 2 intentos de SES en la misma invocación (≈2 s + 3 s por intento, 1 s de espera, ≤12 s total), con `max_attempts=1` en boto3 para que no haya reintentos ocultos del SDK.
- **Fallos** *(Seguro)*: si se agotan los 2 intentos, el código manda a la DLQ directamente y registra `EMAIL_DLQ` con el motivo.

**Evidencia:** caso real del paso 4 — `EMAIL_RETRY` (intento 1, error) → `EMAIL_DLQ` (2 intentos agotados) en 2.05 s total.

### 10. ¿Cómo evitan superar las 10 instancias y qué efecto tiene aumentar su número?

**Con "Simultaneidad reservada" de Lambda — el mecanismo nativo de AWS para un techo duro de ejecuciones concurrentes, no un contador que programamos.** *(Curso + Seguro)*

Reparto: **10** en `reto2-ingesta` (igualando el número de VUs del test oficial) y **2** en `reto2-notifier` (reforzado en dos capas: reservada de función + concurrencia máxima del trigger de SQS).

**Nota honesta** *(Recomendación, declarada explícitamente)*: el peor caso teórico combinado es 12, no 10 — ingesta y notifier no compiten por el mismo cupo (rutas de invocación distintas). Es una interpretación razonada del límite, no una violación oculta. Subir el número da más margen para picos, a costa de restar del pool de la cuenta y, en una lectura estrictamente literal, alejarse más de "≤10".

**Evidencia:** la corrección de 8→10 eliminó el throttling (ver pregunta 5); la config final está confirmada en consola para las dos Lambdas.

### 11. ¿Qué diferencia hay entre el tiempo de toda la carga y el tiempo del evento de emergencia?

**Son dos métricas de naturaleza distinta, aunque se midan en la misma corrida.** *(Complementario)*

El tiempo de toda la carga mide **rendimiento agregado** (throughput). El tiempo del evento `Emergency` mide **latencia de un camino crítico específico**, el único con corte de tiempo exigido por la rúbrica.

**Evidencia:** duración total de la carga ~22.5 s para 1000 peticiones a 44.7 req/s; `ms_since_received` individual entre 590 ms y 2.54 s en las distintas pruebas.

### 12. ¿Cómo demuestran los menos de 16 segundos desde el envío del `Emergency` en k6 hasta la llegada del correo?

**Hoy medimos automáticamente el tramo bajo nuestro control (recepción en ingesta → `EMAIL_SENT`); el tramo de entrega real a Gmail se confirma a mano.** *(Seguro para el primer tramo; Probable/manual para el segundo — declarado así a propósito, sin inflar la cifra)*

`medir-aws.py` 🛠️ calculó `ultima_peticion_a_ultimo_correo_s: 1.642 s` en la corrida de referencia — esto NO es literalmente "envío de k6 → correo recibido en la bandeja" (la redacción exacta de la rúbrica), sino "última petición que vio `reto2-ingesta` → `EMAIL_SENT`". El tramo final depende de un tercero (Google) y hoy se confirma con capturas del correo real, no con un número automatizado.

**Evidencia disponible:** el correo del evento `FTE-710` (`EMAIL_SENT` a las 13:15:46.323 -05:00) apareció en la lista de Gmail como recibido "1:15 p.m." — misma franja de minuto, lo que acota la entrega real a pocos segundos, no minutos, aunque no da una cifra exacta.

**Pendiente para cerrar esto del todo** *(acción concreta, no solo teoría)*: tomar el "Mostrar original" de un correo de prueba en Gmail, que trae el timestamp exacto del `Received:` de los servidores de Google, y restarlo contra el `EMAIL_SENT` de CloudWatch — eso sí daría la cifra real de punta a punta en vez de la aproximación por minuto.

### 13. ¿Cómo comparan marcas de tiempo de componentes ubicados en máquinas diferentes?

**Con timestamps ISO 8601 con zona horaria explícita, generados por el propio código — no el reloj del cliente k6.** *(Seguro)*

Todas las Lambdas y CloudWatch comparten el reloj sincronizado (NTP) de AWS, eliminando el desfase que sí tuvo el sistema local entre máquina física y VM *(documentado en `scripts/medir.py`)*. Para la máquina de k6 (aparte, en Windows), se usa un margen de tolerancia (2-5 s) al definir la ventana en CloudWatch — mismo criterio que `medir.py` ya aplicaba localmente.

**Evidencia:** ningún caso de esta sesión mostró inconsistencia de tiempos entre Lambdas al cruzar `event_id`.

### 14. ¿Qué ocurre si el envío o la entrega del correo se demora?

**Dos escenarios distintos, con dos respuestas distintas.** *(Seguro para SES; Probable/sin SLA para Gmail)*

Si SES tarda en responder: el timeout corto corta el intento y reintenta una vez más, acotando el peor caso a ≤12 s. Si lo que tarda es la **entrega** de Gmail (después de que SES ya aceptó), eso ocurre fuera de nuestro código y no cuenta en nuestras métricas.

**Evidencia:** en todas las pruebas de esta sesión, la entrega real pareció tomar segundos, no minutos (ver pregunta 12) — pero no hay un SLA garantizado por Gmail, así que esto es observación, no garantía.

### 15. ¿Dónde termina la conexión HTTPS y cómo se protegen las comunicaciones posteriores?

**El TLS termina en API Gateway; de ahí hacia adentro, IAM controla el acceso en vez de TLS punto a punto administrado por nosotros.** *(Curso + Complementario)*

API Gateway fuerza TLS 1.3 únicamente (`SecurityPolicy_TLS13_1_3_2025_09`), acceso "Estricto" con SNI obligatorio. De ahí hacia adentro (API Gateway → Lambda → SQS → SES), el tráfico viaja por la red interna de AWS, cifrada por la infraestructura del proveedor.

**Evidencia:** política de seguridad verificada en consola (paso 1); permisos IAM de cada Lambda verificados explícitamente (p. ej. el error `AccessDenied` real que se corrigió en el paso 4, que prueba que el control de acceso sí se aplica).

### 16. ¿Cuál es el principal cuello de botella y qué evidencia respalda esa conclusión?

**Hoy, ninguno bajo la carga oficial — pero sí encontramos y corregimos uno durante esta misma preparación.** *(Seguro)*

Con la configuración corregida: 1000/1000, 0% fallos, avg 119.65 ms / p95 129.09 ms. El cuello de botella real que sí apareció fue la concurrencia reservada insuficiente (8, por debajo de los 10 VUs del test).

**Evidencia:** `AWS/Lambda Throttles = 2` coincidiendo exacto con los 2 fallos observados antes de la corrección.

**Siguientes techos esperables** *(Probable, no alcanzados en esta sesión)*: la cuota de concurrencia de la cuenta (hoy 1000) o el *burst* del *stage* de API Gateway (2000), si el volumen de peticiones creciera mucho más allá de las 1000 actuales.
