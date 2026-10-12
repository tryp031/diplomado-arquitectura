# Reto 2 — Arquitectura en AWS (opción B): flujo y componentes

> **Tipo:** investigación propia (diseño en borrador). No es material oficial del curso.
> **Enunciado:** Actividad M2 — Reto 2 (sistema de alerta para flota vehicular).
> **Estado:** pendiente de confirmar el reparto de concurrencia (8 para ingesta, 2 para notifier).
> **Alcance de este documento:** describe qué hace cada servicio en el camino B, el presupuesto de
> latencia del correo y cómo se calienta la Lambda notifier. No describe la creación de recursos.

---

## 1. Flujo de un evento

```mermaid
flowchart LR
    K6["k6 (equipo de prueba)<br/>1000 peticiones en 30 s"] -->|HTTPS POST /event-notification| APIGW

    subgraph AWS["Cuenta AWS (una región)"]
        APIGW["API Gateway REST<br/>stage prod<br/>rate 15 · burst 2000"]
        APIGW -->|proxy| LI["Lambda de ingesta<br/>concurrencia reservada: 8"]

        LI -->|Position| OK200["200 accepted<br/>(no pasa por la cola)"]
        LI -->|Emergency| Q["SQS emergencias<br/>visibilidad ≥ timeout del notifier"]
        Q -->|event source · batch 1| LN["Lambda notifier<br/>concurrencia reservada: 2 · timeout 15 s"]
        LN -->|2 intentos, timeout 5 s c/u, espera 1 s (≤ 12 s)| SES["Amazon SES<br/>identidad verificada"]
        SES --> GMAIL["Cuenta Gmail personal"]
        LN -->|DLQ tras 2 intentos fallidos| DLQ["SQS DLQ<br/>alertas no enviadas"]
        Q -. "fallo no manejado (maxReceiveCount)" .-> DLQ
        WARM["EventBridge programado<br/>ping cada 5 min, solo ventana de prueba"] -.->|evento vacío, early-return| LN

        LI -. "EMERGENCY_RECEIVED · EMERGENCY_ENQUEUED" .-> CW["CloudWatch Logs"]
        LN -. "EMAIL_SENT (hora del envío) · EMAIL_RETRY · EMAIL_DLQ" .-> CW
    end
```

**Lectura del flujo:**

1. k6 envía cada evento a API Gateway por HTTPS.
2. API Gateway aplica el límite de tasa (15 r/s con burst de 2000) y reenvía a la Lambda de ingesta.
3. La Lambda de ingesta valida el evento. Si es `Position`, responde 200 y termina ahí. Si es `Emergency`, registra la hora de recepción, publica la alerta en SQS y responde 200.
4. SQS guarda la alerta hasta que la Lambda notifier la consume.
5. La Lambda notifier envía el correo a través de SES, con un presupuesto de hasta 2 intentos de 5 s cada uno y 1 s de espera entre ellos (≤ 12 s en total). Si agota los intentos, manda la alerta a la DLQ.
6. Cada paso escribe una línea JSON en CloudWatch Logs. La hora de envío del correo (`EMAIL_SENT`) es la que se compara con la hora de llegada a Gmail.
7. Mientras dura la ventana de medición o la demo, una regla de EventBridge invoca la Lambda notifier cada 5 minutos con un evento vacío, que el handler detecta y responde sin procesar nada. Así la primera alerta real no paga el arranque en frío.

---

## 2. Componentes y responsabilidades

