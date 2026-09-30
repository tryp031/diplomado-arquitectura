# Tácticas de Desplegabilidad — deck oficial del Módulo 2

> **Tipo:** `material-oficial` (Recursos complementarios, Brightspace, Unidad 3 de 5).
> **Fuente:** `TacticasDesplegabilidad.pptx` — Bass, Clements, Kazman, *Software Architecture in Practice*, 4th ed. (citado en el propio deck).
> **Extraído:** 2026-09-30, texto de las láminas tal cual. Se tradujo del inglés con traducción automática en el deck original (hay frases torpes).
> **Límite de la extracción:** solo texto. Los diagramas, figuras y tablas dibujadas como imagen NO están; las láminas que quedan vacías o con solo título dependen de una imagen.
> **Este archivo no se edita.** Las notas y críticas van en `Aportes/`.

---

## Lámina 1

DESPLEGABILIDAD

(DEPLOYABILITY)

## Lámina 2

Desplegabilidad - Deployability

En los "viejos tiempos", los releases eran poco frecuentes: una gran cantidad de cambios se agrupaban en liberaciones y se programaban. Un release contendría nuevas funciones y correcciones de errores. Un release por mes, por trimestre o incluso por año era común. Las presiones competitivas en muchos dominios, con el cargo liderado por el comercio electrónico, dieron como resultado la necesidad de ciclos de lanzamiento mucho más cortos.

En estos contextos, las liberaciones pueden ocurrir en cualquier momento, posiblemente cientos de ellos por día, y cada uno puede ser realizado por un equipo diferente dentro de una organización. Ser capaz de publicar con frecuencia significa que las correcciones de errores en particular no tienen que esperar hasta el próximo lanzamiento programado, sino que pueden realizarse y publicarse tan pronto como se descubra y corrija un error.

Importancia

## Lámina 3

Desplegabilidad - Deployability

La capacidad de Desplegabilidad se refiere a una propiedad del software que indica que puede desplegarse, es decir, asignarse a un entorno para su ejecución, dentro de una cantidad de tiempo y esfuerzo predecible y aceptable. Además, si la nueva implementación no cumple con sus especificaciones, puede revertirse, nuevamente dentro de una cantidad de tiempo y esfuerzo predecible y aceptable.

El atributo de calidad de la capacidad de prueba  sin duda juega un papel fundamental en el despliegue continuo, y el arquitecto puede proporcionar un soporte crítico para el despliegue continua al garantizar que el sistema sea comprobable, en todas las formas que se acaban de mencionar.

Definición

## Lámina 4

Desplegabilidad - Deployability

¿Cómo llega a su host (es decir, push, donde las actualizaciones implementadas no se solicitan, o pull, donde los usuarios o administradores deben solicitar actualizaciones explícitamente)?

¿Cómo se integra en un sistema existente? ¿Se puede hacer esto mientras se está ejecutando el sistema existente?

¿Cuál es el medio, como DVD, unidad USB o entrega por Internet?

¿Cuál es el paquete (p. ej., ejecutable, aplicación, complemento)?

¿Cuál es la integración resultante en un sistema existente?

¿Cuál es la eficiencia de ejecutar el proceso? ¿Cuál es la controlabilidad del proceso?

Retos en el Despliegue de Software

## Lámina 5

Desplegabilidad - Deployability

Los arquitectos se preocupan principalmente por el grado en que la arquitectura soporta despliegues que son:

Granulares. Los despliegues pueden ser de todo el sistema o de elementos dentro de un sistema. Si la arquitectura proporciona opciones para una implementación más detallada, se pueden reducir ciertos riesgos.

Controlables. La arquitectura debe proporcionar la capacidad de implementar en diferentes niveles de granularidad, monitorear el funcionamiento de las unidades desplegadas y revertir las implementaciones fallidas.

Eficientes. La arquitectura debe admitir una implementación rápida (y, si es necesario, un rollback) con un nivel razonable de esfuerzo.

Retos en el Despliegue de Software

## Lámina 6

