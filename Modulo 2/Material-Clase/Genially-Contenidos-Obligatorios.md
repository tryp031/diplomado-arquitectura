# Contenidos obligatorios M2 — los 4 Genially (transcripción)

> **Tipo:** `material-oficial` (Brightspace → Módulo 2 → «Contenidos obligatorios», Unidad 3 de 5).
> **Fuente:** 4 presentaciones interactivas de Genially, públicas, extraídas el 2026-09-30 del campo de
> transcripción que Genially incrusta en cada presentación (`view.genially.com/<id>`):
>
>
> **Las 4 presentaciones (tabla abajo).**
>
> **Falta P4:** *Seguridad* es un **video de YouTube** (`MbUXkPdKaGw`, «Módulo 2 - Seguridad Security», 5 min 13 s).
> **No se capturó** (YouTube bloqueó la transcripción). El deck `Tacticas-Seguridad.md` cubre el tema en texto.
>
> **Límites de la extracción:** es una transcripción **plana**: el orden de las láminas, los pop-ups («Ver más»)
> y la estructura visual **no se conservan** (p. ej. los 7 pasos de ADD aparecen desordenados). Las imágenes,
> tablas de tácticas y la «mini trivia de validación» de P1 **no están**. Números de lámina y orden: ver Genially.
> **Este archivo no se edita.** Las notas van en `Aportes/` o en el bloque final, marcado como anotación.


| # | Título en Genially | Láminas | ID |
|---|---|---|---|
| P1 | M2P1 — Requerimientos y tácticas de Arquitectura de Software | 12 | `683a05d4d217af363e6ff92b` |
| P2 | M2P2 — Disponibilidad (AVAILABILITY) | 7 | `683a06874ebc16740206e856` |
| P3 | M2P3 — Desempeño (PERFORMANCE) | 6 | `683a077a59f7371b934a61fa` |
| P5 | M2P5 — Interoperabilidad (INTEROPERABILITY) | 10 | `683a085c06169c8e038d89f9` |

---

## P1 — Requerimientos de calidad, ASRs, ADD y tácticas

Requerimientos de Calidad En el desarrollo de software, no basta con que una funcionalidad exista. También es clave cómo se comporta esa funcionalidad bajo diferentes condiciones. Aquí es donde entran los requerimientos de calidad, también conocidos como requerimientos no funcionales. Estos requerimientos acompañan a los funcionales, pero les agregan condiciones específicas relacionadas con tiempo de respuesta, disponibilidad, confiabilidad, seguridad, entre otros factores. Son fundamentales para garantizar una experiencia eficiente y segura para los usuarios, y para que el sistema cumpla su propósito en contextos reales de operación. Por ejemplo Ahora veamos algunos ejemplos específicos de cómo los requerimientos de calidad añaden valor a una funcionalidad. Estas características pueden marcar la diferencia entre una experiencia fluida y confiable… o una frustrante e insegura.



A continuación, algunos criterios que suelen acompañar a requerimientos funcionales clave: Que la operación se ejecute en menos de 10 segundos, o incluso en 1 segundo. Que funcione correctamente el 99,9% del tiempo. Que solo usuarios autorizados puedan realizarla. Que los datos estén protegidos y sean anónimos. Que sea posible con cualquier entidad financiera, esté o no registrada en el sistema. Ver más Sección Sección Sección En la diapositiva anterior exploramos las preguntas clave para identificar un ASR (Requerimiento Arquitecturalmente Significativo). ¡Vamos a ponerlo en práctica! Partamos de un ejemplo simple, pero muy útil: el Reto 1, en el que se debía construir un sistema capaz de responder a un estímulo del tipo “ping” con una respuesta “pong”.