| Componente | Qué hace en el sistema | Configuración clave | Por qué está aquí |
|---|---|---|---|
| **k6** | Genera la carga de 1000 eventos en 30 s desde el equipo de prueba. Un solo `Emergency` por corrida. | URL de API Gateway, script del profesor | Es la fuente de la carga que pide el enunciado |
| **API Gateway (REST)** | Recibe las peticiones por HTTPS, aplica el límite de tasa y reenvía a la Lambda de ingesta. | Stage `prod`, throttling rate 15 y burst 2000, sin cache ni WAF | El enunciado pide el límite de 15 r/s en API Gateway. Además entrega la URL HTTPS |
| **Lambda de ingesta** | Valida el payload. Responde 200 a `Position`. Para `Emergency`, registra la recepción, publica en SQS y responde 200. Si SQS falla, responde 503 y no confirma la alerta. | Concurrencia reservada 8, timeout de unos pocos segundos, variable `QUEUE_URL` | Responder rápido sin esperar al correo. Separa la recepción del envío |
| **SQS (cola de emergencias)** | Guarda cada alerta hasta que el notifier la procesa. Amortigua los picos. | Visibilidad mayor o igual al timeout del notifier. Redrive hacia la DLQ | Evita perder alertas si el notifier está ocupado o cae |
| **Lambda notifier** | Toma la alerta, arma el correo y lo envía con un presupuesto de reintentos acotado. Si lo agota, la manda a la DLQ. | Concurrencia reservada 2, timeout 15 s, batch size 1, 2 intentos de 5 s con 1 s de espera, SDK con retries y timeouts cortos, `MAIL_FROM`, `MAIL_TO` | Desacopla el envío del correo de la recepción, dentro de un tiempo que no saque el correo de la banda de 15 s |
| **Amazon SES** | Envía el correo a la cuenta Gmail. | Identidad de remitente verificada. En sandbox, también el destinatario | Servicio de correo nativo de AWS, con control del asunto y del cuerpo |
| **SQS DLQ (cola de mensajes fallidos)** | Guarda las alertas que no se pudieron enviar, para revisarlas. | Retención de varios días | Ninguna alerta se pierde en silencio |
| **CloudWatch Logs** | Guarda las líneas JSON de ambas Lambdas con la hora local de Colombia. | Un grupo de logs por Lambda, retención corta para controlar costo | Es la evidencia de las horas de recepción y de envío que pide la rúbrica |
| **EventBridge (regla programada)** | Calienta la Lambda notifier antes de medir o hacer la demo, para evitar el arranque en frío en la primera alerta real. | Cada 5 min, activa solo en la ventana de prueba, evento vacío que el handler detecta y descarta | Más barato y más seguro de apagar que dejar provisioned concurrency encendido por error |
| **IAM (roles)** | Da a cada Lambda solo los permisos que necesita. | Ingesta: `sqs:SendMessage`. Notifier: `sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sqs:SendMessage` (DLQ), `ses:SendRawEmail`, escritura en logs | Principio de mínimo privilegio |

---

## 3. Límites del enunciado y cómo los cumple el diseño

| Restricción del enunciado | Cómo se cumple en el camino B | Qué hay que verificar |
|---|---|---|
| ≤ 15 peticiones por segundo en API Gateway | Throttling de stage con rate 15 y burst 2000 | Que el valor predeterminado del burst en la cuenta sea el que pide el enunciado |
| ≤ 10 instancias de procesamiento simultáneas | Concurrencia reservada: 8 (ingesta) + 2 (notifier) = 10 | Que 8 alcance para ~33 req/s con ~176 ms de latencia (≈ 6 simultáneas) |
| 100 % de las peticiones procesadas | Burst de 2000 absorbe el pico. La ingesta responde en milisegundos | Que k6 reporte `checks 100 %` y `http_req_failed 0 %` |
| Correo en < 15 s | El envío corre en paralelo a la recepción. Camino feliz estimado en 2-8 s; presupuesto de reintentos acotado a ≤ 12 s en caso de falla; Lambda calentada para evitar el arranque en frío en la primera alerta | Medir `EMERGENCY_RECEIVED` → `EMAIL_SENT` en CloudWatch y la llegada a Gmail |
| Logs con hora de recepción y de envío | Dos líneas JSON con `ts` en `-05:00` | Que ambas líneas aparezcan en CloudWatch con el mismo `event_id` |

---

## 4. Riesgos y puntos abiertos

- **Cold start de la Lambda notifier.** Mitigado con el calentador programado de EventBridge (sección 6). Igual conviene medirlo, por si el calentador no alcanza a cubrir la primera alerta real.
- **SES en sandbox.** Solo envía a direcciones verificadas. Para la demo basta con verificar el Gmail personal.
- **Entrega al menos una vez.** SQS y los reintentos pueden duplicar un correo. Está documentado como costo aceptado.
- **Concurrencia 8/2.** Es una propuesta sin confirmar. Si la ingesta se queda sin instancias bajo carga, verlo en las métricas de Lambda.
- **Costo.** API Gateway, SQS, Lambda y SES se cobran por uso. CloudWatch Logs cobra por almacenamiento. Con una prueba de 30 s el costo esperado es bajo, pero conviene revisarlo en la consola de facturación. El calentador programado se apaga apenas termina la ventana de prueba, para no dejarlo facturando de más.
- **k6 del profesor.** Su script trae una URL de API Gateway de su propia cuenta. Hay que cambiarla por la del equipo antes de medir. Ver además el hallazgo de la sección 6 sobre el orden del `Emergency`.

---

## 5. Lo que no entra en el camino B