ESCENARIO

## Lámina 7

Desplegabilidad - Deployability

Escenario General

Portion of Scenario

Description

Possible Values

Source

The trigger for the deployment

End user, developer, system administrator, operations personnel, component marketplace, product owner.

Stimulus

What causes the trigger

A new element is available to be deployed. This is typically a request to replace a software element with a new version (e.g., fix a defect, apply a security patch, upgrade to the latest release of a component or framework, upgrade to the latest version of an internally produced element).

New element is approved for incorporation.

An existing element/set of elements needs to be rolled back.

## Lámina 8

Desplegabilidad - Deployability

Escenario General

Portion of Scenario

Description

Possible Values

Artifacts

What is to be changed

Specific components or modules, the system’s platform, its user interface, its environment, or another system with which it interoperates. Thus the artifact might be a single software element, multiple software elements, or the entire system.

Environment

Staging, production (or a specific subset of either)

Full deployment.

Subset deployment to a specified portion of users, VMs, containers, servers, platforms.

Response

What should happen

Incorporate the new components.

Deploy the new components.

Monitor the new components.

Roll back a previous deployment.

## Lámina 9

Desplegabilidad - Deployability

Escenario General

Portion of Scenario

Description

Possible Values

Response measure

A measure of cost, time, or process effectiveness for a deployment, or for a series of deployments over time

Cost in terms of:

Number, size, and complexity of affected artifacts

Average/worst-case effort

Elapsed clock or calendar time

Money (direct outlay or opportunity cost)

New defects introduced

Extent to which this deployment/rollback affects other functions or quality attributes.

Number of failed deployments.

Repeatability of the process.

Traceability of the process.

Cycle time of the process.

## Lámina 10

Desplegabilidad - Deployability

Ejemplo de un Escenario concreto

## Lámina 11

TÁCTICAS

## Lámina 12

Desplegabilidad - Deployability

Tácticas

Las tácticas para la capacidad de Despliegue en muchos casos, serán proporcionadas al menos en parte, por infraestructura de CI/CD (integración continua/implementación continua) que se compra en lugar de construir. En tal caso, su trabajo como arquitecto suele ser elegir y evaluar (en lugar de implementar) las tácticas de despliegue correctas y la combinación correcta de las mismas.

## Lámina 13

Desplegabilidad - Deployability

Tácticas - Manage Deployment Pipeline

Scale Rollouts: En lugar de implementar a toda la base de usuarios, los lanzamientos escalados implementan una nueva versión de un servicio gradualmente, a subconjuntos controlados de la población de usuarios, a menudo sin notificación explícita a esos usuarios. (El resto de la base de usuarios continúa usando la versión anterior del servicio). Al lanzar gradualmente, los efectos de las nuevas implementaciones pueden monitorearse y medirse y, si es necesario, revertirse. Esta táctica minimiza el posible impacto negativo de implementar un servicio defectuoso. Requiere un mecanismo arquitectónico (que no forma parte del servicio que se está implementando) para enrutar una solicitud de un usuario al servicio nuevo o antiguo, según la identidad de ese usuario.

## Lámina 14

Desplegabilidad - Deployability

Tácticas - Manage Deployment Pipeline

Roll back:  Si se descubre que una implementación tiene defectos o no cumple con las expectativas del usuario, entonces se puede "revertir" a su estado anterior. Dado que las implementaciones pueden implicar múltiples actualizaciones coordinadas de múltiples servicios y sus datos, el mecanismo de reversión debe poder realizar un seguimiento de todos estos, o debe poder revertir las consecuencias de cualquier actualización realizada por un despliegue, idealmente de manera totalmente automatizada.

## Lámina 15

Desplegabilidad - Deployability

Tácticas - Manage Deployment Pipeline

Script deployment commands:  Las implementaciones suelen ser complejas y requieren muchos pasos para llevarse a cabo y organizarse con precisión. Por este motivo, la implementación suele estar programada. Estos scripts de implementación deben tratarse como código: documentados, revisados, probados y controlados por versión. Un motor de scripting ejecuta la secuencia de comandos de implementación automáticamente, ahorrando tiempo y minimizando las oportunidades de error humano.