Aunque el comportamiento parece básico, es perfecto para comenzar a evaluar atributos de calidad bajo escenarios reales. Escenario de calidad: Ping – Pong Consolidando todo lo aprendido... Ahora que conoces los conceptos de ASRs y has explorado cómo distintos atributos de calidad influyen en el diseño arquitectónico. ¡Véamos un ejemplo completo! A continuación, te presentamos el escenario de calidad totalmente documentado para el Reto 1: Sistema Ping-Pong. Este escenario resume todos los elementos clave que deben considerarse al analizar un requerimiento arquitecturalmente significativo. Escenario de calidad documentado Las operaciones se definen como Normal Operación mínima En estrés oalta carga Se define cuando el sistema se encuentra operando a su máxima capacidad debido a un "estrés" generado por altas solicitudes. Sistema en estado degradado, con funcionalidades al mínimo o las más vitales. Operación donde el sistema se encuentra trabajando en condiciones óptimas, sin aumentos de carga. Tácticas de Arquitectura¿Por qué son importantes? Aquí es donde entran en juego las tácticas de arquitectura, un conjunto de decisiones estructurales que ayudan a garantizar el cumplimiento de los atributos de calidad del sistema. Estas tácticas no solo permiten resolver problemas comunes, sino que también facilitan la predicción del comportamiento del sistema ante diferentes condiciones. Son una especie de "caja de herramientas" del arquitecto de software. ¿Qué harías si tu sistema necesita responder rápido y con seguridad, incluso bajo alta carga? Restricciones de arquitectura Decisiones de arquitectura DISEÑO BASADO EN ATRIBUTOS ADD AAD Actividad de diseño de arquitectura Alcance del sistema DISEÑO BASADO EN ATRIBUTOS ADD Iterar si es necesario Diagramar las vistas y registrar las decisiones de diseño. Establecer el objetivo de la iteración mediante la selección de drivers. Elegir uno o más conceptos de diseño que satisfagan los drivers seleccionados Itinerar Paso 7 Paso 1 Paso 4 Paso 6 Paso 2 Paso 3 Paso 5 PASOS Elegir uno o más elementos del sistema para refinar Crear instancias de elementos arquitectónicos, asignar responsabilidades y definir interfaces Realizar un análisis del diseño actual y revisar el objetivo de la iteración y el logro del propósito del diseño Revise las entradas. Paso 3: Elegir uno o más elementos del sistema para refinar Satisfacer los drivers requiere que tome decisiones de diseño arquitectónico, que luego se manifiestan en una o más estructuras arquitectónicas. Estas estructuras se componen de elementos interrelacionados (módulos y/o componentes) y estos elementos generalmente se obtienen al refinar otros elementos que identificó previamente en una iteración anterior. El refinamiento puede significar la descomposición en elementos de grano más fino (enfoque de arriba hacia abajo), la combinación de elementos en elementos de grano más grueso (enfoque de abajo hacia arriba) o la mejora de elementos previamente identificados. ¡Ver más! ¡Ver más! Para el desarrollo totalmente nuevo, puede comenzar por establecer el contexto del sistema y luego seleccionar el único elemento disponible, es decir, el sistema mismo, para refinarlo mediante descomposición. Para sistemas existentes o para iteraciones de diseño posteriores en sistemas totalmente nuevos, normalmente elige refinar elementos que se identificaron en iteraciones anteriores. ¡Ver más! Los elementos que seleccionará son los que intervienen en la satisfacción de drivers específicos. Por esta razón, cuando el diseño aborda un sistema existente, debe tener una buena comprensión de los elementos que forman parte de la arquitectura construida del sistema. La obtención de esta información puede implicar algún "trabajo de detective", ingeniería inversa o conversaciones con los desarrolladores. ¡Ver más! En algunos casos, es posible que deba invertir el orden de los pasos 2 y 3. Por ejemplo, al diseñar un sistema totalmente nuevo o al desarrollar ciertos tipos de arquitecturas de referencia, al menos en las primeras etapas del diseño, se centrará en los elementos del sistema y comience la iteración seleccionando un elemento en particular y luego considerando los controladores que desea abordar. Estos aspectos no solo afectan el comportamiento del sistema, sino que también pueden impactar directamente en su diseño.