Redis, nginx, el panel de control y Mailpit existen solo en la versión local. En AWS, cada uno se reemplaza por el servicio de la tabla de la sección 2. Gmail por SMTP directo desde Lambda queda como alternativa, pero no se usa en este diseño.

---

## 6. Ajustes de latencia y hallazgos (06-07/10/2026)

### 6.1 Presupuesto de reintentos

El worker reintentaba hasta 4 veces con timeout de 8 s y esperas de 1, 2 y 4 s: ~39 s en el peor caso,
muy por encima de la banda de 15 s de la rúbrica (y rozando la de 45 s). Se acota a:

- 2 intentos, timeout de 5 s cada uno, 1 s de espera entre ellos (≤ 12 s en total antes de ir a la DLQ).
- El SDK de AWS (botocore) también reintenta por su cuenta si no se configura: hay que fijar
  `retries.max_attempts` bajo y timeouts de conexión/lectura cortos, para que no agregue tiempo oculto.
- El reintento de SQS por visibilidad (cuando la Lambda se cae a mitad del envío) queda como respaldo
  de no-pérdida, no como mecanismo de latencia: llegaría después de los 15 s de todas formas.

### 6.2 Lambda calentada

El arranque en frío (0.5-2 s) ya cabía dentro del margen del camino feliz (2-8 s estimados), pero se
agrega como margen de seguridad adicional, no como el arreglo principal del tiempo. Se usa una regla
de EventBridge que invoca la Lambda notifier cada 5 minutos con un evento vacío (el handler lo detecta
y responde sin procesar nada), activa solo durante la ventana de medición o la demo. Se prefirió sobre
provisioned concurrency porque este último se cobra por hora mientras está activo, con riesgo de
quedar encendido por olvido en una cuenta personal.

### 6.3 `medir.py` ya mide lo que pide la rúbrica

Se revisó `scripts/medir.py` del proyecto local: `ultima_peticion_a_ultimo_correo_s` toma la **última
petición vista por nginx en toda la corrida** (no la petición puntual del `Emergency`) y la resta contra
el último `EMAIL_SENT`. Coincide con el texto de la rúbrica («el último envío realizado en el k6» hasta
«la hora de envío del correo»). Si una corrida genera más de un `Emergency`, toma el envío más tardío de
todos; vale la pena dejarlo explícito en la documentación del entregable, porque el enunciado habla de
«el correo» en singular.

### 6.4 El k6 del profesor no garantiza que el `Emergency` sea el último mensaje

El script calcula `globalIndex = (__VU - 1) * (iterations / vus) + __ITER` asumiendo que cada VU corre
un rango fijo de 100 iteraciones. Pero con las opciones dadas (`vus: 10, iterations: 1000, duration: '30s'`)
k6 usa el ejecutor `shared-iterations`: las 1000 iteraciones se reparten desde un fondo común, y `__ITER`
cuenta las iteraciones propias de cada VU, no una posición global. En la práctica, el `Emergency` solo
puede salir de la VU 10 cuando llega a su propia iteración 99 o más, así que una corrida puede terminar
con 0 `Emergency` (si el fondo se agota antes), con 1, o con varios (si a esa VU le tocan más de 100
iteraciones), y cuando aparece no coincide necesariamente con la última petición HTTP del test completo,
porque las otras 9 VUs siguen enviando `Position` en paralelo. Esto coincide con lo medido en tres
corridas del 06/10 (1, 2 y 1 `Emergency`). No es un defecto de la arquitectura del equipo: es un defecto
del script del profesor, y conviene dejarlo anotado como riesgo externo en la documentación del
entregable, junto con el hecho de que `medir.py` (6.3) ya está preparado para medir correctamente aunque
la cantidad de `Emergency` varíe entre corridas.

---

## 7. El panel (frontend) frente a la nube (backend)

API Gateway es la puerta de un **backend**: recibe `POST /event-notification` y lo reenvía a la Lambda
de ingesta. No está pensado para servir una página HTML interactiva, aunque técnicamente se podría
(integración que devuelva HTML, o proxy a un bucket S3 estático).

El **panel** (`panel/`) es un **frontend** de observación, no parte del camino que se mide:

- Vive y corre en la máquina local, no se despliega en AWS.
- No pasa por API Gateway en ningún momento.
- Para la opción B, `panel/infra.py` deja de leer Redis y el socket de Docker, y pasa a leer AWS con
  `boto3`: `logs:FilterLogEvents` (CloudWatch) para los eventos, `sqs:GetQueueAttributes` para el estado
  de la cola. Las acciones de apagar/prender contenedores no tienen equivalente directo y se retiran.
