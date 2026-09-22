| Campo | Valor |
|---|---|
| **Módulo** | 1 — Fundamentos de la Arquitectura de Software |
| **Fecha de consolidación** | 2026-09-15 |
| **Aportes fusionados** | Material oficial Brightspace · `m1-cuadernillo-estudio-camilo.html` (Camilo) · `m1-guia-reto-latencia-camilo.html` (Camilo) · `m1-fundamentos-arquitectura-danny.html` (Danny) · `m1-clasificador-hosts-danny.html` (Danny) · mediciones del reto |
| **Estado** | vigente · ⚠️ **incompleto por falta de material oficial** (ver §1.1) |

---

# Consolidado — Módulo 1

## Resumen ejecutivo

La arquitectura de software es el conjunto de **decisiones estructurales costosas de revertir**;
todo lo demás es diseño. De ahí se derivan las dos ideas que gobiernan el módulo: **toda decisión
es un trade-off**, y **el «por qué» importa más que el «cómo»**. Un atributo de calidad que no se
puede medir no es un atributo: es un deseo.

Este consolidado fusiona cinco fuentes. **Coinciden en los conceptos y divergen en la taxonomía** —
y esa divergencia no se puede resolver con el material disponible, porque la fuente que la resolvería
(el Genially M1P5) no está descargada. Es el riesgo principal del módulo: la autoevaluación permite
**un solo intento**.

---

## 1. Inventario de fuentes

| # | Fuente | Autor | Fecha | Tipo | ¿IA? | Autoridad |
|---|---|---|---|---|---|---|
| F1 | `Material-Clase/Modulo1-ArquitecturaSoftware.md` | PUJ Cali / Diego Rozo | 08/09 | `material-oficial` | no | **máxima** |
| F2 | `Aportes/danny/m1-fundamentos-arquitectura-danny.html` | Danny | 11/09 | `apunte` | sí | media |
| F3 | `Aportes/danny/m1-clasificador-hosts-danny.html` | Danny | 14/09 | `apunte` | sí | media |
| F4 | `Aportes/camilo/m1-cuadernillo-estudio-camilo.html` | Camilo | 15/09 | `investigacion` | sí | media |
| F5 | `Aportes/camilo/m1-guia-reto-latencia-camilo.html` | Camilo | 15/09 | `investigacion` | sí | media |
| F6 | `Ejercicios/Reto-Latencia-Minima/harness/resultados/` | Danny | 08–14/09 | evidencia medida | no | **manda sobre toda estimación** |

> **F4 y F5 no son material oficial** aunque tengan el formato y el tono de un documento
> institucional. Son reelaboraciones del material de Brightspace hechas con IA.

### 1.1 ⚠️ Vacío de información — riesgo alto

El material oficial (F1) **no desarrolla el contenido conceptual**: lo delega en cuatro Genially y
un video de YouTube que son embebidos externos y **no quedaron descargados**.

| Recurso | Qué contiene | Estado |
|---|---|---|
| Genially 1 — Fundamentos | Conceptos esenciales y patrones de la industria | ⬜ no descargado |
| Genially 2 — Leyes y alcance | **La formulación exacta de las leyes** | ⬜ no descargado |
| Genially 3 — Restricciones y decisiones | Factores de diseño | ⬜ no descargado |
| Genially 4 — M1P5 Atributos de calidad | **La taxonomía completa y su clasificación** | ⬜ no descargado |
| Video YouTube `Ne396XnJ8RI` | Importancia estratégica | ⬜ no transcrito |

**Consecuencia:** las contradicciones C1 y C2 (§4) **no se pueden cerrar** sin estos recursos, y
son exactamente el tipo de pregunta que aparece en una autoevaluación de opción múltiple.
**Conseguirlos es la tarea de mayor prioridad del módulo.**

---

## 2. Conceptos principales

### 2.1 Qué es la arquitectura

