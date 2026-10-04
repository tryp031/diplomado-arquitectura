# Cuaderno de estudio — Módulo 2: Requerimientos y tácticas de arquitectura

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny), con asistencia de IA |
| **Fecha** | 2026-09-30 · actualizado 2026-10-04 (gráficas; la autoevaluación pasó a su propia página) |
| **Módulo** | 2 — Requerimientos y Tácticas de Arquitectura de Software |
| **Tipo** | `apunte` — notas de estudio propias; **no es material oficial** |
| **Fuentes** | Material oficial M2 (5 decks de tácticas, 4 Genially, enunciado del Reto 2) · Bass, Clements, Kazman, *Software Architecture in Practice* 4ª ed. (citado por los decks) |
| **Límites** | La autoevaluación oficial no se abrió. Los Genially se leyeron como texto plano (sin imágenes ni orden de láminas). |
| **Estado** | vigente · ⬜ sin consolidar |

> Cada afirmación lleva su etiqueta: **[Curso]** está en el material oficial · **[Complementario]** es
> conocimiento externo al curso · **[Recomendación]** es criterio de arquitecto · **[Hipótesis]** es una
> propuesta sin validar.

---

## 1. Cómo usar este cuaderno

### Tres pasadas, no una

1. **Entender.** Lee las secciones 2 a 4 sin memorizar. Meta: explicar con tus palabras qué es un ASR y cómo pasa de requisito a táctica.
2. **Aplicar.** Haz la sección 11 (el Reto 2 como laboratorio) con lápiz. Meta: que cada concepto tenga un número del reto al lado.
3. **Comprobar.** Responde la autoevaluación interactiva (`m2-autoevaluacion-danny.html`, ver sección 12) **sin mirar**. Solo entonces abre la autoevaluación oficial.

### Qué escribir a mano

- La cadena **ASR → escenario → táctica → patrón → trade-off**, de memoria.
- Las 6 partes del escenario de calidad.
- La frase que el profesor echó de menos en M1: **«Priorizamos X, por Y, a costa de Z.»**

**[Recomendación]** El objetivo de M2 no es memorizar listas de tácticas (hay más de 60 en los decks). Es
poder, ante un requisito, decir qué atributo pesa más, qué táctica lo logra y qué se sacrifica.

---

## 2. La cadena del módulo

```text
Requisitos funcionales ─┐
                        ├─> ASR ──> Escenario de calidad ──> Táctica ──> Patrón ──> Trade-off
Requisitos de calidad ──┘   (los que condicionan        (medible)     (decisión    (paquete      (qué mejora
                             la estructura)                            concreta)   de tácticas)   y qué empeora)
```

| Eslabón | Pregunta que responde | Dónde se ve en el reto |
|---|---|---|
| ASR | ¿Qué requisito de calidad condiciona la arquitectura? | Que la alerta llegue rápido y que no se pierda ningún evento |
| Escenario | ¿Cómo se expresa de forma medible? | «Con 1000 eventos en 30 s, el correo llega en menos de 15 s» |
| Táctica | ¿Qué decisión lo logra? | Colas acotadas, concurrencia, reintento |
| Patrón | ¿Qué paquete de tácticas ya está probado? | Load balancer, circuit breaker |
| Trade-off | ¿Qué sacrifico? | Durabilidad de la cola a cambio de latencia |

**[Curso]** M1 enseñó que toda decisión es un trade-off. M2 baja un nivel: dado un atributo, qué decisiones concretas lo logran.

---

## 3. Requerimientos de calidad y ASR

### Definiciones **[Curso]**

- Los **requerimientos de calidad** (no funcionales) acompañan a los funcionales y les agregan condiciones: tiempo de respuesta, disponibilidad, confiabilidad, seguridad.
- Un **ASR** (*Architecturally Significant Requirement*) es un requisito de calidad tan crítico que **condiciona la arquitectura desde el inicio**.
- No todos los requisitos pesan igual. Los ASR deben definirse **con claridad y de forma priorizada**: algunos se descartan según el contexto, **«pero nunca deben quedar sin analizar»**.

### Cómo identificar un ASR **[Curso]**

Preguntas guía del Genially P1:

- ¿Quién es el actor y qué evento dispara la acción?
- ¿Bajo qué circunstancias ocurre: carga máxima, fallos del sistema, procesos simultáneos?
- ¿Es una acción crítica? ¿Ocurre en tiempo real o durante una transacción sensible?
- ¿Qué atributos implica (rapidez, seguridad, acceso continuo) y qué elementos de la arquitectura afecta?