## Lámina 16

Desplegabilidad - Deployability

Tácticas - Manage Deployed System

Manage service interactions:  Esta táctica se adapta al despliegue y ejecución simultáneas de múltiples versiones de los servicios del sistema. Se pueden dirigir varias solicitudes de un cliente a cualquiera de las versiones en cualquier secuencia. Sin embargo, tener varias versiones del mismo servicio en funcionamiento puede generar incompatibilidades de versión. En tales casos, las interacciones entre los servicios deben ser mediadas para evitar de manera proactiva las incompatibilidades de versión. Esta táctica es una estrategia de gestión de recursos, obviando la necesidad de replicar completamente los recursos para implementar por separado las versiones antiguas y nuevas.

## Lámina 17

Desplegabilidad - Deployability

Tácticas - Manage Deployed System

Package dependencies:  Esta táctica empaqueta un elemento junto con sus dependencias para que se desplieguen juntos y para que las versiones de las dependencias sean coherentes a medida que el elemento pasa de desarrollo a producción. Las dependencias pueden incluir bibliotecas, versiones del sistema operativo y contenedores de utilidades (por ejemplo, sidecar, malla de servicio). Tres formas de empaquetar dependencias son usar contenedores, pods o máquinas virtuales.

## Lámina 18

Desplegabilidad - Deployability

Tácticas - Manage Deployed System

Feature toggle:  Incluso cuando su código se prueba por completo, es posible que encuentre problemas después de implementar nuevas funciones. Por esa razón, es conveniente poder integrar un "interruptor de apagado" (o interruptor de función) para nuevas funciones. El interruptor de interrupción desactiva automáticamente una función en su sistema en tiempo de ejecución, sin obligarlo a iniciar una nueva implementación. Esto brinda la capacidad de controlar las funciones implementadas sin el costo y el riesgo de volver a implementar los servicios.

## Lámina 19

Desplegabilidad - Deployability

Tácticas - Manage Deployed System

Feature toggle

Fuente: Martin Fowler – Feature Toggles (Feature Flags)

## Lámina 20

PATRONES

## Lámina 21

Desplegabilidad - Deployability

Patrones

Los patrones para Despliegue se pueden organizar en dos categorías. La primera categoría contiene patrones para estructurar los servicios que se desplegarán. La segunda categoría contiene patrones sobre cómo desplegar los servicios, que se pueden analizar en dos amplias subcategorías: todo o nada o implementación parcial.

## Lámina 22

Desplegabilidad - Deployability

Patrones - Structuring Services

Microservicios: El patrón de arquitectura de microservicios estructura el sistema como una colección de servicios desplegables de forma independiente que se comunican solo a través de mensajes a través de interfaces de servicio. No se permite ninguna otra forma de comunicación entre procesos: sin enlaces directos, sin lecturas directas del almacén de datos de otro equipo, sin modelo de memoria compartida, sin puertas traseras de ningún tipo. Los servicios generalmente no tienen estado y (debido a que los desarrolla un solo equipo relativamente pequeño) son relativamente pequeños, de ahí el término microservicio. Las dependencias de servicio son acíclicas. Una parte integral de este patrón es un servicio de descubrimiento para que los mensajes puedan enrutarse adecuadamente.

## Lámina 23

Desplegabilidad - Deployability

Patrones - Structuring Services

Beneficios:

Se reduce el tiempo de comercialización. Dado que cada servicio es pequeño y se puede implementar de forma independiente, se puede implementar una modificación de un servicio sin coordinarse con los equipos que poseen otros servicios.

Cada equipo puede elegir sus propias opciones de tecnología para su servicio, siempre que las opciones de tecnología admitan el paso de mensajes. No se necesita coordinación con respecto a las versiones de la biblioteca o los lenguajes de programación. Esto reduce los errores debidos a las incompatibilidades que surgen durante la integración.