`[Curso]` **No es una estructura estática**, sino «un conjunto dinámico de elementos
interrelacionados que definen cómo opera y se desarrolla un sistema de software» (F1, literal).
La palabra que hace el trabajo es *dinámico*: no se decide una vez y se archiva.

`[Complementario]` Richards y Ford (bibliografía oficial del módulo) la descomponen en **cuatro
componentes** — coinciden F2 y F4 de forma independiente:

| Componente | Qué es | Ejemplo |
|---|---|---|
| **Estructura** | El estilo arquitectónico elegido | Monolito en capas, cliente-servidor, microservicios, event-driven, microkernel |
| **Características** | Los atributos de calidad exigidos | Latencia < 1 ms · disponibilidad 99,9 % |
| **Decisiones** | Reglas **duras**, obligatorias | «Solo la capa de negocio accede a la base de datos» |
| **Principios** | **Guías** con margen de interpretación | «Preferir mensajería asíncrona cuando sea posible» |

> **Frontera examinable:** la **decisión** no admite excepción sin cambiar la arquitectura; el
> **principio** admite que un caso justificado se salga. (F2, F4 coinciden.)

`[Recomendación]` (F2) **La prueba de reversibilidad**: «¿esto es arquitectura o diseño?» no se
resuelve por tamaño ni por importancia, sino por **cuánto cuesta cambiarlo en seis meses**. Si
revertirlo obliga a tocar el despliegue, el contrato con otros equipos o el modelo de datos, es
arquitectura. Si se revierte en una tarde, es diseño.

`[Complementario]` (F4) **La analogía de la casa**: antes de construir se decide distribución,
estructura, instalaciones y posibilidades de ampliación. Cambiar un tabique es barato; mover los
cimientos, no.

### 2.2 Las leyes

`[Curso]` F1 confirma que existen «leyes fundamentales que rigen la arquitectura de software», pero
**no las enuncia** — están en el Genially 2.

`[Complementario]` F2 y F4 coinciden en la formulación de Richards y Ford:

| Enunciado | Qué implica |
|---|---|
| **Primera ley** — *Todo en arquitectura de software es un trade-off* | No existe la respuesta «mejor». Existe la apropiada para unos atributos priorizados en un contexto |
| **Corolario** — *Si crees que encontraste algo que no es un trade-off, es que todavía no lo identificaste* | Convierte «no veo la desventaja» en «me falta buscar», no en «no hay» |
| **Segunda ley** — *El «por qué» importa más que el «cómo»* | Es la justificación conceptual del **ADR**. El código dice cómo; solo el registro de la decisión dice por qué |

> ⚠️ **Verificar contra el Genially 2 antes de la autoevaluación.** El docente puede usar otra
> formulación o añadir leyes propias. Un solo intento.

### 2.3 Las tres dimensiones de su importancia

`[Curso]` F1 las nombra explícitamente en la descripción del módulo:

| Dimensión | Qué significa | Dónde se ejerció en el reto (F3) |
|---|---|---|
| **Estructuración de la complejidad** | Descomponer en partes con límites claros | Separar cliente medidor · servidor · análisis. El harness común evita que las variantes se acoplen |
| **Análisis temprano de atributos de calidad** | Evaluar rendimiento, seguridad o disponibilidad *antes* de construir | Congelar la especificación de medición **antes** de escribir las variantes |
| **Decisiones técnicas informadas** | Decidir con criterio explícito y dejar rastro | Elegir la frontera de medición del RTT y justificarla en un ADR |

`[Recomendación]` (F2) La segunda dimensión es la que más cuesta interiorizar porque contradice el
instinto de programar primero. El razonamiento es económico: el costo de cambiar una decisión
arquitectónica **no crece de forma lineal con el tiempo**.

### 2.4 Importancia estratégica

`[Curso]` (F1) La arquitectura es «el puente entre las estrategias de negocio y las soluciones
técnicas». `[Complementario]` (F4) lo concreta en una cadena:

```text
Objetivos del negocio → necesidades → decisiones arquitectónicas → estructura → calidad → evolución
```