De hecho, algunos requerimientos de calidad son tan críticos que influyen desde el inicio en la Arquitectura de Software. A estos se les conoce como ASR (Architecturally Significant Requirements), y deben ser tratados con especial cuidado en el diseño. Hay muchos tipos diferentes de conceptos de diseño disponibles, por ejemplo, tácticas, patrones, arquitecturas de referencia y componentes desarrollados externamente y, para cada tipo, pueden existir muchas opciones. Esto puede resultar en muchas alternativas que necesitan analizarse antes de tomar la decisión final. Paso 4: Elegir uno o más conceptos de diseño que satisfagan los drivers seleccionados Elegir los conceptos de diseño es probablemente la decisión más difícil a la que se enfrentará en el proceso de diseño, ya que requiere que identifique los diversos conceptos de diseño que podrían usarse para lograr su objetivo de iteración y luego hacer una selección de esas alternativas. Hay muchos tipos diferentes de conceptos de diseño disponibles, por ejemplo, tácticas, patrones, arquitecturas de referencia y componentes desarrollados externamente y, para cada tipo, pueden existir muchas opciones. Esto puede resultar en muchas alternativas que necesitan analizarse antes de tomar la decisión final. Antes de comenzar el diseño de la arquitectura, es importante determinar el alcance del sistema: qué hay dentro y qué hay fuera del sistema que está creando y con qué entidades externas interactuará el sistema. Este contexto se puede representar usando un diagrama de contexto del sistema. Descripción general de la actividad de diseño de arquitectura REQUERIMIENTOS ARQUITECTURALMENTE SIGNIFICATIVOS (ASRs) ¿Cómo identificar un ASR?



A continuación, te presentamos una serie de preguntas guía que te permitirán reconocer si un requerimiento es, o no, arquitecturalmente significativo: ¿Carga máxima?  ¿En fallos del sistema? ¿Durante procesos simultáneos? ¿Bajo qué circunstancias ocurre el evento? Un clic, una solicitud externa, una actualización automática… ¿Es una acción crítica? ¿Ocurre en tiempo real? ¿Durante una transacción sensible? ¿Rapidez? ¿Seguridad? ¿Acceso contínuo? Como rendimiento, disponibilidad, escalabilidad, seguridad, mantenibilidad, etc. El "actor" puede ser un usuario, un componente del sistema, un servicio externo, etc. ¿Cuáles elementos de la arquitectura están directamente afectados? Bases de datos, servicios, infraestructura, protocolos de seguridad… ¿Qué atributos de calidad están implicados? ¿En qué momento interviene este actor? ¿Qué respuesta espera el actor? ¿Qué evento desencadena la acción? ¿Qué actor está asociado al ASR? PASO 6: Diagramar las vistas y registrar las decisiones de diseño. En este punto, ha terminado de realizar las actividades de diseño para la iteración. Sin embargo, es posible que no haya tomado ninguna medida para asegurarse de que las vistas, las representaciones de las estructuras que creó, se conserven.  Por ejemplo, si realizó el paso 5 en una sala de conferencias, probablemente terminó con una serie de diagramas en una pizarra. Esta información es esencial para el resto del proceso y debe capturarla para luego analizarla y comunicarla a otras partes interesadas. Capturar las vistas puede ser tan simple como tomar una foto de la pizarra. Es casi seguro que las vistas que ha creado no están completas; por lo tanto, es posible que estos diagramas deban revisarse y refinarse en una iteración posterior. Esto normalmente se hace para acomodar elementos resultantes de otras decisiones de diseño que tomará para admitir controladores adicionales. Es por esto por lo que hablamos de “bocetar” las vistas en ADD, donde un “boceto” se refiere a un tipo de documentación preliminar. La documentación más formal y completa de estas vistas, en caso de que decida producirla, ocurre solo después de que se hayan terminado las iteraciones de diseño (como parte de la actividad de documentación arquitectónica). ¡Ver más! ¡Ver más! Además de capturar los bocetos de las vistas, debe registrar las decisiones importantes tomadas en la iteración del diseño, así como las razones que motivaron estas decisiones (es decir, la justificación), para facilitar el análisis y la comprensión posteriores de las decisiones. Por ejemplo, las decisiones sobre tradeoffs importantes deben registrarse en este momento. Durante una iteración de diseño, las decisiones se toman principalmente en los pasos 4 y 5. Paso 1: Revise las entradas Antes de comenzar una ronda de diseño, debe asegurarse de que los drivers arquitectónicos (las entradas del proceso de diseño) estén disponibles y sean correctos.Éstas incluyen: •	El propósito de la ronda de diseño. •	Los requisitos funcionales primarios.  • Los escenarios de atributos de calidad primarios (QA).  •	Cualquier restricción. •	Cualquier preocupación. Nota Cada atributo de calidad presenta desafíos únicos, y por eso cada uno requiere un conjunto distinto de tácticas para ser abordado de manera eficaz. En el siguiente recurso, analizaremos uno a uno los principales atributos de calidad y descubriremos qué tácticas son más efectivas para cada uno. Mini trivia de validación: PASO 7: Realizar un análisis del diseño actual y revisar el objetivo de la iteración y el logro del propósito del diseño Para este paso, debería haber creado un diseño parcial que aborde el objetivo establecido para la iteración. Asegurarse de que este caso sea realmente una buena idea, para evitar stakeholders insatisfechos y reprocesos. Puede realizar el análisis usted mismo revisando los bocetos de las vistas y las decisiones de diseño que capturó, pero una idea aún mejor es que alguien más lo ayude a revisar este diseño. Hacemos esto por la misma razón por la que las organizaciones suelen tener un grupo de pruebas/control de calidad separado: otra persona no compartirá sus suposiciones y tendrá una base de experiencia y una perspectiva diferentes. Una vez que se haya analizado el diseño realizado en la iteración, debe revisar el estado de su arquitectura en términos de su propósito de diseño establecido. Esto significa considerar si, en este punto, ha realizado suficientes iteraciones de diseño para satisfacer los controladores asociados con la ronda de diseño. También significa considerar si se ha logrado el propósito del diseño o si se necesitan rondas de diseño adicionales en futuros incrementos del proyecto. ¡Ver más! Paso  5: Crear instancias de elementos arquitectónicos, asignar responsabilidades y definir interfaces Cuando haya seleccionado uno o más conceptos de diseño, debe tomar otro tipo de decisión: cómo instanciar elementos a partir de los conceptos que acaba de seleccionar. Por ejemplo, si seleccionó el patrón de capas como concepto de diseño, debe decidir cuántas capas se utilizarán y sus relaciones permitidas, ya que el patrón en sí no las prescribe. Después de instanciar los elementos, debe asignar responsabilidades a cada uno de ellos. Por ejemplo, en una aplicación, suelen estar presentes al menos tres capas: presentación, negocio y datos. Las responsabilidades de estas capas difieren: las responsabilidades de la capa de presentación incluyen la gestión de todas las interacciones del usuario, la capa empresarial gestiona la lógica de la aplicación y hace cumplir las reglas empresariales, y la capa de datos gestiona la persistencia y coherencia de los datos. ¡Ver más! Instanciar elementos es solo una parte de la creación de estructuras que satisfagan un driver o una preocupación. Los elementos que se han instanciado también deben estar conectados, lo que les permite colaborar entre sí. Esto requiere la existencia de relaciones entre los elementos y el intercambio de información a través de algún tipo de interfaz. La interfaz es una especificación contractual que indica cómo debe fluir la información entre los elementos. ¡Ver más! Antes de comenzar el diseño de la arquitectura, es importante determinar el alcance del sistema: qué hay dentro y qué hay fuera del sistema que está creando y con qué entidades externas interactuará el sistema. Este contexto se puede representar usando un diagrama de contexto del sistema. En el diseño arquitectónico, convertimos las decisiones sobre los impulsores arquitectónicos en estructuras. Los drivers arquitectónicos comprenden requisitos significativos desde el punto de vista arquitectónico (ASR), pero también incluyen funcionalidad, restricciones, preocupaciones arquitectónicas y propósito de diseño. Descripción general de la actividad de diseño de arquitectura Imagina un edificio imponente:su fachada llama la atención, pero son los cimientos y estructuras internas los que garantizan su durabilidad y funcionalidad.