- Las credenciales de AWS que usa viven en la máquina donde corre el panel (no en el navegador de quien
  lo mira). El rol/usuario IAM del panel debe ser de solo lectura.
- Para la demo sincrónica, lo esperable es compartir pantalla (el profesor ve tu `localhost:8090`, sin
  tráfico de red entre máquinas). Si hiciera falta que alguien lo abra desde otra máquina, un túnel
  (`ngrok`, Cloudflare Tunnel) con autenticación básica; nunca exponer el puerto sin autenticación.
- Pendiente de implementar: el cambio de `panel/infra.py` y `panel/agregador.py` de Docker/Redis a
  `boto3`/CloudWatch. Se hace cuando el stack de AWS ya esté desplegado (sección 8, paso 3 en adelante),
  porque antes no hay nada real que leer.

---

## 8. Evidencia de latencia por región (08/10/2026)

**Metodología.** Un primer intento con `curl` (una sola petición por región) resultó engañoso: usaba
el hostname genérico `execute-api.<región>.amazonaws.com`, que no existe sin el id de una API real
delante, así que las primeras mediciones fallaban por un motivo distinto al que se pensó en su momento
(no era bloqueo de DNS ni de la red). Se corrigió probando contra un endpoint real que sí existe en toda
región sin crear nada (`sts.<región>.amazonaws.com`), primero con una sola petición por región, y
después con una prueba de verdad: **k6 con la misma concurrencia del script del profesor** (10 VUs, 100
iteraciones), que es la que importa porque es como va a llegar el tráfico real. El script está en
`pruebas-region/latencia.js`, junto a este documento.

**Resultado (ms, de `http_req_duration`, 100 iteraciones por región):**

| Región | avg | mediana | p90 | p95 | máx |
|---|---|---|---|---|---|
| us-east-1 | 222.8 | 129.0 | 534.7 | 543.1 | 589.8 |
| **us-east-2** | **186.4** | **111.9** | **434.6** | 534.6 | 572.2 |
| us-west-2 | 215.5 | 176.3 | 461.2 | 537.5 | 590.3 |
| sa-east-1 | 201.4 | 139.5 | 402.0 | 465.0 | 844.7 (pico aislado) |

**Decisión: `us-east-2`.** Gana en promedio, mediana y p90; `sa-east-1` gana por poco en p95 pero tiene
el peor máximo de las cuatro (un pico aislado, no representativo). Es además la misma región que usa el
profesor en su script oficial, una variable menos de la que preocuparse.

**Por qué importó repetir la prueba:** la primera medición (una sola petición por región, hecha con
`curl` el 07/10) había dado a `us-east-1` como la mejor. Con 100 muestras concurrentes por región, la
conclusión se invirtió por completo: `us-east-1` termina siendo la peor de las cuatro. Una sola muestra
no alcanza para decidir esto.

**Nota técnica, sin efecto en la comparación:** cada corrida de 100 iteraciones registró 300 peticiones
HTTP (`http_reqs`), exactamente 3 por iteración y por igual en las cuatro regiones. STS sin credenciales
responde con una cadena de un par de redirecciones antes del error final; como ocurre igual en las
cuatro regiones, no distorsiona cuál es más rápida, pero se deja anotado por si alguien repite la prueba
y le extraña el número.

**Lo que esta prueba no mide:** es tráfico hacia STS, no hacia el API Gateway real (que todavía no
existe). Sirve para decidir la región antes de desplegar nada; la medición que de verdad cuenta para la
rúbrica es la del paso 5 de la sección 9, contra el sistema completo ya desplegado en `us-east-2`.

---

## 9. Estado y próximos pasos (08/10/2026)

**Decidido:**
- Camino B (API Gateway → Lambda ingesta → SQS → Lambda notifier → SES), en vez del A (ECS Fargate).
- Región: **`us-east-2`**, con evidencia medida en la sección 8. Todos los recursos (API Gateway, las
  dos Lambdas, SQS, SQS DLQ, SES, CloudWatch, EventBridge) van en esa misma región — mezclar regiones
  solo agrega latencia cruzada y complica la identidad de SES, que es por región.
- Presupuesto de reintentos acotado a ≤ 12 s (sección 6.1) y calentador programado de la Lambda notifier
  (sección 6.2).