y en una consecuencia que conviene citar: **una arquitectura adecuada reduce el costo del cambio;
una inadecuada convierte cada requisito nuevo en un proyecto.**

### 2.5 Restricciones y decisiones

`[Curso]` (F1) «Las decisiones clave definen la estructura y el comportamiento del sistema,
mientras que las restricciones actúan como límites que guían el diseño.» Tres frentes:
**negocio · tecnología · equipo y recursos**. F2, F4 y F5 coinciden.

> **Fórmula mental** (F4): *Decisión = elección. Restricción = límite que condiciona esa elección.*
> **La restricción se recibe; la decisión se elige.** Separarlas explícitamente en el PDF es la
> forma más rápida de demostrar dominio del marco (F5).

| Frente | Ejemplos (unión de F2, F4, F5) |
|---|---|
| **Negocio** | Presupuesto · plazos · time-to-market · regulación y cumplimiento · contratos con terceros · penalizaciones por indisponibilidad |
| **Tecnología** | Stack heredado · licencias · nube ya contratada · capacidad de red · límites del proveedor · versiones soportadas · compatibilidad |
| **Equipo y recursos** | Tamaño del equipo · experiencia disponible · madurez operativa · rotación · presupuesto de tiempo · infraestructura |

`[Recomendación]` (F2) **La restricción de equipo es la más subestimada y la que más proyectos
hunde.** Una arquitectura de microservicios con event sourcing es impecable sobre el papel y
catastrófica con cuatro personas sin experiencia en sistemas distribuidos. *La mejor arquitectura
teórica puede ser la peor decisión práctica* — y eso no es una concesión, es parte del análisis.

### 2.6 Responsabilidades del arquitecto

`[Complementario]` (F4, única fuente que las lista):

- Tomar decisiones arquitectónicas y **dejar registrada su justificación**.
- Analizar la arquitectura de forma **continua**, no solo al inicio.
- Mantenerse al día con las tendencias relevantes **para el contexto**.
- Velar por el cumplimiento de las decisiones adoptadas.
- Conocer el dominio del negocio para traducir necesidades en atributos de calidad.
- Ejercer comunicación, negociación y liderazgo técnico.

### 2.7 Estilos y patrones más citados

`[Complementario]` (F4):

| Estilo | A favor | En contra |
|---|---|---|
| Monolítico en capas | Simple de desarrollar y desplegar | Se vuelve rígido al crecer |
| Cliente-servidor | Separa presentación de procesamiento y datos | — |
| Microservicios | Despliegue independiente | Alto costo operativo |
| Orientado a eventos | Desacoplamiento, asincronía | Trazabilidad más difícil |
| Microkernel (plug-in) | Núcleo estable + extensiones | Útil solo en productos configurables |

### 2.8 La regla que vale más que la taxonomía

`[Recomendación]` (F2 y F4 lo dicen con distintas palabras; F5 lo operacionaliza)

> **Un atributo de calidad que no se puede medir no es un atributo de calidad: es un deseo.**

| Deseo | Atributo de calidad |
|---|---|
| «El sistema debe ser rápido» | p99.9 del RTT < 1 ms · payload 32 B · closed-loop · en loopback |
| «El sistema debe ser seguro» | Cero vulnerabilidades críticas OWASP Top 10 en SAST previo a cada despliegue |
| «El sistema debe estar disponible» | 99,95 % mensual · RTO 15 min · RPO 5 min |
| «El sistema debe ser mantenible» | Un desarrollador nuevo despliega un cambio en su primera semana |

F4 aporta la versión del módulo: en vez de «debe ser rápido», *«el 95 % de las solicitudes debe
responder en menos de 2 segundos con una carga de 500 usuarios concurrentes»*.

**Esto es directamente el trabajo del reto:** el enunciado dice «preferiblemente menor a un
milisegundo», que es un deseo a medio camino. Convertirlo en la versión de la derecha — nombrando
percentil, payload, régimen de carga y frontera de medición — **es** la actividad.