### La regla de priorización del curso **[Curso]**

El ejemplo trabajado es el Reto 1 (ping → pong):

| Atributo | Dato del escenario | Prioridad | Por qué |
|---|---|---|---|
| Latencia | respuesta esperada 1 ms | **Alta** | El enunciado la especificó |
| Seguridad | sin cifrado | Baja | No se consideró; se documenta igual |
| Disponibilidad | 90 % | Baja | No se explicitó |

**Lección:** el atributo se prioriza por lo que el enunciado exige. Lo demás no se ignora: **se documenta como no priorizado**.

**[Recomendación]** Esta es la respuesta a la observación del profesor sobre M1. Una presentación debe abrir con el atributo
prioritario y derivar todo de él, no justificarlo al final.

### El método ADD (Attribute-Driven Design) **[Curso]**

| Paso | Qué se hace |
|---|---|
| 1 | Revisar las entradas: propósito, requisitos funcionales primarios, escenarios de calidad, restricciones, preocupaciones |
| 2 | Fijar el objetivo de la iteración eligiendo *drivers* |
| 3 | Elegir elementos del sistema a refinar |
| 4 | Elegir conceptos de diseño (tácticas, patrones, arquitecturas de referencia, componentes externos). **Es la decisión más difícil** |
| 5 | Instanciar elementos, asignar responsabilidades y definir interfaces |
| 6 | Diagramar las vistas y registrar las decisiones **con su justificación y los trade-offs** |
| 7 | Analizar el diseño (idealmente con otra persona) y decidir si hacen falta más iteraciones |

- Los **drivers** son los ASR más la funcionalidad, las restricciones, las preocupaciones y el propósito del diseño.
- Criterio para detenerse: **«deje que el riesgo sea su guía»**. Las iteraciones terminan cuando el diseño es «suficientemente bueno» para los drivers críticos.

---

## 4. El escenario de calidad

### Las 6 partes **[Curso]**

| Parte | Pregunta | Ejemplo (deck de Desempeño) |
|---|---|---|
| Fuente | ¿Quién o qué origina el estímulo? | 500 usuarios |
| Estímulo | ¿Qué llega? | 2000 solicitudes en 30 s |
| Artefacto | ¿Qué parte del sistema? | el sistema completo |
| Entorno | ¿En qué estado está? | condiciones normales |
| Respuesta | ¿Qué hace el sistema? | procesa todas las solicitudes |
| Medida de respuesta | ¿Cómo se verifica? | latencia promedio de 2 s |

- El Genially P1 usa otros nombres para lo mismo: *Actor, Estímulo, Ambiente, Artefacto, Respuesta esperada*, más *Unidad* y *Prioridad*. **[Recomendación]** Elige un solo vocabulario en el entregable.
- **Tres estados de operación [Curso]:** *normal*, *estrés o alta carga* (el sistema opera a su máxima capacidad) y *operación mínima* (estado degradado, solo lo vital).

### Un escenario útil pide percentil **[Complementario]**

El ejemplo del deck usa «latencia promedio». En M1 se comprobó que el promedio esconde la cola. Un escenario bien hecho especifica **percentil y condiciones de carga**: «p95 < 15 s con 35 req/s».

### Plantilla para copiar

| Parte | Tu escenario |
|---|---|
| Fuente | |
| Estímulo | |
| Artefacto | |
| Entorno | |
| Respuesta | |
| Medida de respuesta (con percentil) | |

---

## 5. Disponibilidad

### Defecto, error, falla **[Curso]**

| Término | Significado | Ejemplo |
|---|---|---|
| **Defecto** (*fault*) | La causa | Un disco con sectores dañados |
| **Error** | Estado intermedio entre defecto y falla | El sistema lee datos corruptos pero sigue respondiendo |
| **Falla** (*failure*) | Desviación de la especificación, **visible desde fuera** | El usuario no puede guardar su pedido |

La disponibilidad es la capacidad de **enmascarar o reparar defectos para que no se conviertan en fallas**, de modo que el tiempo
de interrupción acumulado no supere un valor requerido en un intervalo dado. Los defectos se pueden prevenir, tolerar, eliminar o pronosticar.

### Cuánto es «un nueve» **[Complementario]**

