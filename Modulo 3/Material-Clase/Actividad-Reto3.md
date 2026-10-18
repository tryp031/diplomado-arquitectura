# Actividad M3 — Reto 3: Diseñando Arquitecturas Resilientes

> **Tipo:** `material-oficial` (Brightspace → Módulo 3 → «Evidencia de aprendizaje: actividad M3»).
> **Fuente:** texto de la página de la actividad (instrucciones incrustadas en Brightspace), leído el 2026-10-18
> con sesión de Danny. La página de bienvenida lo llama «archivo adjunto titulado *Actividad módulo 3. Reto -
> Diseñando Arquitecturas Resilientes*», pero **no hay archivo adjunto**: el enunciado está como texto en la página.
> **Transcripción:** texto tal cual; las dos imágenes de «Resultados esperados» están en `img/` y transcritas abajo como `[imagen]`.
> **Este archivo no se edita.** Las observaciones propias van en `Aportes/`. El bloque «Lo que el enunciado NO dice»
> es anotación de Danny/IA, **no** del curso.

**Entrega en Brightspace:** carga de archivos (hasta 2 GB), «Grabar» o «Elegir opción existente». **La fecha de cierre
no aparece en la página**; según `_Base-Conocimiento/CRONOGRAMA.md` el módulo va del 21/10 al **03/11/2026**.
Al leerla: «Aún no hay envíos».

---

## Instrucciones

**Actividad: Módulo 3. Reto - Diseñando Arquitecturas Resilientes**

Estimado estudiante, a continuación, se presentan los pasos para desarrollar la actividad del Módulo 3. Lee con atención y desarrolla todos los pasos, entregando las evidencias solicitadas:

### Caso: contexto del Negocio

Eres parte del equipo de arquitectura de **Sistemas UltraSeguros S.A.**, una empresa líder que ofrece servicios críticos para múltiples clientes alrededor del mundo. Entre estos servicios, se encuentran la gestión de transacciones financieras, análisis de datos en tiempo real y monitoreo de infraestructuras críticas.

El éxito de la compañía depende de un sistema capaz de **mantenerse operativo incluso en las peores circunstancias**. En un mundo donde los picos de tráfico, errores inesperados y fallos en componentes individuales son inevitables, tus clientes confían en que la plataforma pueda **adaptarse, degradarse progresivamente y recuperarse automáticamente** sin interrupciones significativas.

La gerencia ha identificado un problema urgente: **durante los picos de tráfico**, el sistema tiende a fallar bajo carga, lo que afecta la experiencia del cliente y genera pérdidas millonarias. **¿Puedes diseñar una arquitectura que haga que el sistema reaccione a los fallos automáticamente y se recupere con inteligencia?**

### El Reto

Tu misión, como arquitecto, es diseñar y construir un sistema que cumpla con las siguientes características:

- **Degradación progresiva y recuperación automática:**
  - Si el sistema detecta fallos recurrentes o altos niveles de errores, debe degradar automáticamente sus capacidades para mantener los servicios críticos en funcionamiento.
  - Cuando los indicadores de salud regresen a niveles aceptables, el sistema debe recuperar gradualmente todas sus funcionalidades.
- **Resiliencia dinámica basada en la salud de los servicios:**
  - Los cambios en los niveles de servicio deben registrarse y ser visibles en logs o métricas.
- **Pruebas bajo carga:**
  - Se proporcionará un script de pruebas que simula picos de carga, incluyendo solicitudes que generan fallos intencionales.
  - Tu sistema debe pasar por los 3 niveles de servicio (Full, Degradado, y Operación Mínima) y recuperarse exitosamente al nivel inicial y transicionar entre los mismos.
- **Tolerancia a fallos:**
  - Durante el estado de Operación Mínima, el sistema debe seguir respondiendo cuando la petición falle con un mensaje de Error claro para los usuarios: "Nivel 3: Sistema bajo mantenimiento, intente más tarde"
  - Durante el estado de Operación Mínima, el sistema debe seguir respondiendo cuando la petición se logre resolver con un mensaje de Error claro para los usuarios: "Nivel 3: Operación al mínimo"

### Requerimientos Técnicos

Ten en cuenta los requerimientos técnicos necesarios:

- **API Gateway:** actuará como punto de entrada para todas las solicitudes y debe enrutar dinámicamente las solicitudes a diferentes niveles de servicio.
- **3 servicios diferentes por nivel de servicio:**
  - Nivel 1 (full): el sistema responde con todas sus capacidades activas.
  - Nivel 2 (degradado): funciona con un subconjunto de capacidades, priorizando los servicios esenciales.
  - Nivel 3 (mínimo): responde con un mensaje de mantenimiento.
- **Logs y métricas:** el sistema debe registrar todos los cambios de nivel y las métricas clave.

### Pruebas

Se proporcionará un **script de pruebas K6** que simula 6 minutos de solicitudes, distribuyendo las cargas y fallos intencionales. Tu solución debe:

- Pasar por los 3 niveles de servicio durante la ejecución.
- Mostrar recuperación completa al finalizar las pruebas.
- Demostrar degradación y recuperación de forma dinámica.

### Entregables

Como evidencia de la actividad, debes entregar los siguientes productos:

- **Código fuente:**
  - Archivo comprimido en formato ZIP con toda la implementación necesaria.
- **Documentación técnica:**
  Documento en formato PDF que incluya lo siguiente:
  - **Decisiones de arquitectura:** justificar por qué se eligieron los componentes y servicios utilizados.
  - **Atributo de calidad más importante:** explicar cuál es y por qué fue priorizado.
  - **Diagrama de la arquitectura:** representación visual clara de la solución.
  - **Tácticas de arquitectura:** explicar las tácticas utilizadas para cumplir con los objetivos.
- **Demostración en vivo o video (2.5 Puntos):**
  **Formato: video en MP4** (máx. 5 minutos) o enlace a YouTube según corresponda.
  - Ejecución funcional de la arquitectura bajo las condiciones simuladas por el script de pruebas.
  - Explicación clara de cómo tu solución detecta fallos, degrada el sistema y se recupera.
  - Logs y métricas que validen el comportamiento esperado.

### Restricciones

- Solo se permite usar servicios de AWS.
- No se proporcionará plantilla inicial. Debes investigar, diseñar y construir la solución desde cero.
- No puedes modificar el script de pruebas proporcionado.

### Objetivo final

Demuestra que tu solución puede **mantener el sistema en funcionamiento incluso en las peores circunstancias**. Solo las arquitecturas más resilientes e inteligentes superarán este reto.

### Detalles de las transiciones esperadas:

- **Inicio:** El sistema comienza en **Nivel 1 (Full Service)**.
- **Degradación:**
  - Si se detectan **5 errores o más**, el sistema transiciona al **Nivel 2 (Degradado)**.
  - Si se detectan **10 errores o más**, el sistema transiciona al **Nivel 3 (Mantenimiento).**
- **Recuperación:**
  - Desde **Nivel 3**, cuando los indicadores vuelven a estar en un estado saludable, el sistema transiciona a **Nivel 2**.
  - Desde **Nivel 2**, cuando los indicadores están completamente estables, el sistema regresa a **Nivel 1**.

### Resultados esperados `[imagen]`

Dos capturas de la consola de k6 (`img/reto3-resultados-esperados-1.png` y `-2.png`, 468 px de ancho, legibles ampliadas).
Formato de cada línea: `INFO[<seg>] Minute: <m>, Iteration: <n>, Error: <bool>, Status: <código>, Message: {"message":"<texto>"} source=console`.

**Imagen 1** (minutos 2 → 4, iteraciones 39 → 67):

| Iteraciones | Error | Status | Mensaje |
|---|---|---|---|
| 39–40 | false | 200 | `Nivel 1: OK` |
| 41–42 | true | 500 | `Nivel 1: Operación Full con Error` |
| 43–55 | true | 500 | `Nivel 2: Operación Limitada` |
| 56–60 | false | 200 | `Nivel 2: OK` |
| 61–67 | false | 200 | `Nivel 1: OK` |

**Imagen 2** (minutos 6 → 7, iteraciones 109 → 140):

| Iteraciones | Error | Status | Mensaje |
|---|---|---|---|
| 109–118 | false | 200 | `Nivel 2: OK` |
| 119–134 | false | 200 | `Nivel 1: OK` |
| 135 | false | 200 | `Nivel 3: OK` |
| 136 | false | 200 | `Nivel 1: OK` |
| 137–140 | false | 200 | `Nivel 3: OK` |

Última línea: `INFO[0555] Esperando 40 segundos para iniciar en el segundo 00...`

---

## Lo que el enunciado NO dice (anotación; no es del curso)

1. **El script de k6 no está adjunto en la página.** «Se proporcionará». *Actualización 18/10:* Danny lo tenía
   descargado (fecha del archivo: 13/10). Está en `k6-script-profesor-reto3.js`, sin modificar. Lo que revela está
   en «Lo que dice el script de k6», más abajo.
2. **«5 errores o más» ¿en qué ventana?** Acumulados desde el inicio, consecutivos, por minuto o por ventana
   deslizante: cada lectura da un diseño distinto. Tampoco define «indicadores saludables» (3 → 2) ni
   «completamente estables» (2 → 1) con un número.
3. **Las imágenes contradicen el texto.** En la imagen 1 el sistema pasa a Nivel 2 tras **2** errores (no 5) y no
   llega a Nivel 3 pese a **15** errores seguidos (41–55). Vuelve de 2 a 1 tras 5 éxitos. Probablemente son de una
   implementación de referencia con otros umbrales o con ventana; **no se puede usar como especificación sin
   preguntar**.