### 2.9 Diferencias que suelen confundir

`[Complementario]` (F4, aporte exclusivo suyo y muy examinable):

| Par | Cómo distinguirlos |
|---|---|
| Disponibilidad vs. rendimiento | ¿Funciona? vs. ¿qué tan rápido? Un sistema que responde en 30 s está disponible, con mal rendimiento |
| Rendimiento vs. escalabilidad | Comportamiento ante una carga concreta vs. capacidad de soportar el crecimiento de esa carga |
| Disponibilidad vs. tolerancia a fallos | ¿Está operativo? vs. ¿puede seguir operativo cuando ocurre un fallo? |
| Tolerancia a fallos vs. recuperabilidad | Sigue funcionando **durante** el fallo vs. vuelve a funcionar **después** |
| Mantenibilidad vs. modificabilidad | Comprender+corregir+modificar+probar+actualizar vs. solo introducir cambios con impacto acotado |
| Observabilidad vs. auditabilidad | Necesidad técnica (¿qué ocurre?) vs. necesidad de control (¿quién hizo qué y cuándo?) |

### 2.10 Trade-offs

`[Curso]` Primera ley. `[Complementario]` Tabla de F2:

| Al maximizar… | …se degrada | Por qué |
|---|---|---|
| **Latencia mínima** | Portabilidad · mantenibilidad · costo · simplicidad operativa | Cada nanosegundo se compra con especificidad |
| **Disponibilidad** | Consistencia · costo | Teorema CAP; la redundancia se paga |
| **Seguridad** | Rendimiento · usabilidad | Cifrado, validación y autenticación añaden trabajo y fricción |
| **Escalabilidad** | Simplicidad · consistencia · depurabilidad | Distribuir introduce red, y la red introduce fallo parcial |
| **Time-to-market** | Todo lo demás | Deuda técnica: un préstamo con intereses |

`[Complementario]` (F4) El trade-off depende del **dominio**, y esto responde a por qué no hay
arquitectura perfecta sino **adecuada a un contexto**:

| Dominio | Atributos que priman |
|---|---|
| Banca | Seguridad · disponibilidad · fiabilidad · auditabilidad |
| Videojuego en línea | Rendimiento · escalabilidad · disponibilidad |
| Sistema médico | Seguridad · disponibilidad · integridad · fiabilidad · auditabilidad |
| Herramienta interna pequeña | Simplicidad · mantenibilidad · costo |

> **Cómo responder en el examen o ante el docente** (F2): nunca «esta arquitectura es mejor». La
> forma defendible es *«priorizando **X** e **Y**, y aceptando degradar **Z**, la opción apropiada
> es **A**, porque…»*. **Nombrar lo que sacrificas no es debilidad en la respuesta: es la respuesta.**

---

## 3. Hechos, opiniones e hipótesis

| Afirmación | Tipo | Evidencia |
|---|---|---|
| El módulo clasifica los atributos en operacionales, estructurales y transversales | **Hecho** | F1, literal |
| El material cita ISO/IEC 25000 e ISO/IEC 25010 de forma inconsistente | **Hecho** | F1: «ISO/IEC 25000» en Cierre; «ISO/IEC 25010» en Conclusiones y Recursos |
| ISO/IEC 25010:2011 tiene 8 características | **Hecho** | ISO, citado en los propios recursos de F1 |
| ISO/IEC 25010 fue revisada en 2023 y la vigente tiene 9 características | **Hecho** | F2; verificable en iso25000.com. **El diplomado cita la de 2011** |
| Las leyes son las de Richards y Ford | **Hipótesis** | F2 y F4 coinciden, pero F1 no las enuncia. Richards & Ford es bibliografía oficial → plausible, no confirmado |
| TCP loopback entrega 25–60 µs de ida y vuelta | **Opinión/estimación** | F5. **Contradicho por medición** → ver C3 |
| Memoria compartida entrega 150–600 ns | **Opinión/estimación** | F5. **Contradicho por medición** → ver C4 |
| Variante TCP Python: p50 13,38 µs · p99.9 62,38 µs · máx 2 202 µs | **Hecho medido** | F6, 100 000 iteraciones tras 20 000 de calentamiento |
| Variante Memoria compartida C: p50 83 ns · p99.9 167 ns · máx 34,8 µs | **Hecho medido** | F6, 3 rondas × 1 000 000. Ninguna muestra supera 1 ms |
| El transporte explica el 91 % de la diferencia y el lenguaje el 9 % | **Hecho medido** | F6, control Bc (TCP en C) contra B (TCP en Python) |
| `CLOCK_MONOTONIC` avanza a saltos de 1 µs en macOS | **Hecho medido** | ADR-003 |
| macOS/arm64 no permite fijar hilos a núcleos (`KERN_NOT_SUPPORTED`) | **Hecho verificado** | ADR-002 |
| La cola de latencia la causa el planificador / la máquina ocupada | **Hipótesis** | 363 violaciones del umbral un día y cero otro. **Experimento bajo carga controlada pendiente** |