| Disponibilidad | Indisponibilidad por año |
|---|---|
| 99 % | ≈ 3,65 días |
| 99,9 % | ≈ 8,8 horas |
| 99,99 % | ≈ 52,6 minutos |
| 99,999 % | ≈ 5,3 minutos |

El deck dice que «alta disponibilidad» suele ser 99,999 % o más. **[Recomendación]** Antes de dar el número, define **qué cuenta
como tiempo de inactividad**: los decks excluyen el mantenimiento programado, pero para el usuario sigue sin estar disponible.

### Relación con otros atributos **[Curso]**

- **Con seguridad:** un ataque de denegación de servicio busca precisamente que el sistema no esté disponible.
- **Con desempeño:** es difícil distinguir un sistema caído de uno extremadamente lento.

### Tácticas **[Curso]** — tres propósitos: detectar, recuperar, prevenir

| Familia | Tácticas |
|---|---|
| **Detectar fallas** | Monitor · Ping/Echo · Heartbeat · Timestamp · Condition monitoring · Sanity checking · Voting · Exception detection · Self-test |
| **Recuperar: preparación y reparación** | Redundant spare · Rollback · Exception handling · Software upgrade · **Retry** · Graceful degradation |
| **Recuperar: reintroducción** | Shadow · Nonstop forwarding |
| **Prevenir** | Removal from service · Transactions · Predictive model · Exception prevention · Increase competence set |

**Patrones [Curso]:** *hot spare* (redundancia activa), *warm spare* (pasiva), *cold spare*, **TMR** (tres réplicas que votan) y **Circuit breaker**.
El costo de cualquier repuesto redundante es el costo de tener recursos duplicados.

**[Complementario]** *Retry* sin *circuit breaker* puede empeorar una caída: cada cliente reintenta y multiplica la carga sobre el servicio que ya está débil.

---

## 6. Desempeño

### Se trata del tiempo **[Curso]**

«*It's about time*»: es la capacidad de cumplir requisitos de tiempo. Órdenes de magnitud del deck:

| Operación | Tiempo |
|---|---|
| Cálculo | miles de nanosegundos |
| Red dentro de un mismo centro de datos | cientos de microsegundos |
| Red intercontinental | más de 100 ms |
| Acceso a disco | decenas de milisegundos |

**Concurrencia:** ocurre cada vez que el sistema crea un subproceso o corre en más de un procesador. Es de los conceptos que más debe entender un arquitecto.

### Por qué tarda una respuesta **[Curso]**

Procesamiento y uso de recursos · bloqueo por contención de recursos · dependencia de otros cálculos.

### Tácticas **[Curso]** — dos grandes familias

| Familia | Tácticas |
|---|---|
| **Controlar la demanda** | Gestionar solicitudes de trabajo · Limitar la respuesta al evento · **Priorizar eventos** · Reducir la sobrecarga computacional · Tiempos de ejecución acotados · Aumentar la eficiencia de los recursos |
| **Gestionar recursos** | Aumentar recursos · **Introducir concurrencia** · Múltiples copias de cómputo · Múltiples copias de datos (caché) · **Colas de tamaño limitado** · Programar recursos |

**Patrones [Curso]:** Service mesh · Load balancer · Map-Reduce. El deck también trae una lámina de tipos de pruebas (sin texto en lo capturado).

### La cuenta que hay que saber hacer **[Complementario]**

**Ley de Little:** `concurrencia ≈ llegadas por segundo × duración de cada una`. Con 35,7 req/s (el k6 de referencia) y 0,176 s por petición se necesitan ≈ 6 en paralelo. Con 0,5 s por petición son ≈ 18.
Esa aritmética decide si un límite de 10 instancias alcanza.

![Ley de Little con 35,7 req/s: el límite de 10 instancias se cruza cuando cada petición dura más de 0,28 s. Modelo de cálculo, no medición.](graficas/ley-little.svg)

| Duración por petición | Instancias simultáneas | ¿Cabe en 10? |
|---|---|---|
| 0,176 s (k6 de referencia) | ≈ 6,3 | Sí |
| 0,28 s (corte) | 10 | Justo |
| 0,5 s (si el handler espera el correo) | ≈ 17,8 | No |

**Lectura:** el límite de 10 instancias no limita *cuántas* peticiones atiendes, sino *cuánto puede durar*
cada una. Todo lo lento (el correo) tiene que salir del camino que responde al cliente.

---

## 7. Seguridad