- El panel sigue siendo local y pasa a leer AWS en vez de Docker (sección 7), cuando corresponda.
- Todo el trabajo de este diseño queda en `E:\Diplomado Arq. Software\Módulo 2\` (este archivo y la
  carpeta `pruebas-region\`). El repositorio del equipo (`diplomado-arquitectura`, carpeta
  `Modulo 2\Ejercicios\Reto2-Alerta-Flota\`) no se ha tocado: ni el código de los adaptadores SQS/SES ni
  las Lambdas existen todavía ahí.

**Pendiente de confirmar:**
- El reparto de concurrencia reservada 8 (ingesta) / 2 (notifier) — ver sección 3.
- Si la demo será por pantalla compartida o si alguien más necesita abrir el panel desde otra máquina
  (cambia si hace falta el túnel de la sección 7).

**Siguiente paso acordado — desplegar y probar de a un componente, todo en `us-east-2`, en este orden:**

1. ✅ **API Gateway solo** (sin Lambda detrás) — **completado el 08/10/2026.**
2. ✅ **Lambda de ingesta + su conexión con API Gateway** — **completado el 09/10/2026.**
3. ✅ **SQS** — **completado el 09/10/2026.**
4. ✅ **Lambda notifier + SES** — **completado el 11/10/2026.** Código, trigger, reintentos, DLQ y el
   envío real del correo, todo validado de punta a punta.
5. **Todo junto con el k6 del profesor**: la prueba de carga completa y una medición adaptada de
   `medir.py` a CloudWatch.

### Paso 1 — API Gateway (completado 08/10/2026)

- API REST `reto2-alerta-flota` (id `ofuhehmw59`), región `us-east-2`, endpoint type Regional, IPv4,
  modo de acceso Estricto (SNI obligatorio), política de seguridad `SecurityPolicy_TLS13_1_3_2025_09`.
- Recurso `/event-notification`, método `POST`, integración **Mock** (sin Lambda todavía), responde
  `200` con `{"status": "mock"}`.
- Stage `prod` desplegado. Throttling del stage: **Tasa 15, Ampliación (burst) 2000** — igual a la
  imagen del enunciado.
- URL: `https://ofuhehmw59.execute-api.us-east-2.amazonaws.com/prod/event-notification`.
- **Validado con el patrón de carga real** (`pruebas-region/prueba-carga-profesor.js`, copia del k6 del
  profesor con solo la URL cambiada): 1000/1000 peticiones, `checks_succeeded 100%`,
  `http_req_failed 0%`, 0 respuestas `429`, a ~45 req/s. El burst de 2000 absorbe la ráfaga sin
  problema, igual que predice la sección 10.4 del informe de latencia del Reto 1 sobre bursts vs. rate.

**Hallazgo, sin impacto en el resultado:** `curl.exe` (el que trae Windows 10 de fábrica, con el motor
Schannel) no completa el handshake TLS contra este endpoint — error `(35) Recv failure: Connection was
reset` — porque la política de seguridad exige TLS 1.3 únicamente y Schannel en esta build de Windows 10
(`10.0.19045`) no lo soporta de forma confiable. El navegador y **k6** sí conectan sin problema (k6 trae
su propio TLS en Go, independiente del sistema operativo). Como la herramienta real para medir es k6, no
`curl`, esto no bloquea nada — queda anotado por si alguien más del equipo se topa con el mismo error al
probar algo suelto con `curl` desde Windows.

### Paso 2 — Lambda de ingesta (completado 09/10/2026)

- Función `reto2-ingesta`, región `us-east-2`, runtime Python 3.14, rol de ejecución básico generado
  por la consola (solo permisos de CloudWatch Logs; falta agregar `sqs:SendMessage` en el paso 3).
- Código en `lambda/ingesta.py` (junto a este documento) — **reimplementación de la misma lógica** del
  sistema local (`domain.py` + `ingest_app.py`: solo `type` obligatorio, placa ausente → `DESCONOCIDA`,
  `Emergency` sin distinguir mayúsculas, mismos nombres de evento de log), **no el mismo código fuente**:
  el local depende de FastAPI y del paquete `alerta`, que no se empaquetaron para Lambda. Si más
  adelante se quiere reutilizar el código literal (no solo la lógica), habría que subir esos módulos en
  un `.zip` o una Lambda Layer — quedó descartado por ahora, no estaba en el plan.
- Integración del método `POST /event-notification` cambiada de Mock a **Lambda Function**, con
  **integración de proxy de Lambda** activada (modo de transferencia: almacenamiento en búfer, timeout
  29000 ms). Redeploy del stage `prod` después del cambio.