## Lámina 24

Desplegabilidad - Deployability

Patrones - Structuring Services

Beneficios:

Los servicios se escalan más fácilmente que las aplicaciones de granularidad más gruesa. Dado que cada servicio es independiente, agregar dinámicamente instancias del servicio es sencillo. De esta manera, la oferta de servicios puede adaptarse más fácilmente a la demanda.

## Lámina 25

Desplegabilidad - Deployability

Patrones - Structuring Services

Tradeoffs:

La sobrecarga aumenta, en comparación con la comunicación en memoria, porque toda la comunicación entre servicios se produce a través de mensajes a través de una red. Esto se puede mitigar en cierta medida mediante el uso del patrón de malla de servicio, que restringe la implementación de algunos servicios en el mismo host para reducir el tráfico de red. Además, debido a la naturaleza dinámica de las implementaciones de microservicios, los servicios de descubrimiento se utilizan mucho, lo que aumenta la sobrecarga. En última instancia, esos servicios de descubrimiento pueden convertirse en un cuello de botella en el rendimiento.

## Lámina 26

Desplegabilidad - Deployability

Patrones - Structuring Services

Tradeoffs:

Los microservicios son menos adecuados para transacciones complejas debido a la dificultad de sincronizar actividades entre sistemas distribuidos.

La libertad de cada equipo para elegir su propia tecnología tiene un costo: la organización debe mantener esas tecnologías y la base de experiencia requerida.

El control intelectual del sistema total puede ser difícil debido a la gran cantidad de microservicios. Esto introduce un requisito para catálogos y bases de datos de interfaces para ayudar a mantener el control intelectual. Además, el proceso de combinar adecuadamente los servicios para lograr el resultado deseado puede ser complejo y sutil.

## Lámina 27

Desplegabilidad - Deployability

Patrones - Structuring Services

Tradeoffs:

Diseñar los servicios para que tengan las responsabilidades adecuadas y un nivel adecuado de granularidad es una tarea de diseño formidable.

Para lograr la capacidad de implementar versiones de forma independiente, la arquitectura de los servicios debe estar diseñada para permitir esa estrategia de implementación.

Las organizaciones que han empleado mucho el patrón de arquitectura de microservicio incluyen Google, Netflix, PayPal, Twitter, Facebook y Amazon.

## Lámina 28

Desplegabilidad - Deployability

Patrones - Complete Replacement of Services

Suponga que hay N instancias del Servicio A y desea reemplazarlas con N instancias de una nueva versión del Servicio A, sin dejar instancias de la versión original. Desea hacer esto sin reducir la calidad del servicio para los clientes del servicio, por lo que siempre debe haber N instancias del servicio en ejecución.

## Lámina 29

Desplegabilidad - Deployability

Patrones - Complete Replacement of Services

Blue/green: En este tipo de despliegue, se crearían N nuevas instancias del servicio y cada una se completaría con el nuevo Servicio A (llamémoslas instancias verdes). Después de instalar las N instancias del nuevo Servicio A, el servidor DNS o el servicio de descubrimiento se cambiaría para apuntar a la nueva versión del Servicio A. Una vez que se determina que las nuevas instancias funcionan satisfactoriamente, entonces y solo entonces se eliminan las N instancias del Servicio A original. Antes de este punto límite, si se encuentra un problema en la nueva versión, es una simple cuestión de volver al original (los servicios azules) con poca o ninguna interrupción..

## Lámina 30

Desplegabilidad - Deployability

Patrones - Complete Replacement of Services

Blue/green

## Lámina 31

Desplegabilidad - Deployability

Patrones - Complete Replacement of Services

Rolling upgrade: Una actualización gradual reemplaza las instancias del Servicio A con instancias de la nueva versión del Servicio A, una a la vez. (En la práctica, puede reemplazar más de una instancia a la vez, pero solo una pequeña fracción se reemplaza en un solo paso). Los pasos de la actualización continua son los siguientes:

Asigne recursos para una nueva instancia del Servicio A (por ejemplo, una máquina virtual).