Fuentes: el deck de Seguridad y el video obligatorio (`Material-Clase/Video-Seguridad.md`, capturado el 04/10).

### Definición y las tres características **[Curso]**

Capacidad de proteger datos e información del acceso no autorizado, sin negarlo a quien sí está autorizado. Se caracteriza por
**Confidencialidad, Integridad y Disponibilidad**. El módulo también cubre privacidad y regulaciones como GDPR para información de identificación personal (PII).

Los tres pilares, con los ejemplos del video **[Curso]**:

| Pilar | Qué protege | Ejemplo del video |
|---|---|---|
| **Confidencialidad** | Que nadie no autorizado **lea** la información | Un pirata no accede a tu declaración de impuestos |
| **Integridad** | Que nadie no autorizado **altere** la información | La nota que puso el profesor no cambia hasta que la ves |
| **Disponibilidad** | Que el usuario legítimo **pueda usar** el sistema | La tienda de libros no se cae por un ataque |

**Privacidad [Curso]:** limitar quién accede a la **PII**, que según el NIST es cualquier dato que identifique a una
persona (nombre, número de seguro social, fecha de nacimiento, información médica, educativa o financiera).

### El escenario de seguridad del video **[Curso]**

Es el único escenario de seguridad completo del material de M2. Desglosado en las 6 partes:

| Parte | Valor |
|---|---|
| Fuente | Un empleado descontento, desde una ubicación remota |
| Estímulo | Intenta modificar la tabla de tasas de pago |
| Artefacto | Los datos del sistema (la tabla de tasas) |
| Entorno | Operación normal |
| Respuesta | Se detecta el intento y el sistema registra la actividad |
| Medida de respuesta | Los datos correctos se restauran **en un día** |

**[Recomendación]** Fíjate en la medida: no es «evitar el ataque», sino **cuánto tarda en recuperarse**. Un
escenario de seguridad también puede medirse en tiempo.

### Tácticas **[Curso]** — la analogía del edificio físico

Un edificio seguro limita el acceso (vallas, puntos de control), detecta intrusos (insignias), disuade (guardias),
reacciona (cierre automático de puertas) y se recupera (copias fuera del sitio). Lo mismo aplica al software:

| Familia | Tácticas |
|---|---|
| **Detectar ataques** | Detectar intrusión · Detectar denegación de servicio · Verificar integridad del mensaje · Detectar anomalías en la entrega de mensajes |
| **Resistir ataques** | Identificar actores · Autenticar · Autorizar · Acceso limitado · Limitar la exposición · **Cifrar datos** · Entidades separadas · **Validar entrada** · Cambiar configuración de credenciales |
| **Reaccionar** | Revocar acceso · Restringir inicio de sesión · Informar a los actores |
| **Recuperarse** | Auditoría · No repudio |

El video llama «**identificar**» a la primera familia; el deck la llama «**detectar**». Es la misma; en los entregables usar «detectar».

**Patrones [Curso]:** Intercepting validator, Intrusion Prevention System (IPS). Lecturas: OWASP Top Ten 2021, CWE/SANS Top 25, SAST vs DAST.

**[Recomendación]** *Safety* (evitar estados peligrosos) y *security* (proteger información) son atributos distintos en Bass.
La traducción al español del deck de Disponibilidad los mezcla bajo «seguridad».

---

## 8. Interoperabilidad

### Definición **[Curso]**

Capacidad de un sistema de interactuar con otros **independientemente de sus tecnologías, lenguajes, plataformas o protocolos**.
No basta con comunicarse: **el receptor debe entender y procesar** la información.

### Tácticas **[Curso]** — tres categorías

| Categoría | Idea | Variantes |
|---|---|---|
| **Discover services** | Cómo encuentran y acceden a servicios en un entorno distribuido | Descubrimiento de servicios |
| **Orchestrate** | Cómo se coordinan varios servicios para una tarea compleja | Control **centralizado** (un orquestador) o **descentralizado** · monitoreo y gestión del flujo |
| **Tailor interface** | Cómo se adaptan las interfaces entre sistemas heterogéneos | Transformación de datos · Adaptadores · Interfaces estandarizadas |

**Ejemplo del curso:** un hospital integra gestión de pacientes, facturación, laboratorios externos y portal de citas con formato HL7.
Medidas: el sistema procesa y almacena en menos de 2 s, sin ajustes manuales y sin errores de integración.