- **Validado con el mismo k6 del paso 1** (`prueba-carga-profesor.js`, 1000 peticiones): `999/1000`
  checks exitosos, **1 solo fallo**, exactamente el `Emergency` de esa corrida (índice ≥ 999), que
  devolvió `503` porque `QUEUE_URL` todavía no existe. Confirmado con CloudWatch Logs Insights — las dos
  líneas de ese `event_id` son `EMERGENCY_RECEIVED` seguida de `EMERGENCY_ENQUEUE_FAILED` con el error
  `RuntimeError: QUEUE_URL no configurada todavía`. Es el camino de error diseñado a propósito
  (sección 5 del diseño local: "preferimos un error visible a confirmar una alerta perdida"), no un
  defecto.
- Latencia observada con Lambda real (vs. Mock del paso 1): avg 128 ms, p95 135 ms, máx 917 ms — algo
  más alta que con el Mock (116 ms avg), razonable por la ejecución real de la función.

### Paso 3 — SQS (completado 09/10/2026)

- **Cola principal `reto2-emergencias`** (Estándar, no FIFO — el diseño tolera duplicados a propósito,
  ver nota más abajo): tiempo de visibilidad `90` s (6× el timeout de 15 s que se le va a poner a la
  Lambda notifier). Redrive policy hacia la DLQ con `maxReceiveCount = 3`.
- **DLQ `reto2-emergencias-dlq`** (Estándar, configuración por defecto).
- Permiso agregado al rol de ejecución de `reto2-ingesta`: política en línea `reto2-ingesta-sqs-send`
  con `sqs:SendMessage` sobre `arn:aws:sqs:us-east-2:074928163617:reto2-emergencias`.
- Variable de entorno `QUEUE_URL` agregada a `reto2-ingesta` con la URL de la cola principal.
- **Hallazgo metodológico, importante para no repetirlo:** una corrida del k6 del profesor que dio
  `checks_succeeded 100%` **no demostró que el camino `Emergency` funcionara** — esa corrida
  simplemente no generó ningún `Emergency` (posible según la sección 6.4: el reparto de iteraciones de
  `shared-iterations` no garantiza que se genere ninguno). El 100% de éxito solo reflejaba que las
  1000 peticiones eran `Position`. Por eso, para validar el camino `Emergency` no se usó el script del
  profesor (no es determinístico), sino una prueba dedicada de una sola petición
  (`pruebas-region/prueba-emergency.js`).
- **Validado con esa prueba determinística:** `status=200`, `event_id` devuelto coincide con las líneas
  de CloudWatch Logs Insights `EMERGENCY_RECEIVED` → `EMERGENCY_ENQUEUED` (sin fallo). Confirmado además
  en la consola de SQS: `reto2-emergencias` quedó con **1 mensaje disponible, 0 en tránsito**, y la DLQ
  en **0** — nadie ha consumido ni fallado nada todavía, que es el estado esperado antes del paso 4.

### Paso 4 — Lambda notifier + SES (completado, 09/10 → 11/10/2026)

- Función `reto2-notifier`, región `us-east-2`, runtime Python 3.14, timeout `15 s` (el valor decidido
  en la sección 6.1). Código en `lambda/notifier.py`, misma salvedad que `ingesta.py`: reimplementación
  de la lógica del `SmtpNotifier`/`NotifierWorker` locales, no el mismo archivo.
- Variables de entorno: `MAIL_FROM` y `MAIL_TO` = `ingcamilocespedes@gmail.com`, `DLQ_URL` apuntando a
  `reto2-emergencias-dlq`. **Cambio de identidad (11/10):** el correo original, `notificadore
  mergenciaflotas@gmail.com`, resultó **inhabilitado permanentemente por Google** (desde el 08/10, por
  sospecha de creación/uso tipo bot — ajeno a este proyecto, detectado al intentar entrar a verificar la
  identidad en SES). Se reemplazó por `ingcamilocespedes@gmail.com` como remitente y destinatario
  oficiales: se verificó esa identidad en SES y se actualizó el `Resource` de la política IAM
  correspondiente al nuevo ARN.
- Presupuesto de reintentos implementado tal cual la sección 6.1: 2 intentos, cliente de `boto3` con
  `connect_timeout=2, read_timeout=3` y `retries={"max_attempts": 1}` (para que el SDK no agregue
  reintentos ocultos), 1 s de espera entre intentos. Si agota los 2, manda la alerta a la DLQ a mano
  (`sqs.send_message`) y termina sin error, para que SQS borre el mensaje original de la cola principal.