4. **Los mensajes de Nivel 1 y 2 solo están en la imagen.** El texto define solo los del Nivel 3; `Nivel 1: OK`,
   `Nivel 1: Operación Full con Error`, `Nivel 2: OK` y `Nivel 2: Operación Limitada` salen de la captura.
5. **El mensaje de Nivel 3 no coincide.** El texto pide `Nivel 3: Operación al mínimo` (éxito) y
   `Nivel 3: Sistema bajo mantenimiento, intente más tarde` (fallo); la imagen 2 muestra `Nivel 3: OK`. Además el
   texto llama «mensaje de Error» al caso de éxito.
6. **La imagen 2 muestra oscilación**: `Nivel 3 → Nivel 1 → Nivel 3` entre iteraciones consecutivas (135–137) sin
   errores visibles. Es compatible con **estado no compartido entre instancias** (cada instancia con su propio
   contador). Es exactamente el riesgo de diseño que hay que evitar con Lambdas concurrentes, o una entrada a Nivel 3
   por un criterio que el texto no explica.
7. **«3 servicios diferentes por nivel de servicio»** es ambiguo: ¿un servicio por nivel (3 en total) o tres por
   nivel (9)? La lista que sigue sugiere **uno por nivel**.
8. **La carga es baja.** En las capturas, una iteración cada ~3 s (≈ 20 peticiones/min). El reto habla de
   «picos de tráfico», pero lo que mide es **la máquina de estados ante errores**, no el throughput.
9. **Rúbrica incompleta.** Solo la demostración tiene puntaje visible (**2,5 pts**). No se dice cuánto valen el
   código y el documento. Tampoco si el envío es individual o grupal (en el M2 fue individual).
10. **Demo:** dice «en vivo **o** video MP4 (máx. 5 min) / YouTube». En el M2 la regla era: quien asiste presenta en
    vivo, quien no, entrega video. Aquí no lo distingue.
11. **«Solo AWS» es explícito** por primera vez (en el M2 estaba implícito). Un diseño local como el del Reto 2 no
    cumple por sí solo.

## Lo que dice el script de k6 (anotación; no es del curso)

Fuente: `k6-script-profesor-reto3.js` (copia byte a byte de `reto3.js`, verificada con SHA-256).

1. **El fallo lo pide el cliente.** Cada `POST` lleva `{"message", "timestamp", "error": true|false}`. El servidor
   no falla de verdad: debe **tratar `error: true` como un fallo** (las imágenes responden 500) y contarlo.
2. **Carga fija y baja:** 1 VU, **140 iteraciones**, `sleep(3)` → ≈ 20 peticiones/min. Son **7 «minutos»**, no 6 (el
   comentario dice «6 minutos × 20» pero 140 = 7 × 20). `maxDuration: 8m`.
3. **El «minuto» que imprime es por iteración** (`floor(i/20)+1`), no de reloj. Como cada iteración dura 3 s + la
   latencia, el minuto lógico se va desfasando del minuto real.
4. **Patrón de errores (35 en total):**

   | Minuto lógico | Iteraciones | Errores |
   |---|---|---|
   | 1 | 1–20 | **5** (1–5) |
   | 2 | 21–40 | 0 |
   | 3 | 41–60 | **15** (41–55) |
   | 4 | 61–80 | 0 |
   | 5 | 81–100 | **15** (81–95). El comentario dice «las primeras 10», pero el código usa `< 15` |
   | 6–7 | 101–140 | 0 |

   Si el contador fuera acumulado y sin ventana, el minuto 1 llevaría a Nivel 2 y el minuto 3 a Nivel 3, y **nunca
   se recuperaría**. Por eso los umbrales «5 / 10 errores» **solo tienen sentido con una ventana** (de tiempo o de
   N peticiones).
5. **Arranca en el segundo 00 del reloj.** Para que el reloj de k6 coincida con los minutos de reloj del servidor.
   Es un indicio (**suposición**, no confirmado) de que la solución de referencia cuenta errores **por minuto de
   reloj**, por ejemplo con métricas o alarmas de CloudWatch de período 1 min. El retraso de evaluación de esas
   alarmas explicaría por qué las imágenes cambian de nivel «tarde» y por qué aparece Nivel 3 en el minuto 7, sin
   errores.
6. **No tiene `checks` ni `thresholds`.** k6 no aprueba ni reprueba nada: el resultado se juzga **leyendo los logs**
   (como en las imágenes). Los mensajes que devuelva el servidor son, en la práctica, la evidencia.
7. **La URL apunta al API Gateway del profesor** (`…execute-api.us-east-2…/prod/service-api`). Para correrlo contra
   nuestro sistema hay que cambiar la URL; igual que en el M2, es el único cambio admisible y conviene declararlo.
8. El `console.log` de espera vive en el contexto *init*; k6 lo vuelve a ejecutar al final (por eso la imagen 2
   termina con «Esperando 40 segundos…»). No afecta la prueba.