De igual manera, un sistema puede verse bien visualmente, pero son las tácticas arquitectónicas las que le dan estabilidad, seguridad, extensibilidad y rendimiento. 2.	Motivación – la metáfora del edificio Te invitamos a leer el siguiente post: https://www.linkedin.com/posts/jacobbeningo_embedded-firmware-coding-activity-7270077013544050688-rRsD/ Luego, las estructuras resultantes se utilizan para guiar el proyecto de muchas formas.Sirven como base para educar a un nuevo miembro del proyecto. Hasta ahora hemos visto cómo los requerimientos de calidad agregan valor a las funcionalidades del sistema. Pero, ¿sabías que no todos los requerimientos pesan lo mismo al momento de diseñar la arquitectura?



Algunos tienen tal impacto que definen desde el inicio la estructura del sistema, y deben ser considerados desde la etapa más temprana del desarrollo.  Estos son los llamados ASRs: Requerimientos Arquitecturalmente Significativos. A continuación, podrás explorar cómo este requerimiento se ve afectado por distintos atributos de calidad como: Latencia Escenario detallado Seguridad Disponibilidad •	Atributo: Valor



•	Unidad: Segundos



•	Respuesta esperada: 1 ms



•	Prioridad: Alta •	Elemento: Valor



•	Actor: Cliente