**[Recomendación]** Este ejemplo es de salud. El diplomado tiene sesgo financiero: el mismo razonamiento aplica a integraciones bancarias.

---

## 9. Desplegabilidad y usabilidad (complementarios)

No figuran en el temario declarado; vienen como decks de Recursos complementarios. **[Recomendación]** Estudio ligero, solo lo esencial.

| Atributo | Familias | Patrones |
|---|---|---|
| **Desplegabilidad** | Gestionar el pipeline (despliegues escalonados, rollback, scripts) · Gestionar el sistema desplegado (versiones, dependencias, **feature toggle**) | Microservicios · Blue/green · Rolling · Canary · A/B |
| **Usabilidad** | Iniciativa del usuario (cancelar, deshacer, pausar) · Iniciativa del sistema (modelos de tarea, usuario, sistema) | MVC · Observer · Memento |

---

## 10. Cada táctica cuesta algo: la matriz de trade-offs

Esta tabla es la que faltó en la sustentación de M1. **[Recomendación]** Complétala tú; aquí van ejemplos resueltos.

| Decisión | Mejora | Empeora |
|---|---|---|
| Cola entre la entrada y el procesamiento | Disponibilidad (no se pierde el evento), desempeño de la ingesta | Latencia extremo a extremo; complejidad; posibles duplicados |
| Reintentos | Disponibilidad ante fallas transitorias | Carga durante una caída; latencia del peor caso |
| Redundancia activa (*hot spare*) | Disponibilidad, tiempo de recuperación | Costo |
| Caché (múltiples copias de datos) | Desempeño | Consistencia de los datos |
| Limitar tasa (*throttling*) | Protege al sistema, desempeño estable | Rechaza tráfico legítimo si el límite es bajo |
| Cifrar datos | Seguridad (confidencialidad) | Desempeño |
| Entidades separadas | Seguridad, disponibilidad (aísla fallas) | Desempeño (más saltos), operación |
| Memoria compartida en vez de red (M1) | Desempeño | Disponibilidad, seguridad, desplegabilidad |

---

## 11. El Reto 2 como laboratorio

**[Curso]** Sistema de alerta temprana para una flota vehicular: recibir 1000 eventos en 30 s, detectar `Emergency` y mandar un
correo a Gmail. Restricciones: API Gateway a 15 req/s, máximo 10 instancias simultáneas. El diseño completo y las opciones
están en `m2-analisis-apertura-danny.md` §5.

### Ejercicios para estudiar con el reto

1. **Escribe el escenario de calidad** de la latencia de la alerta con las 6 partes, y cuál es su medida.
2. **Escribe el escenario de «no perder ningún evento»**. ¿Qué atributo es y por qué tiene prioridad alta según la regla del curso?
3. **Calcula** el ritmo real del k6: 1000 peticiones en 30 s. ¿Cuánto es frente al límite de 15 req/s? ¿Qué parámetro del API Gateway lo hace posible?
4. **Aplica la ley de Little** con dos duraciones por petición (0,2 s y 0,5 s). ¿Alcanzan 10 instancias?
5. **Elige el atributo más importante** y completa la frase: «Priorizamos ___, por ___, a costa de ___.»
6. **Lista tres atributos no priorizados** y su justificación. Es lo que pide la regla del Genially P1.

### Cuánto *burst* hace falta **[Complementario]**

El API Gateway limita con un **token bucket**: el cubo empieza con *burst* fichas, cada petición gasta una
y se recarga a *rate* fichas por segundo. Si el cubo se vacía, la petición recibe **429** y se pierde el
«100 % procesadas».

![Fichas en el cubo durante la prueba k6 (35,7 req/s de llegada, rate 15). Con burst 2000 sobra; con burst 500 se vacía hacia el segundo 24. Modelo de cálculo, no medición.](graficas/token-bucket.svg)

| Burst | ¿Se vacía el cubo? | Resultado aproximado |
|---|---|---|
| 2000 (imagen del enunciado) | No: quedan ≈ 1420 fichas al terminar | 0 respuestas 429 |
| 580 | Justo al final | Mínimo para 1000 peticiones |
| 500 | Sí, a los ≈ 24,2 s | ≈ 80 respuestas 429 |

**Cuenta:** fichas disponibles = burst + 15 × 28 s. Tienen que alcanzar para 1000 → burst ≥ **580**.

**Límites del modelo, para no sobreinterpretarlo:**