---

## 4. Contradicciones entre fuentes

### C1 — Taxonomía de atributos ⚠️ **NO RESUELTA — riesgo de examen**

| Atributo | Camilo (F4) lo clasifica como | Danny (F2) lo clasifica como |
|---|---|---|
| **Rendimiento** | **transversal** | **operacional** |
| **Usabilidad** | **operacional** | **transversal** |
| **Fiabilidad, tolerancia a fallos, recuperabilidad** | **transversales** | operacionales (recuperabilidad) |
| **Portabilidad** | transversal | **estructural** |
| Disponibilidad, escalabilidad | operacionales | operacionales ✔ |
| Mantenibilidad, modificabilidad, testabilidad | estructurales | estructurales ✔ |
| Seguridad | transversal | transversal ✔ |

**Qué dice el material oficial:** solo que existen las tres categorías. El desarrollo está en el
Genially M1P5, **no descargado**.

**Resolución:** *imposible con lo disponible.* `[Complementario]` En Richards & Ford —bibliografía
oficial— rendimiento es **operacional** y usabilidad es **transversal** (la clasificación de F2),
pero el docente puede haber usado otra. **No se adopta ninguna de las dos.**

> **Acción inmediata:** conseguir el Genially M1P5 **antes** de la autoevaluación. Si no se
> consigue, responder según Richards & Ford y asumir el riesgo conscientemente.

### C2 — ISO/IEC 25000 vs. ISO/IEC 25010 — **resuelta**

| Fuente | Qué dice |
|---|---|
| **F1** (oficial) | «ISO/IEC 25000» en el Cierre; «ISO/IEC 25010» en Conclusiones y en Recursos |
| **F4** (Camilo) | Los presenta como estándares **alternativos**: «otros estándares, como ISO/IEC 25010, organizan las características de otra manera» |
| **F2** (Danny) | 25000 es la **familia** (SQuaRE); 25010 es el **modelo de calidad dentro** de ella |

**Se adopta F2.** Razón: la propia referencia bibliográfica de F1 lo confirma —
*«ISO/IEC 25010:2011 Systems and software engineering — SQuaRE — System and software quality
models»*. **No son alternativas: una contiene a la otra.** La formulación de F4 es incorrecta y no
debe pasar al entregable.

> En una entrega escrita conviene decir «la familia ISO/IEC 25000, y en concreto el modelo
> ISO/IEC 25010». Y mencionar que existe la revisión de 2023 con 9 características es exactamente
> el tipo de precisión que distingue a un arquitecto de alguien que memorizó una tabla.

### C3 — Latencia de TCP en loopback — **resuelta por medición**

| Fuente | Valor |
|---|---|
| F5 (Camilo) | «30–60 µs» (intro) · «25–60 µs» (Nivel 1) |
| **F6 (medido)** | **13,38 µs** en Python · **11,5 µs** en C |