•	Estímulo: Ping



•	Ambiente: Operación normal



•	Artefacto: Servidor local



•	Respuesta esperada: Ante el envío de un estímulo de tipo ping, el servidor responde con un pong. •	Atributo: Valor



•	Impacto: Datos sin cifrar. Mecanismos sin cifrado. •	Ambiente: Operación normal



•	Prioridad: Baja •	Atributo: Valor •	Unidad: %



•	Respuesta esperada: 90



•	Prioridad: Baja ¿Por qué es importante este escenario? ♦	Este ejemplo muestra cómo documentar completamente un requerimiento arquitecturalmente significativo.



♦	Permite identificar qué atributos son críticos, cuáles no lo son en el contexto actual, y qué decisiones arquitectónicas deben tomarse para garantizar el comportamiento esperado. Paso 2: Establecer el objetivo de la iteración mediante la selección de drivers Cada iteración de diseño se enfoca en lograr un objetivo particular. Tal objetivo generalmente implica diseñar para satisfacer un subconjunto de los drivers. Por ejemplo, un objetivo de iteración podría ser crear estructuras a partir de elementos que permitan lograr un escenario de rendimiento particular o un caso de uso. Por este motivo, al realizar actividades de diseño, debe establecer un objetivo antes de iniciar una iteración de diseño en particular. Iterar si es necesario Debe realizar iteraciones adicionales y repetir los pasos 2 a 7 para cada driver que se consideró. Sin embargo, la mayoría de las veces, este tipo de repetición no será posible debido a limitaciones de tiempo o de recursos que lo obligan a detener las actividades de diseño y pasar a la implementación.¿Cuáles son los criterios para evaluar si son necesarias más iteraciones de diseño? Deje que el riesgo sea su guía. Al menos debería haberse dirigido a los controladores con la mayor prioridad. Idealmente, debe tener la certeza de que los controladores críticos están satisfechos o, al menos, que el diseño es "suficientemente bueno" para satisfacerlos. Cuando se pulse el botón “Confirmar pago”, se debe procesar la transacción financiera con la entidad correspondiente. Pero, además, se espera que este proceso:



✓	Sea rápido. ✓	Ocurra con alta disponibilidad. ✓	Solo esté habilitado para usuarios autorizados. ✓	Proteja los datos del usuario. ✓ Sea compatible con diversas entidades financieras. Por ejemplo 1.	Diseño robusto y alineado al negocio La elección de tácticas adecuadas facilita la construcción de sistemas robustos, optimizados y alineados con las necesidades del negocio y de los usuarios. Esto mejora la mantenibilidad, la escalabilidad y la eficiencia desde las primeras etapas del desarrollo. A continuación, podrás explorar cómo este requerimiento se ve afectado por distintos atributos de calidad como: Latencia Seguridad Disponibilidad •	Unidad: Segundos



•	Respuesta esperada: 1 ms



•	Prioridad: Alta



⚠️ Este atributo sí fue especificado desde el inicio en el reto, por lo tanto, su prioridad es alta. La arquitectura debe considerar mecanismos que garanticen una respuesta casi inmediata. •	Impacto: Datos sin cifrar. Mecanismos sin cifrado. •	Prioridad: Baja



🔒 En este escenario, la seguridad no se tuvo en cuenta. Aunque no siempre es una omisión crítica en sistemas simples, en entornos reales, no cifrar datos puede tener consecuencias graves. Este es un claro ejemplo de atributo de calidad no considerado, que también debemos identificar y documentar. •	Unidad: %



•	Respuesta esperada: 90



•	Prioridad: Baja



❗ Aunque es un atributo de calidad importante, no fue explicitado en el reto, lo que le otorga una prioridad baja en este caso específico. Esto no significa que no sea relevante en otros contextos, pero la arquitectura no se diseñó pensando en disponibilidad como eje principal. Como puedes ver, los ASRs deben definirse con claridad y de forma priorizada. Algunos tendrán un impacto profundo en las decisiones arquitectónicas; otros pueden ser descartados según el contexto… pero nunca deben quedar sin analizar. 3.	Construyendo experiencias, no solo software. Así como un arquitecto civil diseña cimientos firmes, un arquitecto de software utiliza tácticas para responder a desafíos como el rendimiento, la seguridad, la confiabilidad y la escalabilidad.