- Trigger de SQS (`reto2-emergencias`, batch size 1) agregado. **Corrección a lo documentado antes:**
  el asistente de la consola para agregar el trigger **no** agrega automáticamente los permisos de
  `sqs:ReceiveMessage`/`DeleteMessage`/`GetQueueAttributes` al rol — hubo que agregarlos a mano, junto
  con `ses:SendRawEmail` (sobre la identidad verificada) y `sqs:SendMessage` sobre la DLQ, los tres en
  una sola política en línea (`reto2-notifier-sqs-ses`).
- **Primera validación (09/10), antes de verificar SES:** el mensaje de prueba que llevaba desde el
  paso 3 esperando en `reto2-emergencias` fue consumido apenas se activó el trigger. El log mostró
  `EMAIL_RETRY` (intento 1, error de SES por identidad no verificada) y `EMAIL_DLQ` (2 intentos
  agotados), con el mismo `event_id` de la prueba. Duración total: **2.05 s**, bien dentro del
  presupuesto de 12 s y del timeout de 15 s. Confirmado también en SQS: `reto2-emergencias` a 0
  mensajes, `reto2-emergencias-dlq` a 1.
- **Validación final con envío real (11/10), con `prueba-emergency.js`:** `EMAIL_SENT` confirmado en
  CloudWatch — `{"event": "EMAIL_SENT", "attempt": 1, "ms_since_received": 1660}`. **1.66 s** desde que
  `reto2-ingesta` recibió el Emergency hasta que SES confirmó el envío (con arranque en frío: `Init
  Duration: 529.97 ms`), muy por debajo del presupuesto de 12 s — nunca hizo falta el segundo intento.
  El correo llegó de verdad a la bandeja de `ingcamilocespedes@gmail.com`, **pero cayó en spam**: Gmail
  lo etiquetó "a través de amazonses.com, firmado por amazonses.com" en vez de por `gmail.com` — es
  exactamente la desalineación DMARC anotada como riesgo conocido (no hay dominio propio disponible
  para verificar con DKIM en SES y resolverlo de raíz). Se documenta como limitación conocida: el
  sistema entrega el correo, solo que no llega a la bandeja principal.
- **Nota operativa:** CloudWatch Logs Insights, con el filtro `@message like /EMAIL/` y alcance "Todos"
  los grupos de registro, no encontró estas líneas (buscó solo en 2 grupos, no en el de `reto2-notifier`
  — parece quedar con el alcance acotado a los grupos vistos recientemente, no a todos de verdad). La
  vista normal de "Eventos de registro" del log stream de la función sí las mostró sin problema. Si algo
  no aparece en Logs Insights pero la evidencia indirecta (colas, respuestas HTTP) sugiere que sí pasó,
  conviene revisar el log stream crudo antes de concluir que algo falló.
- **Hallazgo sobre la cuota de la cuenta (09/10):** la cuenta de AWS tenía la cuota de "Concurrent
  executions" reducida a `10` (el valor por defecto de AWS es `1000` — es una cuenta nueva). Lambda
  exige dejar siempre al menos 100 ejecuciones sin reservar a nivel de cuenta, así que con un total de
  10 no se podía usar "concurrencia reservada" en ninguna función hasta que AWS aprobara un aumento
  (pedido el 09/10, al mínimo que deja pedir la consola: `1000`).
- **Solución parcial mientras se aprobaba:** en el propio desencadenador de SQS de `reto2-notifier` se
  configuró "Concurrencia máxima: 2" — un límite del origen de eventos, no de la cuota de cuenta, sin el
  piso de 100.
- **Resuelto (11/10): la cuota ya fue aprobada** en `1000`. Se configuró "Simultaneidad reservada: 8"
  en `reto2-ingesta` y "Simultaneidad reservada: 2" en `reto2-notifier`, sin error. El reparto 8/2
  diseñado desde el principio (= 10, el límite del enunciado) quedó completo, con el tope de `reto2-
  notifier` reforzado en dos capas (la reservada de función y la concurrencia máxima del trigger).