**Manda el dato medido.** La estimación de Camilo es conservadora por un factor de ~2–4×. Es
razonable como orden de magnitud publicado, pero **el informe cita nuestros números, no los de una
referencia genérica**.

### C4 — Latencia de memoria compartida — **resuelta por medición**

| Fuente | Valor |
|---|---|
| F5 (Camilo) | 150–600 ns |
| **F6 (medido)** | **83 ns** (p50, 3 × 1 000 000) |

**Manda el dato medido.** Nuestra implementación es ~2–7× mejor que la estimación. Vale la pena
decir por qué en el informe: buffer circular con índices atómicos alineados a línea de caché y
espera activa, exactamente como F5 describe — pero además la tabla del dominio **cabe en una sola
línea de caché de 64 B** (F3), lo que elimina el fallo de caché del camino crítico.

### C5 — Socket de dominio Unix — **abierta, pendiente de medir**

F5 estima 8–20 µs. **Sin medir**: es la variante C, asignada a Camilo, con fecha 21/09.
Es su propia estimación la que deberá verificar.

### C6 — Alcance de las variantes — **decisión de equipo, no error**

F5 propone 5 peldaños: HTTP · TCP · **UDP** · Unix · memoria compartida.
El equipo implementó: A (HTTP) · B/Bc (TCP) · C (Unix) · D (memoria) · **E (ICMP)**.

**Diferencia:** F5 incluye UDP y no ICMP; el equipo hizo lo contrario.
**Se mantiene el plan del equipo.** Añadir UDP ahora es sobreingeniería — ya hay cinco variantes,
el rango cubierto es de seis órdenes de magnitud, y el enunciado no pide exhaustividad. El
argumento de F5 a favor de UDP (*«el sacrificio es de un atributo nombrado del módulo —fiabilidad—
y no de una comodidad»*) es bueno y **se recoge en el informe como análisis, sin implementarlo**.

### C7 — Nomenclatura — **se unifica**

F5 usa «Nivel 0–4»; el equipo usa «variante A–E». Se mantiene A–E (ya está en el código, los logs
y los ADR). Mapa de equivalencia para leer el documento de Camilo:

| F5 | Equipo | Transporte |
|---|---|---|
| Nivel 0 | **A** | HTTP/1.1 REST |
| Nivel 1 | **B** / **Bc** | TCP + `TCP_NODELAY` (Python / C) |
| Nivel 2 | *(no implementado)* | UDP |
| Nivel 3 | **C** | Socket de dominio Unix |
| Nivel 4 | **D** | Memoria compartida + espera activa |
| — | **E** | ICMP (línea base) |

### C8 — Warm-up — **discrepancia menor, hay que cerrarla**

F5 recomienda descartar 50 000–100 000 muestras. La variante TCP Python se midió descartando **20 000**.
**Acción:** unificar el criterio en `ESPEC-MEDICION.md` y aplicarlo a todas las variantes, o
justificar por escrito por qué 20 000 basta. Si cada variante usa un warm-up distinto, la
comparación pierde validez — que es justamente lo que el harness común existe para evitar.

---

## 5. Lo que los aportes de Camilo **mejoran** del trabajo actual

No todo son contradicciones. F5 contiene cuatro cosas que el reto **no tiene** y que deberían
incorporarse:

| # | Aporte de F5 | Por qué vale | Costo |
|---|---|---|---|
| 1 | **Medir el costo del reloj en vacío y reportarlo** | Una llamada monotónica cuesta ~20–25 ns. Con un RTT de 83 ns, **el instrumento es ~25 % de lo medido**. No declararlo es un agujero metodológico | Bajo — un microbenchmark |
| 2 | **Medir con y sin `TCP_NODELAY`** | El ejemplo más limpio de «una decisión de una línea con impacto de orden de magnitud» | Bajo — ya existe la variante TCP Python |
| 3 | **Matriz de 10 atributos × 5 niveles** | Más completa que la tabla de trade-offs actual. Muestra de un vistazo que *la columna que gana en la primera fila pierde en casi todas las demás* | Nulo — adaptarla |
| 4 | **Nombrar io_uring, DPDK, Onload, RDMA y páginas enormes como fuera de alcance, y por qué** | Demuestra conocer el techo y saber dónde está la frontera del ejercicio | Nulo — un párrafo |
| 5 | **Tabla «cada parte del reto ↔ sección del Módulo I ↔ atributos involucrados»** | Demuestra que el ejercicio se resolvió con el marco del módulo y no solo con intuición técnica | Nulo — adaptarla |