Estas decisiones moldean la experiencia del usuario, generan confianza y determinan el éxito a largo plazo del sistema.

---

## P2 — Disponibilidad

Disponibilidad (AVAILABILITY) Tácticas Definición Disponibilidad (AVAILABILITY) Relación con otros atributos de calidad Escenario Definición La disponibilidad se refiere a la propiedad del software de estar ahí listo para realizar su tarea cuando se necesita. También abarca la capacidad de un sistema para enmascarar o reparar defectos de modo que no se conviertan en fallas, asegurando así que el período de interrupción del servicio acumulativo no exceda un valor requerido durante un intervalo de tiempo específico. La causa de una falla (failure) se llama defecto (fault). Un defecto puede ser interno o externo al sistema bajo consideración. Los estados intermedios entre la ocurrencia de un defecto y la ocurrencia de una falla se denominan errores. Los defectos se pueden prevenir, tolerar, eliminar opronosticar. Una falla es la desviación del sistema de su especificación, donde esa desviación es visible externamente. Determinar que ha ocurrido una falla requiere algún observador externo en el entorno. Relación con otrosatributos de calidad La disponibilidad está estrechamente relacionada con la seguridad, pero claramente distinta de ella. Un ataque de denegación de servicio está diseñado explícitamente para hacer que un sistema falle, es decir, para que no esté disponible.   La disponibilidad también está estrechamente relacionada con el Rendimiento, ya que puede ser difícil saber cuándo un sistema ha fallado y cuándo simplemente responde de manera extremadamente lenta. Ver más Escenario general Escenario Ejemplo de un escenario concreto Tácticas Las tácticas de disponibilidad están diseñadas para permitir que un sistema prevenga o soporte fallas del sistema para que el servicio que entrega siga cumpliendo con su especificación. Tactics to Control Response Fault Fault masked, prevented, or repair made Las tácticas de disponibilidad tienen 1 de 3 propósitos: 1. Detección 2. Recuperación 3. Prevención de fallas Ver más Escenario general A continuación, verás un escenario general: Ejemplo de un escenario concreto Un servidor en una granja de servidores falla durante el funcionamiento normal y el sistema informa al operador y continúa funcionando sin tiempo de inactividad. Finalmente, la disponibilidad está estrechamente relacionada con la seguridad, que se ocupa de evitar que el sistema entre en un estado peligroso y de recuperar o limitar el daño cuando lo hace. Para ampliar el detalle de cada táctica, cómo se aplica y su significado, te invitamos a consultar el siguiente libro: Bass, L., Clements, P., &amp; Kazman, R. (2022). Software architecture in practice (4th ed.). SEI / Addison-Wesley.

---

## P3 — Desempeño

desempeño (performance) Definición "It’s about time" Desempeño, es eso: se trata de tiempo y de la capacidad del sistema para cumplir con los requisitos de tiempo. El hecho es que las operaciones en las computadoras toman tiempo: 



Los cálculos toman un tiempo del orden de miles de nanosegundos



el acceso al disco (ya sea de estado sólido o giratorio) toma un tiempo del orden de decenas de milisegundos Ver más Concurrencia La concurrencia ocurre cada vez que su sistema crea un nuevo subproceso, porque los subprocesos, por definición, son secuencias de control independientes. La multitarea en su sistema es compatible con subprocesos independientes. Múltiples usuarios son compatibles simultáneamente en su sistema mediante el uso de subprocesos. La simultaneidad también ocurre cada vez que su sistema se ejecuta en más de un procesador, ya sea que esos procesadores estén empaquetados por separado o como procesadores de múltiples núcleos. La concurrencia es uno de los conceptos más importantes que un arquitecto debe comprender y uno de los temas menos enseñados en los cursos de informática. La concurrencia se refiere a las operaciones que ocurren en paralelo. Escenario Ejemplo de un escenario concreto: 500 users Initiate 2,000 request in 30-second interval Normal operations Processes all requests Average latency of 2 seconds 500 usuarios inician 2.000 solicitudes en un intervalo de 30 segundos, en condiciones normales de funcionamiento. El sistema procesa todas las solicitudes con una latencia promedio de dos segundos. PerformanceTactics Control Resource Demand ManageResources Manage Work RequestsLimit Event Response Prioritize Events Reduce Computational Overhead Bound Execution Times Increase Efficiency Increase ResourcesIntroduce Concurrency Maintain Multiple Copies of Computationes Maintain Multiple Copies of Data Bound Queue Sizes Schedule Resources Para ampliar el detalle de cada táctica, cómo se aplica y su significado, te invitamos a consultar el siguiente libro: Bass, L., Clements, P., &amp; Kazman, R. (2022). Software architecture in practice (4th ed.). SEI / Addison-Wesley. Los cálculos toman un tiempo del orden de miles de nanosegundos. El acceso a la red toma un tiempo que va desde cientos de microsegundos dentro del mismo centro de datos hasta más de 100 milisegundos para mensajes intercontinentales. El acceso al disco (ya sea de estado sólido o giratorio) toma un tiempo del orden de decenas de milisegundos. El tiempo debe tenerse en cuenta al diseñar su sistema para el rendimiento.