Instale y registre la nueva versión del Servicio A.

Comience dirigir solicitudes a la nueva versión del Servicio A.

Elija una instancia del antiguo Servicio A, permita que complete cualquier procesamiento activo y luego destruya esa instancia.

Repita los pasos anteriores hasta que se hayan reemplazado todas las instancias de la versión anterior.

## Lámina 32

Desplegabilidad - Deployability

Patrones - Complete Replacement of Services

Un diagrama de flujo del patrón de Rolling Upgrade (actualización  gradual) implementado por la herramienta Asgard de Netflix

## Lámina 33

Desplegabilidad - Deployability

Patrones - Complete Replacement of Services

Blue/green deployment

Rolling upgrade deployment

## Lámina 34

Desplegabilidad - Deployability

Patrones - Complete Replacement of Services

Beneficios:

El beneficio de estos patrones es la capacidad de reemplazar completamente las versiones implementadas de los servicios sin tener que poner el sistema fuera de servicio, lo que aumenta la disponibilidad del sistema.

## Lámina 35

Desplegabilidad - Deployability

Patrones - Complete Replacement of Services

Tradeoffs:

La utilización máxima de recursos para un enfoque azul/verde es de 2N instancias, mientras que la utilización máxima para una actualización continua es de N + 1 instancias. En cualquier caso, se deben adquirir los recursos para albergar estas instancias. Antes de la adopción generalizada de la computación en la nube, la adquisición significaba la compra: una organización tenía que comprar computadoras físicas para realizar la actualización.

## Lámina 36

Desplegabilidad - Deployability

Patrones - Complete Replacement of Services

Tradeoffs:

Suponga que detecta un error en el nuevo Servicio A cuando lo implementa. A pesar de todas las pruebas que realizó en los entornos de desarrollo, integración y ensayo, cuando su servicio se implementa en producción, aún puede haber errores latentes. Si está utilizando la implementación azul/verde, cuando descubra un error en el nuevo Servicio A, es posible que se hayan eliminado todas las instancias originales y que la reversión a la versión anterior lleve un tiempo considerable. Por el contrario, una actualización gradual puede permitirle descubrir un error en la nueva versión del servicio mientras las instancias de la versión anterior aún están disponibles.

## Lámina 37

Desplegabilidad - Deployability

Patrones - Complete Replacement of Services

Tradeoffs:

Desde la perspectiva de un cliente, si está utilizando el modelo de implementación azul/verde, entonces, en cualquier momento, la nueva versión o la versión anterior estarán activas, pero no ambas. Si está utilizando el patrón de actualización gradual, ambas versiones están activas simultáneamente. Esto introduce la posibilidad de dos tipos de problemas: inconsistencia temporal y desajuste de interfaz.

## Lámina 38

Desplegabilidad - Deployability

Patrones - Complete Replacement of Services

Tradeoffs:

Temporal inconsistency - Inconsistencia temporal. En una secuencia de solicitudes del Cliente C al Servicio A, algunas pueden ser atendidas por la versión anterior del servicio y otras pueden ser atendidas por la nueva versión. Si las versiones se comportan de manera diferente, esto puede causar que el Cliente C produzca resultados erróneos, o al menos inconsistentes. (Esto se puede prevenir usando la táctica de administrar interacciones de servicio).

## Lámina 39

Desplegabilidad - Deployability

Patrones - Complete Replacement of Services

Tradeoffs:

Interface mismatch - Desajuste de la interfaz. Si la interfaz de la nueva versión del Servicio A es diferente de la interfaz de la versión anterior del Servicio A, las invocaciones de los clientes del Servicio A que no se han actualizado para reflejar la nueva interfaz producirán resultados impredecibles. Esto se puede evitar ampliando la interfaz pero sin modificar la interfaz existente y utilizando el patrón de mediador para traducir de la interfaz extendida a una interfaz interna que produzca el comportamiento correcto.

## Lámina 40

Desplegabilidad - Deployability

Patrones - Partial Replacement of Service