> El punto 1 es el más importante: con la variante Memoria compartida C midiendo 83 ns, **el costo del instrumento ya
> no es despreciable**. Es una debilidad real del informe actual y Camilo la detectó.

---

## 6. Conexión con módulos anteriores

Módulo 0 (inducción) no aporta contenido técnico. La única conexión operativa: **después de la
fecha de cierre no se califica, sin excepción** — gobierna el plan del reto (entrega objetivo
27/09, cierre 29/09).

---

## 7. Implicaciones arquitectónicas

1. **La arquitectura es un ciclo, no un acto único.** La evolución del sistema produce evidencia que
   redefine los drivers. El ADR es lo único que hace revisable una decisión seis meses después
   (F2).
2. **El sistema operativo es una restricción arquitectónica, no un detalle de implementación.**
   Verificado: `thread_policy_set` → `KERN_NOT_SUPPORTED` en macOS/arm64; `CLOCK_MONOTONIC` con
   granularidad de 1 µs. La plataforma acota lo que la arquitectura puede prometer.
3. **Plano de control ≠ plano de datos** (F3). La interfaz que enciende y observa el sistema no
   puede estar en la ruta medida: un navegador vive en milisegundos. Verificado: las mismas
   mediciones desde terminal y desde la aplicación web dan resultados idénticos (13,4/13,46 µs ·
   11,5/11,67 µs · 83/83 ns).
4. **La opción que gana el benchmark es la que no desplegarías.** Memoria compartida gana por seis
   órdenes de magnitud y ata los procesos al mismo host, quema un núcleo al 100 %, pierde
   transparencia de red y es infernal de depurar. **Decir las dos cosas a la vez es el ejercicio.**
5. **La cola es donde vive la arquitectura; el promedio es donde se esconde** (F5). Medido: media
   13,45 µs contra máximo 2 202 µs — un factor de **163**.

---

## 8. Preguntas abiertas

| # | Pregunta | Bloquea | Cómo se resuelve |
|---|---|---|---|
| 1 | **¿Cuál es la taxonomía de atributos según el docente?** (C1) | Autoevaluación — 1 intento | Genially M1P5 |
| 2 | ¿Cuál es la formulación exacta de las leyes? | Autoevaluación | Genially 2 |
| 3 | ¿La entrega del reto es una por grupo o una por persona? | Todo el plan | Preguntar 15/09 |
| 4 | ¿Qué frontera de medición espera el docente? | Redacción del informe | Preguntar 15/09 |
| 5 | Mediana 13 µs con máximo entre 130 µs y 44 ms según el día: **¿cumple 1 ms?** | Conclusión del informe | Preguntar 15/09 |
| 6 | ¿Espera red física entre dos máquinas o acepta loopback? | Alcance experimental | Preguntar 15/09 |
| 7 | ¿La cola la causa el planificador o la máquina ocupada? | Análisis del informe | Experimento bajo carga controlada |
| 8 | ¿Se adopta el warm-up de 50 k–100 k o se justifica el de 20 k? (C8) | Validez de la comparación | Decisión de equipo |

---

## 9. Temas que requieren más investigación

- **ISO/IEC 25010:2023** — las 9 características, *Interaction Capability* y *Flexibility*. Basta
  con saber que existe y que el diplomado cita la de 2011.
- **Teorema CAP** — se nombra en la tabla de trade-offs pero no está en el material del M1.
  Probablemente aparezca en módulos posteriores.