---

## P5 — Interoperabilidad

INTEROPERABILIDAD (INTEROPERABILITY) INTEROPERABILIDAD – INTEROPERABILITY Definición La interoperabilidad es la capacidad de un sistema para interactuar con otros sistemas de manera efectiva, independientemente de sus diferencias en tecnologías, lenguajes, plataformas o protocolos.   Esta característica es crucial para permitir la integración y el intercambio de información entre componentes o sistemas heterogéneos, facilitando la colaboración y el cumplimiento de objetivos comunes en un entorno diverso. Escenarios Tácticas ESCENARIOS Seguridad – Security

Ejemplo de un Escenario concreto Un hospital desea implementar un sistema de gestión de pacientes que pueda integrarse con los sistemas de facturación, laboratorios externos y el portal de citas en línea para garantizar que los datos fluyan de manera uniforme entre todos los sistemas ¡Ver más! Escenario Artefacto Fuente del estímulo Estímulo Entorno Escenario TÁCTICAS Las tácticas de arquitectura son estrategias que ayudan a lograr objetivos específicos relacionados con los atributos de calidad. En el caso de la interoperabilidad, las tácticas se centran en facilitar la integración y comunicación entre sistemas. Es importante nombrar que no sólo basta con comunicarse, por el contrario, la información debe entenderse por parte del receptor y procesarse; esto garantiza que se cumpla a cabalidad la interoperabilidad. ¡Ver más! Discover Services Esta categoría de tácticas aborda cómo los sistemas encuentran y acceden a servicios en un entorno distribuido. Las tácticas incluyen: Ejemplo Orchestrate Estas tácticas se centran en cómo los sistemas coordinan múltiples servicios para completar una tarea más compleja; estas incluyen: Ejemplo Transformación de datos Tailor Interface Ejemplo Adaptadores Esta categoría se centra en cómo se diseñan y adaptan las interfaces para facilitar la interacción entre sistemas heterogéneos. Las tácticas son: ​ Interfaces estandarizadas​ Diseñar interfaces que sigan estándares comunes para garantizar la interoperabilidad desde el principio. Medidas de respuesta:  