A veces no es deseable cambiar todas las instancias de un servicio. Los patrones de implementación parcial tienen como objetivo proporcionar múltiples versiones de un servicio simultáneamente para diferentes grupos de usuarios; se utilizan para fines tales como control de calidad (pruebas canarias) y pruebas de marketing (pruebas A/B).

## Lámina 41

Desplegabilidad - Deployability

Patrones - Partial Replacement of Service

Canary Testing: Antes de lanzar una nueva versión, es prudente probarla en el entorno de producción, pero con un conjunto limitado de usuarios. Canary testing designa a un pequeño grupo de usuarios que probarán la nueva versión. A veces, estos probadores son los llamados usuarios avanzados o usuarios de flujo de vista previa de fuera de su organización que es más probable que ejerzan rutas de código y casos extremos que los usuarios típicos pueden usar con menos frecuencia. Los usuarios pueden o no saber que están siendo utilizados como conejillos de indias, es decir, canarios. Otro enfoque es utilizar probadores dentro de la organización que está desarrollando el software.

## Lámina 42

Desplegabilidad - Deployability

Patrones - Partial Replacement of Service

Canary Testing

## Lámina 43

Desplegabilidad - Deployability

Patrones - Partial Replacement of Service

Beneficios:

Canary testing permite a los usuarios reales "explotar" el software de formas que las pruebas simuladas no pueden. Esto permite que la organización que implementa el servicio recopile datos "en uso" y realice experimentos controlados con un riesgo relativamente bajo.

Canary testing incurre en costos de desarrollo adicionales mínimos, porque el sistema que se está probando está en camino a la producción de todos modos.

Canary testing minimiza la cantidad de usuarios que pueden estar expuestos a un defecto grave en el nuevo sistema.

## Lámina 44

Desplegabilidad - Deployability

Patrones - Partial Replacement of Service

Tradeoffs:

Canary testing requiere planificación y recursos adicionales por adelantado, y es necesario formular una estrategia para evaluar los resultados de las pruebas.

Si las pruebas canary están dirigidas a usuarios avanzados, esos usuarios deben identificarse y la nueva versión se les debe enrutar.

## Lámina 45

Desplegabilidad - Deployability

Patrones - Partial Replacement of Service

A/B Testing – Pruebas A/B: Los especialistas en marketing utilizan las Pruebas A/B para realizar un experimento con usuarios reales para determinar cuál de varias alternativas produce los mejores resultados comerciales. Un número pequeño pero significativo de usuarios recibe un trato diferente al resto de los usuarios. La diferencia puede ser menor, como un cambio en el tamaño de la fuente o el diseño del formulario, o puede ser más significativa. Al igual que en las pruebas Canary, los servidores DNS y las configuraciones del servicio de descubrimiento están configurados para enviar solicitudes de clientes a diferentes versiones. En las pruebas A/B, se monitorean las diferentes versiones para ver cuál ofrece la mejor respuesta desde una perspectiva comercial.

## Lámina 46

Desplegabilidad - Deployability

Patrones - Partial Replacement of Service

Beneficios:

Las pruebas A/B permiten a los equipos de marketing y desarrollo de productos realizar experimentos y recopilar datos de usuarios reales.

Las pruebas A/B pueden permitir la selección de usuarios en función de un conjunto arbitrario de características.

## Lámina 47

Desplegabilidad - Deployability

Patrones - Partial Replacement of Service

Tradeoffs:

Las pruebas A/B requieren la implementación de alternativas, una de las cuales será descartada.

Las diferentes clases de usuarios y sus características deben identificarse por adelantado.

## Lámina 48

Desplegabilidad - Deployability

Lecturas Recomendadas

Feature Toggles - Martin Fowler

From Big Bang to Canary - Medium

## Lámina 49

Bibliografía

Len Bass, Paul Clements, Rick Kazman. Software Architecture in Practice. 4th Edition. SEI / Addison-Wesley, 2022​

## Lámina 50

_(sin texto: la lámina es una imagen)_