- **Patrones de resiliencia** — Circuit Breaker (Fowler) y feature toggles están en los recursos
  complementarios de F1 pero no se desarrollan en el módulo.
- **Estrategias de Disaster Recovery en AWS** — cuatro de los quince recursos complementarios.
  **Confirma el sesgo AWS-first del curso**; conviene leerlos antes del módulo de cloud.
- **Costo real de la llamada al reloj** en la máquina de medición (§5.1).

---

## 10. Posibles preguntas de evaluación

1. ¿Cuáles son los **cuatro componentes** de una arquitectura? *(estructura · características · decisiones · principios)*
2. Diferencia entre **decisión** y **principio**. *(la decisión no admite excepción; el principio sí)*
3. Diferencia entre **decisión** y **restricción**. *(se elige vs. se recibe)*
4. Las **tres dimensiones** de la importancia de la arquitectura.
5. Enunciar la **primera ley** y su **corolario**.
6. ¿Por qué el «por qué» importa más que el «cómo»? *(sin el registro, la decisión no es revisable)*
7. Los **tres frentes** de restricciones. *(negocio · tecnología · equipo)*
8. Clasificar un atributo dado en operacional / estructural / transversal. ⚠️ **Ver C1**
9. Disponibilidad vs. rendimiento; rendimiento vs. escalabilidad; tolerancia a fallos vs. recuperabilidad.
10. Las **ocho características** de ISO/IEC 25010:2011.
11. Convertir un enunciado vago en un requisito medible.
12. Identificar el atributo en juego en un caso práctico *(los 6+ casos de F4 son excelente entrenamiento)*.
13. ¿Por qué no existe una arquitectura «mejor»?

---

## 11. Qué sube a `_Base-Conocimiento/Aprendizajes/`

Se escriben al cerrar el módulo (29/09). Candidatos confirmados por este consolidado:

1. **Un atributo de calidad que no se mide es un deseo** — el método para convertir un enunciado
   vago en un requisito verificable. Transversal a cualquier requisito no funcional.
2. **La media miente; reporta percentiles** — con la evidencia del factor 163.
3. **Congelar la especificación de medición antes de implementar** — aplica a cualquier benchmark
   comparativo. Refuerzo de C8: incluye el warm-up, no solo la frontera.
4. **El costo del instrumento debe medirse y declararse** — aporte de Camilo. Aplica a toda
   instrumentación, no solo a la latencia.
5. **Separar plano de control y plano de datos** — aplica a observabilidad en general.
6. **El sistema operativo es una restricción arquitectónica** — con la evidencia de macOS/arm64.
7. **La opción que gana el benchmark suele ser la que no desplegarías** — la primera ley, medida.
8. **Cómo se consolidan fuentes que se contradicen** — el método de este documento: registrar ambas,
   resolver por autoridad, y dejar abierto lo que no se puede cerrar.

---

## 12. Próximos pasos

| # | Acción | Responsable | Fecha |
|---|---|---|---|
| 1 | **Conseguir los 4 Genially y el video** (exportar a PDF o transcribir a `Notas/`) | Danny | antes de la autoevaluación |
| 2 | Llevar las preguntas 3–6 (§8) al encuentro sincrónico | Danny | **15/09 18:00** |
| 3 | Cerrar C8 (warm-up) en `ESPEC-MEDICION.md` | Danny | 16/09 |
| 4 | Incorporar las 5 mejoras de §5 al informe | Danny | 20/09 |
| 5 | Implementar y medir la variante A | Freddy | 21/09 |
| 6 | Implementar y medir la variante C — y contrastar con su propia estimación de 8–20 µs (C5) | Camilo | 21/09 |
| 7 | Experimento bajo carga controlada (pregunta 7) | Danny | 22/09 |
| 8 | Autoevaluación M1 — **un solo intento**, después del paso 1 | cada uno | antes del 29/09 |
| 9 | Escribir los aprendizajes de §11 | Danny | 29/09 |