- Supone llegadas constantes. El k6 real manda ráfagas, así que el cubo se vacía antes de lo calculado.
- El k6 espera cada respuesta antes de mandar la siguiente. Como un 429 responde rápido, una vez que
  empiezan los rechazos el k6 **acelera**, y habría más 429 que los ≈ 80 del modelo.
- El límite por defecto de una cuenta AWS suele ser mucho mayor (del orden de miles de burst). Es
  **Probable**, no está verificado en nuestra cuenta: hay que leer el valor real del stage antes de diseñar.

### Lo que hay que verificar antes de diseñar **[Hipótesis]**

- El valor real del *burst* del API Gateway en nuestra cuenta (el enunciado muestra 2000 pero dice «por defecto»).
- Qué proporción de los eventos del k6 son `Emergency` (el script no está disponible).
- Las cuotas de envío de correo y el tiempo de salida del *sandbox* del servicio de correo.

---

## 12. Autoevaluación

La autoevaluación vive en su propia página interactiva: **`m2-autoevaluacion-danny.html`**, en esta misma carpeta.

<a class="boton" href="m2-autoevaluacion-danny.html">Abrir la autoevaluación (29 preguntas) →</a>

- **29 preguntas en 4 niveles:** recordar, comprender, aplicar y decidir.
- **5 tipos de pregunta:** opción múltiple, verdadero o falso, cálculo, caso del Reto 2 y «encuentra el error».
- Cada respuesta explica **por qué fallan las demás opciones** y enlaza la sección de este cuaderno que conviene releer.
- Marcador por nivel, filtros (por nivel, sin responder, falladas) y respuestas guardadas en el navegador para el repaso espaciado.

**[Recomendación]** Hazla después de la sección 11, **sin mirar** el cuaderno. Abre la autoevaluación oficial de Brightspace
solo cuando los niveles 1 y 2 te salgan sin fallos: en M1 fue de **un solo intento**.

---

## 13. Glosario rápido

| Término | Definición breve |
|---|---|
| **ASR** | Requisito arquitecturalmente significativo: condiciona la estructura desde el inicio |
| **Atributo de calidad** | Propiedad medible del sistema (latencia, disponibilidad, seguridad…) |
| **Escenario de calidad** | Forma medible de un requisito: fuente, estímulo, artefacto, entorno, respuesta, medida |
| **Táctica** | Decisión de diseño que influye en un atributo |
| **Patrón** | Paquete probado de tácticas y estructura |
| **Driver** | Entrada del diseño: ASR, funcionalidad, restricciones, preocupaciones, propósito |
| **ADD** | Attribute-Driven Design: método iterativo de 7 pasos |
| **Defecto / Error / Falla** | Causa / estado intermedio / desviación visible |
| **Hot / warm / cold spare** | Repuesto activo / pasivo / apagado |
| **TMR** | Triple Modular Redundancy: tres réplicas que votan el resultado |
| **Circuit breaker** | Corta las llamadas a un servicio fallido hasta que se recupere |
| **Throttling** | Limitar la tasa de peticiones aceptadas |
| **Burst** | Tamaño del cubo de tokens: cuántas peticiones seguidas se absorben por encima de la tasa |
| **Ley de Little** | Concurrencia ≈ tasa de llegada × duración |
| **Percentil (p95)** | Valor por debajo del cual cae el 95 % de las mediciones |
| **Orquestación** | Coordinación de servicios por un componente central |
| **HL7** | Formato de intercambio de datos de salud (ejemplo del curso) |
| **Safety / Security** | Evitar estados peligrosos / proteger la información |
| **PII** | Información de identificación personal |
| **k6** | Herramienta de pruebas de carga usada en el reto |

---

## 14. Qué falta por estudiar

| Falta | Por qué importa | Cómo conseguirlo |
|---|---|---|
| **Descriptores de la rúbrica de Brightspace** | Vienen vacíos; no sabemos qué separa un 5 de un 3 | Preguntarlo en el encuentro del **06/10** |
| **Autoevaluación oficial** | Puede ser de un solo intento, como en M1 | Abrirla después de la §12 de este cuaderno, nunca antes |
| **Lecturas complementarias** (OWASP, AWS DR ×4, Fowler ×2, canary) | Profundizan las tácticas; no son obligatorias | Son públicas: se pueden resumir desde los enlaces de `Material-Clase/Modulo2-Brightspace.md` |