Tiempo de respuesta: El sistema debe procesar y almacenar los datos en menos de 2 segundos. El sistema del hospital interpreta correctamente el formato HL7. El sistema de gestión de pacientes del hospital, que debe recibir y procesar la información del laboratorio Se notifica al médico responsable a través del portal de citas Antes de comenzar el diseño de la arquitectura, es importante determinar el alcance del sistema: qué hay dentro y qué hay fuera del sistema que está creando y con qué entidades externas interactuará el sistema. Este contexto se puede representar usando un diagrama de contexto del sistema. Los resultados del laboratorio se almacenan en la base de datos del hospital. El sistema de laboratorio externo realiza una solicitud para enviar los resultados de análisis de un paciente al sistema de gestión del hospital Control centralizado Un componente central (como un orquestador) controla la secuencia de interacciones entre servicios para cumplir un flujo de trabajo.​ Convertir datos de un formato a otro para asegurar que sistemas con diferentes especificaciones puedan comunicarse Componentes que traducen entre interfaces o protocolos incompatibles para habilitar la comunicación.​ Control descentralizado Los propios servicios participan en la coordinación, cada uno interactuando con otros según reglas predefinidas.​ Luego, las estructuras resultantes se utilizan para guiar el proyecto de muchas formas.Sirven como base para educar a un nuevo miembro del proyecto. Antes de comenzar el diseño de la arquitectura, es importante determinar el alcance del sistema: qué hay dentro y qué hay fuera del sistema que está creando y con qué entidades externas interactuará el sistema. Este contexto se puede representar usando un diagrama de contexto del sistema. Descripción general de la actividad de diseño de arquitectura En el diseño arquitectónico, convertimos las decisiones sobre los impulsores arquitectónicos en estructuras. Los drivers arquitectónicos comprenden requisitos significativos desde el punto de vista arquitectónico (ASR), pero también incluyen funcionalidad, restricciones, preocupaciones arquitectónicas y propósito de diseño. Compatibilidad:  Debe garantizar el cumplimiento de los estándares HL7 sin necesidad de ajustes manuales. AQUí va la imagen AQUí va la imagen Operación normal en un entorno de red local con conexión segura a internet. Monitoreo y gestión del flujo Establecer mecanismos para monitorear y ajustar dinámicamente la ejecución de flujos de trabajo según las condiciones del entorno. Precisión: La información debe integrarse sin errores en el perfil del paciente correspondiente. Una solicitud de transferencia de datos (en formato HL7) se envía al sistema del hospital.

---

## Anotaciones (NO son del curso; conocimiento complementario o hallazgo de la extracción)

1. **P1 usa el Reto 1 como ejemplo trabajado de ASR** y prioriza explícitamente los atributos:
   latencia = **prioridad alta** (porque el enunciado la especificó), seguridad = baja (*no se consideró*),
   disponibilidad = baja (*no se explicitó*, meta 90 %). Es el modelo de razonamiento que el profesor
   espera: **el atributo se prioriza por lo que el enunciado exige, y lo demás se documenta como no priorizado**.
   Es la lección directa para la justificación del «atributo de calidad más importante» del Reto 2.
2. **Escenario de calidad (P1):** los campos que usa son *Actor · Estímulo · Ambiente · Artefacto · Respuesta esperada*
   (+ *Unidad*, *Prioridad*). Bass et al. usan *fuente, estímulo, artefacto, entorno, respuesta, medida de respuesta*;
   aquí «Actor» = fuente y «Respuesta esperada» incluye la medida. Conviene usar **un solo vocabulario** en el entregable.
3. **Tres estados de operación (P1):** *normal*, *estrés/alta carga* y *operación mínima/degradada*. Útil para el Reto 2
   (1000 eventos en 30 s es el estado de estrés).
4. **Errores o ambigüedades del material:**
   - P2 cierra con «la disponibilidad está estrechamente relacionada con la **seguridad**, que se ocupa de evitar que el
     sistema entre en un estado peligroso». Eso describe **safety** (seguridad funcional/física), no **security**
     (seguridad de la información). La traducción al español fusiona los dos sentidos; en el Bass original son atributos distintos.
   - P5 conserva el marcador de borrador literal **«AQUí va la imagen»** (×2): hay contenido sin terminar.
   - P5 repite al final un bloque de ADD («Descripción general de la actividad de diseño de arquitectura…») que no
     tiene relación con interoperabilidad: texto pegado de P1.
   - P3 da como escenario «500 usuarios inician 2000 solicitudes en 30 s, latencia media 2 s»: es **el mismo orden de
     magnitud del Reto 2** (1000 eventos / 30 s). Probable pista del profesor, pero no lo dice.
   - P1 fija la disponibilidad del ping-pong en «90 %»; el otro ejemplo habla de «99,9 %». Son ejemplos distintos, no contradicción.
5. **Interoperabilidad (P5)** llega con 3 categorías de tácticas: *Discover Services*, *Orchestrate* (control centralizado
   vs. descentralizado; monitoreo y gestión del flujo) y *Tailor Interface* (transformación de datos, adaptadores, interfaces
   estandarizadas). El ejemplo es un hospital con HL7 (sector salud), no financiero.
6. **Relevancia para el Reto 2:** el enunciado prioriza *desempeño* y *disponibilidad* (mensaje de bienvenida del módulo),
   no interoperabilidad ni seguridad; P5 y el video de seguridad son contexto, no insumo directo del reto.