- **Corrección del reparto (11/10, hallazgo del paso 5):** con la reservada de `reto2-ingesta` en 8, el
  k6 del profesor (10 VUs) empezó a fallar 2 de cada 1000 peticiones por **throttling de Lambda**
  (`AWS/Lambda Throttles = 2`, coincidiendo exacto con los 2 fallos). La causa: cada VU manda una
  petición a la vez, así que el techo real de peticiones simultáneas que puede generar el test es
  igual al número de VUs (10) — con solo 8 reservados, cualquier instante en que los 10 VUs tengan una
  petición en vuelo agota el cupo. `reto2-notifier` no compite por ese mismo cupo (lo invoca SQS en una
  ruta aparte, async), así que subir su reservada no habría ayudado en nada y solo habría alejado más el
  sistema del límite de "≤10 instancias". **Se corrigió a "Simultaneidad reservada: 10" en
  `reto2-ingesta`**, igualando el número de VUs del test — es el techo exacto, no un margen arbitrario.
  `reto2-notifier` se dejó igual (reservada 2 + concurrencia máxima 2 del trigger), porque no hay carga
  real que justifique subirla. Nota de diseño para la exposición: si el límite de concurrencia fuera más
  estricto que el número de VUs del test, la solución correcta sería desacoplar con una integración
  directa de API Gateway a SQS (sin Lambda en el camino síncrono) — se documenta la idea, no se
  implementa, porque hoy el límite (10) coincide con la carga real que se prueba (evitar
  sobreingeniería).
- **Calentador creado (09/10/2026):** `reto2-calentador-notifier`, con **EventBridge Scheduler** (el
  servicio nuevo, no una regla clásica de EventBridge) — `rate(5 minutes)`, destino `reto2-notifier` vía
  `AWS Lambda Invoke`, sin carga personalizada (el código ya trata un evento sin `Records` como no-op:
  no hizo falta tocarlo). Rol de ejecución generado automáticamente por el asistente, limitado a invocar
  solo esa función. **Desactivado** desde el 09/10/2026 (ya se probó que funciona); volver a activarlo
  justo antes de medir o de la demo, y apagarlo otra vez al terminar.
- **Pendiente, cosmético:** quedan `MAIL_FROM_1`/`MAIL_TO_1` en el entorno de `reto2-notifier` como
  respaldo del correo inhabilitado — ya sin uso, se pueden borrar cuando se edite el entorno por otra
  razón.

**Cambios de identidad de correo (11/10):** `notificadoremergenciaflotas@gmail.com` resultó
**inhabilitada permanentemente por Google** (ver nota en el paso 4). Se probaron, en orden:
`ingcamilocespedes@gmail.com` (personal — funcionó, pero se descartó como oficial por no querer
mezclar una cuenta personal con el proyecto) y `grupo2arquitecturasoftware@proton.me` (identidad del
equipo — SES la aceptó para enviar, pero **no se pudo confirmar ninguna entrega real**, ni a bandeja ni
a spam, ni rebote registrado en la lista de supresión de SES; se sospecha rechazo silencioso por el
DMARC estricto de Proton, ni agregar `us-east-2.amazonses.com` a la lista de permitidos de Proton lo
resolvió). **Correo oficial adoptado: `grupo2arquitecturasoftware@gmail.com`** — identidad del equipo,
no personal, con entrega real confirmada repetidas veces (cae en spam, mismo patrón DMARC ya conocido,
pero entrega sin duda).

### Paso 5 — Carga completa del profesor (completado, 11/10/2026)

- **Corrida con `prueba-carga-profesor.js`** (copia exacta del k6 oficial, solo con la URL cambiada),
  contra el sistema completo ya con la corrección de concurrencia (10 en `reto2-ingesta`):
  **1000/1000 `checks_succeeded`, 0% fallos**, `http_req_duration` avg 119.65 ms / p95 129.09 ms.
- El único `Emergency` que generó esa corrida (placa `FTE-710`, `event_id bd1e0a2c-b00b-4e8a-bafa-
  44c4a88ee83c`) se encoló, se procesó y el correo llegó de verdad a `grupo2arquitecturasoftware@
  gmail.com` (spam), confirmando el camino completo de punta a punta bajo la carga oficial, no solo con
  la prueba determinística de un solo evento.
- **Nota:** esta corrida se hizo con el calentador (`reto2-calentador-notifier`) todavía **desactivado**
  — el resultado ya es válido igual, el arranque en frío de `reto2-notifier` (si lo hubo) quedó muy por
  debajo del presupuesto de 12 s en todas las pruebas anteriores. Si se quiere repetir con el calentador
  activo para la medición final de latencia que pide la rúbrica (sección 6.4, último envío de k6 →
  correo recibido), activar el schedule unos minutos antes de correr k6 y apagarlo después.
- **Pendiente, menor:** adaptar `medir.py` (o una consulta de CloudWatch Logs Insights equivalente) para
  calcular automáticamente la métrica exacta de la rúbrica (último envío de k6 → `EMAIL_SENT`), en vez
  de leerla a mano de los logs como se hizo aquí. No bloquea nada — los tiempos ya medidos (662 ms a
  1.7 s) dejan margen de sobra frente al corte de 15 s.
