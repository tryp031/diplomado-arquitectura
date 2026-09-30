# Tácticas de Disponibilidad — deck oficial del Módulo 2

> **Tipo:** `material-oficial` (Recursos complementarios, Brightspace, Unidad 3 de 5).
> **Fuente:** `TacticasDisponibilidad.pptx` — Bass, Clements, Kazman, *Software Architecture in Practice*, 4th ed. (citado en el propio deck).
> **Extraído:** 2026-09-30, texto de las láminas tal cual. Se tradujo del inglés con traducción automática en el deck original (hay frases torpes).
> **Límite de la extracción:** solo texto. Los diagramas, figuras y tablas dibujadas como imagen NO están; las láminas que quedan vacías o con solo título dependen de una imagen.
> **Este archivo no se edita.** Las notas y críticas van en `Aportes/`.

---

## Lámina 1

DISPONIBILIDAD

(AVAILABILITY)

## Lámina 2

Disponibilidad - Availability

Definición

La Disponibilidad se refiere a la propiedad del software de estar ahí listo para realizar su tarea cuando usted lo necesita.

La Disponibilidad también abarca la capacidad de un sistema para enmascarar o reparar defectos de modo que no se conviertan en fallas, asegurando así que el período de interrupción del servicio acumulativo no exceda un valor requerido durante un intervalo de tiempo específico.

Una falla es la desviación del sistema de su especificación, donde esa desviación es visible externamente. Determinar que ha ocurrido una falla requiere algún observador externo en el entorno.

## Lámina 3

Disponibilidad - Availability

Definición

La causa de una falla (failure) se llama defecto (fault). Un defecto puede ser interno o externo al sistema bajo consideración. Los estados intermedios entre la ocurrencia de un defecto y la ocurrencia de una falla se denominan errores. Los defectos se pueden prevenir, tolerar, eliminar o pronosticar.

## Lámina 4

Disponibilidad - Availability

Relación con otros Atributos de Calidad

La Disponibilidad está estrechamente relacionada con la seguridad, pero claramente distinta de ella. Un ataque de denegación de servicio está diseñado explícitamente para hacer que un sistema falle, es decir, para que no esté disponible.

La Disponibilidad también está estrechamente relacionada con el Rendimiento, ya que puede ser difícil saber cuándo un sistema ha fallado y cuándo simplemente responde de manera extremadamente lenta. Finalmente, la disponibilidad está estrechamente relacionada con la Seguridad, que se ocupa de evitar que el sistema entre en un estado peligroso y de recuperar o limitar el daño cuando lo hace.

## Lámina 5

MÉTRICAS

## Lámina 6

Disponibilidad

¿Cómo se mide?

La Disponibilidad de un sistema se puede medir como la probabilidad de que proporcione los servicios especificados dentro de los límites requeridos durante un intervalo de tiempo especificado. Se utiliza una expresión bien conocida para derivar la disponibilidad de estado estable (que proviene del mundo del hardware):

MTBF/(MTBF + MTTR)

MTBF (Mean Time Between Failures): Tiempo medio entre fallas

MTTR (Mean Time To Repair): Tiempo medio de reparación.

Total Uptime / ( Total Uptime + Total Downtime) x 100

## Lámina 7

Disponibilidad

¿Cómo se mide?

Los tiempos de inactividad programados (cuando el sistema se pone fuera de servicio intencionalmente) no deben tenerse en cuenta al calcular la disponibilidad.

La Disponibilidad esperada de un sistema o servicio se expresa frecuentemente como un SLA. El SLA especifica el nivel de disponibilidad que se garantiza y, normalmente, las penalizaciones que sufrirá el proveedor si se infringe el SLA.

## Lámina 8

Disponibilidad

¿Cómo se mide?

El término Alta Disponibilidad generalmente se refiere a diseños que apuntan a una disponibilidad del 99,999 por ciento ("5 nueves") o más.

## Lámina 9

Disponibilidad

Ejemplo en AWS

Fuente: AWS S3 Storage Classes

## Lámina 10

Disponibilidad

Métricas relacionadas

Fuente: Attlasian – Incident Management - Common Metrics

## Lámina 11

ESCENARIO

## Lámina 12

Disponibilidad

Escenario General

## Lámina 13

Disponibilidad

Ejemplo de un Escenario concreto

Un servidor en una granja de servidores falla durante el funcionamiento normal y el sistema informa al operador y continúa funcionando sin tiempo de inactividad.

## Lámina 14

TÁCTICAS

## Lámina 15

Disponibilidad

Las Tácticas de Disponibilidad, están diseñadas para permitir que un sistema prevenga o soporte fallas del sistema para que el servicio que entrega siga cumpliendo con su especificación.

Tácticas

Las tácticas de disponibilidad tienen uno de tres propósitos: detección, recuperación o prevención de fallas.

## Lámina 16

Disponibilidad

Tácticas

## Lámina 17

Disponibilidad

Tácticas -  Fault Detection

Monitor: Este componente se utiliza para monitorear el estado de salud de varias otras partes del sistema: procesadores, procesos, E/S, memoria, etc. Un monitor del sistema puede detectar fallas o congestión en la red u otros recursos compartidos, como un ataque de denegación de servicio. Orquesta el software usando otras tácticas en esta categoría para detectar componentes que funcionan mal. Por ejemplo, el monitor del sistema puede iniciar pruebas automáticas o ser el componente que detecta marcas de tiempo defectuosas o latidos perdidos.

## Lámina 18

Disponibilidad

Tácticas -  Fault Detection

Ping/Echo. En esta táctica, se intercambia un par de mensajes de solicitud/respuesta asincrónicos entre nodos; se utiliza para determinar la accesibilidad y el retraso de ida y vuelta a través de la ruta de red asociada. Además, el eco indica que el componente al que se hizo ping está vivo. El ping a menudo lo envía un monitor del sistema. Ping/echo requiere que se establezca un umbral de tiempo; este umbral le dice al componente que hace ping cuánto tiempo debe esperar el eco antes de considerar que el componente al que se hizo ping ha fallado ("tiempo de espera agotado"). Las implementaciones estándar de ping/echo están disponibles para nodos interconectados a través del Protocolo de Internet (IP).

## Lámina 19

Disponibilidad

Tácticas -  Fault Detection

Heartbeat. Este mecanismo de detección de fallas emplea un intercambio periódico de mensajes entre un monitor del sistema y un proceso que se está monitoreando. Un caso especial de latido es cuando el proceso que se está monitoreando reinicia periódicamente el temporizador de vigilancia en su monitor para evitar que caduque y, por lo tanto, señale una falla. Para los sistemas en los que la escalabilidad es una preocupación, los gastos generales de transporte y procesamiento se pueden reducir incorporando mensajes de latidos a otros mensajes de control que se intercambian. La diferencia entre el latido del corazón y el ping/eco radica en quién tiene la responsabilidad de iniciar la verificación de estado: el monitor o el componente mismo.

## Lámina 20

Disponibilidad

Tácticas -  Fault Detection

Timestamp. Esta táctica se utiliza para detectar secuencias incorrectas de eventos, principalmente en sistemas de paso de mensajes distribuidos. Se puede establecer una marca de tiempo de un evento asignando el estado de un reloj local al evento inmediatamente después de que ocurra el evento. Los números de secuencia también se pueden usar para este propósito, ya que las marcas de tiempo en un sistema distribuido pueden ser inconsistentes entre diferentes procesadores.

## Lámina 21

Disponibilidad

Tácticas -  Fault Detection

Condition monitoring. Esta táctica implica verificar las condiciones en un proceso o dispositivo, o validar las suposiciones hechas durante el diseño. Al monitorear las condiciones, esta táctica evita que un sistema produzca un comportamiento defectuoso. El cálculo de checksums  es un ejemplo común de esta táctica. Sin embargo, el monitor en sí mismo debe ser simple (e, idealmente, demostrablemente correcto) para garantizar que no introduzca nuevos errores de software.

## Lámina 22

Disponibilidad

Tácticas -  Fault Detection

Sanity checking. Esta táctica verifica la validez o razonabilidad de operaciones específicas o salidas de un componente. Por lo general, se basa en el conocimiento del diseño interno, el estado del sistema o la naturaleza de la información bajo escrutinio. Se emplea con mayor frecuencia en las interfaces, para examinar un flujo de información específico.

## Lámina 23

Disponibilidad

Tácticas -  Fault Detection

Voting. Votar implica comparar resultados computacionales de múltiples fuentes que deberían estar produciendo los mismos resultados y, si no es así, decidir qué resultados usar. Esta táctica depende críticamente de la lógica de votación, que generalmente se realiza como un singleton simple, rigurosamente revisado y probado para que la probabilidad de error sea baja. Votar también depende críticamente de tener múltiples fuentes para evaluar.

## Lámina 24

Disponibilidad

Tácticas -  Fault Detection

Exception detection. Esta táctica se enfoca en la detección de una condición del sistema que altera el flujo normal de ejecución. Se puede refinar aún más de la siguiente manera:

System exceptions

Parameter fence

Parameter typing

Timeout

## Lámina 25

Disponibilidad

Tácticas -  Fault Detection

Self-test. Los componentes (o, más probablemente, los subsistemas completos) pueden ejecutar procedimientos para comprobar su correcto funcionamiento. Los procedimientos de autocomprobación pueden ser iniciados por el propio componente o invocados de vez en cuando por un monitor del sistema. Estos pueden implicar el empleo de algunas de las técnicas que se encuentran en el monitoreo de condiciones, como checksums (sumas de verificación)

## Lámina 26

Disponibilidad

Tácticas -  Fault Recovery - Preparation and repair

Redundant spare - Repuesto redundante. Esta táctica se refiere a una configuración en la que uno o más componentes duplicados pueden intervenir y hacerse cargo del trabajo si falla el componente principal. Esta táctica está en el corazón de los patrones de repuesto en caliente y repuesto en frío, que difieren principalmente en qué tan actualizado está el componente de respaldo en el momento de su toma de control.

## Lámina 27

Disponibilidad

Tácticas -  Fault Recovery - Preparation and repair

Rollback. Una reversión permite que el sistema vuelva a un buen estado anterior conocido (denominado "línea de reversión") (tiempo de reversión) al detectar una falla. Una vez que se alcanza el estado anterior, la ejecución puede continuar. Esta táctica a menudo se combina con la táctica de transacciones y la táctica de repuesto redundante para que, después de que se haya producido una reversión, una versión en espera del componente fallido se promueva al estado activo. La reversión depende de que una copia de un estado anterior (un punto de control) esté disponible para los componentes que se están revirtiendo.

## Lámina 28

Disponibilidad

Tácticas -  Fault Recovery - Preparation and repair

Exception handling - Manejo de excepciones. Una vez que se ha detectado una excepción, el sistema la manejará de alguna manera. Lo más fácil que puede hacer es simplemente colapsar, pero, por supuesto, esa es una idea terrible desde el punto de vista de la disponibilidad, la usabilidad, la capacidad de prueba y el sentido común. Hay posibilidades mucho más productivas.

El mecanismo empleado para el manejo de excepciones depende en gran medida del entorno de programación empleado, que va desde códigos de retorno de funciones simples (códigos de error) hasta el uso de clases de excepción que contienen información útil en la correlación de fallas, como el nombre de la excepción, el origen de la excepción y la causa de la excepción. El software puede usar esta información para enmascarar o reparar la falla.

## Lámina 29

Disponibilidad

Tácticas -  Fault Recovery - Preparation and repair

Software upgrade - Actualización de software. El objetivo de esta táctica es lograr actualizaciones en servicio para imágenes de código ejecutable de una manera que no afecte el servicio. Las estrategias incluyen lo siguiente:

Parche de función. Este tipo de parche, que se utiliza en la programación de procedimientos, emplea un enlazador/cargador incremental para almacenar una función de software actualizada en un segmento preasignado de la memoria de destino.

Parche de clase. Este tipo de actualización es aplicable para destinos que ejecutan código orientado a objetos, donde las definiciones de clase incluyen un mecanismo de puerta trasera que permite la adición en tiempo de ejecución de funciones y datos de miembros.

Actualización de software en servicio sin impacto (ISSU). Esto aprovecha la táctica de repuesto redundante para lograr actualizaciones del software y el esquema asociado que no afectan al servicio.

## Lámina 30

Disponibilidad

Tácticas -  Fault Recovery - Preparation and repair

Retry. La táctica de reintento supone que el error que provocó la falla es transitorio y que volver a intentar la operación puede conducir al éxito. Se usa en redes y en granjas de servidores donde las fallas son esperadas y comunes. Debe establecerse un límite en el número de reintentos que se intentan antes de que se declare un error permanente.

Ignore faulty behavior - Ignorar el comportamiento defectuoso. Esta táctica exige ignorar los mensajes enviados desde una fuente en particular cuando determinamos que esos mensajes son falsos. Por ejemplo, nos gustaría ignorar los mensajes que emanan de la falla en vivo de un sensor.

## Lámina 31

Disponibilidad

Tácticas -  Fault Recovery - Preparation and repair

Graceful degradation - Degradación agraciada. Esta táctica mantiene las funciones más críticas del sistema en presencia de fallas de los componentes, mientras descarta las funciones menos críticas. Esto se hace en circunstancias en las que fallas de componentes individuales reducen la funcionalidad del sistema, en lugar de causar una falla completa del sistema.

Reconfiguration - Reconfiguración. La reconfiguración intenta recuperarse de fallas mediante la reasignación de responsabilidades a los recursos o componentes (potencialmente restringidos) que quedaron en funcionamiento, mientras se mantiene la mayor funcionalidad posible.

## Lámina 32

Disponibilidad

Tácticas -  Fault Recovery - Reintroduction

Shadow - Sombra. Esta táctica se refiere a operar un componente actualizado en servicio o que falló anteriormente en un "modo oculto" durante un período de tiempo predefinido antes de revertir el componente a un rol activo. Durante esta duración, se puede monitorear su comportamiento para verificar que sea correcto y se puede repoblar su estado de forma incremental.

Resincronización de estados. Esta táctica de socia de la táctica de repuesto redundante. Cuando se usa con redundancia activa, una versión de la táctica de repuesto redundante, la resincronización de estado ocurre orgánicamente, ya que los componentes activos y de reserva reciben y procesan entradas idénticas en paralelo. En la práctica, los estados de los componentes activo y en espera se comparan periódicamente para garantizar la sincronización.

## Lámina 33

Disponibilidad

Tácticas -  Fault Recovery - Reintroduction

Nonstop forwarding - Reenvío continuo. Este concepto se originó en el diseño del enrutador y supone que la funcionalidad se divide en dos partes: el  supervisor o controlador (que gestiona la conectividad y la información de enrutamiento) y el plano de datos (que hace el trabajo real de enrutar los paquetes del remitente al receptor). Si un enrutador experimenta la falla de un supervisor activo, puede continuar reenviando paquetes a lo largo de rutas conocidas, con enrutadores vecinos, mientras se recupera y valida la información del protocolo de enrutamiento.

## Lámina 34

Disponibilidad

Tácticas -  Fault Prevention

Removal from service - Retiro del servicio. Esta táctica se refiere a colocar temporalmente un componente del sistema en un estado fuera de servicio con el fin de mitigar posibles fallas del sistema. Por ejemplo, un componente de un sistema puede quedar fuera de servicio y restablecerse para eliminar fallas latentes (como fugas de memoria, fragmentación o errores leves en un caché desprotegido) antes de que la acumulación de fallas alcance el nivel que afecta el servicio, lo que resulta en fallo de sistema. Otros términos para esta táctica son rejuvenecimiento de software y reinicio terapéutico. Si reinicia su computadora todas las noches, está practicando la eliminación del servicio.

## Lámina 35

Disponibilidad

Tácticas -  Fault Prevention

Transactions - Transacciones. Los sistemas destinados a servicios de alta disponibilidad aprovechan la semántica transaccional para garantizar que los mensajes asíncronos intercambiados entre componentes distribuidos sean atómicos, coherentes, aislados y duraderos, propiedades denominadas colectivamente "propiedades ACID". La realización más común de la táctica de transacciones es el protocolo de "compromiso en dos fases" (2PC). Esta táctica evita las condiciones de carrera causadas por dos procesos que intentan actualizar el mismo elemento de datos al mismo tiempo.

## Lámina 36

Disponibilidad

Tácticas -  Fault Prevention

Predictive Model - Modelo predictivo. Un modelo predictivo, cuando se combina con un monitor, se emplea para monitorear el estado de salud de un proceso del sistema para garantizar que el sistema esté funcionando dentro de sus parámetros operativos nominales y para tomar medidas correctivas cuando el sistema se acerca a un umbral crítico. Las métricas de desempeño operativo monitoreadas se utilizan para predecir la aparición de fallas; los ejemplos incluyen la tasa de establecimiento de la sesión (en un servidor HTTP), el cruce del umbral (monitoreo de marcas de agua altas y bajas para algunos recursos compartidos restringidos), estadísticas sobre el estado del proceso (por ejemplo, en servicio, fuera de servicio, en mantenimiento, inactivo) y estadísticas de longitud de la cola de mensajes.

## Lámina 37

Disponibilidad

Tácticas -  Fault Prevention

Exception prevention - Prevención de excepciones. Esta táctica se refiere a las técnicas empleadas con el fin de evitar que ocurran excepciones del sistema. El uso de clases de excepción, que permite que un sistema se recupere de forma transparente de las excepciones del sistema, se analizó anteriormente. Otros ejemplos de prevención de excepciones incluyen código de corrección de errores (utilizado en telecomunicaciones), tipos de datos abstractos como punteros inteligentes y el uso de envoltorios para evitar fallas como punteros colgantes o infracciones de acceso a semáforos. Los punteros inteligentes evitan las excepciones al verificar los límites de los punteros y al garantizar que los recursos se desasignen automáticamente cuando no hay datos que se refieran a ellos, lo que evita fugas de recursos.

## Lámina 38

Disponibilidad

Tácticas -  Fault Prevention

Increase competence set - Aumentar el conjunto de competencias. El conjunto de competencias de un programa es el conjunto de estados en los que es "competente" para operar. Por ejemplo, el estado cuando el denominador es cero está fuera del conjunto de competencias de la mayoría de los programas de división. Cuando un componente genera una excepción, indica que se ha descubierto a sí mismo fuera de su conjunto de competencias; en esencia, no sabe qué hacer y está tirando la toalla. Aumentar el conjunto de competencias de un componente significa diseñarlo para manejar más casos (fallas) como parte de su funcionamiento normal.

## Lámina 39

PATRONES

## Lámina 40

Disponibilidad

Patrones -  Redundant Spare

Active redundancy (hot spare): Para los componentes con estado, esto se refiere a una configuración en la que todos los nodos (activos o de repuesto redundantes) en un grupo de protección reciben y procesan entradas idénticas en paralelo, lo que permite que los repuestos redundantes mantengan un estado sincrónico con el nodo activo. Debido a que el repuesto redundante posee un estado idéntico al del procesador activo, puede tomar el relevo de un componente fallido en cuestión de milisegundos. El caso simple de un nodo activo y un nodo de repuesto redundante se conoce comúnmente como redundancia uno más uno. La redundancia activa también se puede utilizar para la protección de instalaciones, donde los enlaces de red activos y en espera se utilizan para garantizar una conectividad de red de alta disponibilidad.

## Lámina 41

Disponibilidad

Patrones -  Redundant Spare

Passive redundancy (warm spare): Para los componentes con estado, esto se refiere a una configuración en la que solo los miembros activos del grupo de protección procesan el tráfico de entrada. Una de sus funciones es proporcionar actualizaciones de estado periódicas a los repuestos redundantes. Debido a que el estado mantenido por los repuestos redundantes solo se acopla débilmente con el de los nodos activos en el grupo de protección (la falta de acoplamiento es una función del período de las actualizaciones de estado), los nodos redundantes se denominan como repuestos calientes.

## Lámina 42

Disponibilidad

Patrones -  Redundant Spare

Spare (cold spare): El repuesto en frío se refiere a una configuración en la que los repuestos redundantes permanecen fuera de servicio hasta que se produce una conmutación por error, momento en el cual se inicia un procedimiento de encendido y reinicio en el repuesto redundante antes de ponerlo en servicio. Debido a su bajo rendimiento de recuperación y, por lo tanto, a su alto tiempo medio de reparación, este patrón no se adapta bien a los sistemas que tienen requisitos de alta disponibilidad.

## Lámina 43

Disponibilidad

Patrones -  Redundant Spare

Beneficios

El beneficio de un repuesto redundante es un sistema que continúa funcionando correctamente después de solo un breve retraso en presencia de una falla. La alternativa es un sistema que deja de funcionar correctamente, o deja de funcionar por completo, hasta que se repara el componente defectuoso. Esta reparación podría llevar horas o días.

## Lámina 44

Disponibilidad

Patrones -  Redundant Spare

Tradeoffs

El tradeoff de cualquiera de estos patrones es el costo adicional y la complejidad en que se incurre al proporcionar un repuesto. El tradeoff entre las tres alternativas es el tiempo de recuperación de una falla versus el costo de tiempo de ejecución incurrido para mantener un repuesto actualizado. Un repuesto dinámico conlleva el costo más alto pero conduce al tiempo de recuperación más rápido, por ejemplo.

## Lámina 45

Disponibilidad

Patrones - TMR

Triple Modular Redundancy (TMR): Esta implementación ampliamente utilizada de la táctica de votación emplea tres componentes que hacen lo mismo. Cada componente recibe entradas idénticas y reenvía su salida a la lógica de votación, que detecta cualquier incoherencia entre los tres estados de salida. Ante una inconsistencia, el votante denuncia una falta. También debe decidir qué salida usar, y las diferentes instancias de este patrón usan diferentes reglas de decisión. Las opciones típicas son dejar que la mayoría gobierne o elegir algún promedio calculado de los resultados dispares.

## Lámina 46

Disponibilidad

Patrones - TMR

Beneficios

TMR es simple de entender e implementar. Es felizmente independiente de lo que podría estar causando resultados dispares, y solo se preocupa por tomar una decisión razonable para que el sistema pueda seguir funcionando.

Tradeoffs

Existe un tradeoff entre aumentar el nivel de replicación, lo que eleva el costo, y la disponibilidad resultante. En los sistemas que emplean TMR, la probabilidad estadística de que dos o más componentes fallen es muy pequeña, y tres componentes representan un punto óptimo entre la disponibilidad y el costo.

## Lámina 47

Disponibilidad

Patrones - Circuit breaker

## Lámina 48

Disponibilidad

Patrones - Circuit breaker

Circuit breaker: Una táctica de disponibilidad comúnmente utilizada es reintentar. En caso de que se agote el tiempo de espera o se produzca un error al invocar un servicio, el invocador simplemente vuelve a intentarlo, una y otra vez. Un circuit breaker evita que el invocador lo intente innumerables veces, esperando una respuesta que nunca llega. De esta manera, rompe el ciclo interminable de reintentos cuando considera que el sistema está lidiando con una falla. Esa es la señal para que el sistema comience a manejar la falla. Hasta que se "restablezca" la ruptura del circuito, las invocaciones subsiguientes regresarán inmediatamente sin transmitir la solicitud de servicio.

## Lámina 49

Disponibilidad

Patrones - Circuit breaker

Circuit breaker

Fuente: Martin Fowler – Circuit Breaker

## Lámina 50

Disponibilidad

Patrones - Circuit breaker

Beneficios

Este patrón puede eliminar de los componentes individuales la política sobre cuántos reintentos permitir antes de declarar una falla.

En el peor de los casos, los interminables reintentos infructuosos harían que el componente invocador fuera tan inútil como el componente invocado que falló. Este problema es especialmente agudo en los sistemas distribuidos, donde podría tener muchas personas llamando a un componente que no responde y quedando fuera de servicio, lo que provoca que la falla se propague en cascada por todo el sistema.

## Lámina 51

Disponibilidad

Patrones - Circuit breaker

Tradeoffs:

Se debe tener cuidado al elegir los valores de tiempo de espera (o reintento). Si el tiempo de espera es demasiado largo, se agrega una latencia innecesaria. Pero si el tiempo de espera es demasiado corto, entonces el circuito se disparará cuando no sea necesario, una especie de "falso positivo", lo que puede reducir la disponibilidad y el rendimiento de estos servicios.

## Lámina 52

Disponibilidad

Patrones

Process pairs - Proceso de pares. Este patrón emplea puntos de control y reversión. En caso de falla, la copia de seguridad ha sido revisada y (si es necesario) revertida a un estado seguro, por lo que está lista para tomar el control cuando ocurra una falla.

Forward error recovery - Recuperación de errores de reenvío. Este patrón proporciona una forma de salir de un estado indeseable avanzando hacia un estado deseable. Esto a menudo se basa en capacidades integradas de corrección de errores, como la redundancia de datos, de modo que los errores puedan corregirse sin necesidad de volver a un estado anterior o volver a intentarlo.

## Lámina 53

Disponibilidad

Lecturas Recomendadas

Disaster Recovery (DR) Architecture on AWS, Part I: Strategies for Recovery in the Cloud.

Disaster Recovery (DR) Architecture on AWS, Part II: Backup and Restore with Rapid Recovery.

Disaster Recovery (DR) Architecture on AWS, Part III: Pilot Light and Warm Standby

Disaster Recovery (DR) Architecture on AWS, Part IV: Multi-site Active/Active

Circuit Breaker – Martin Fowler

Tips for High Availability -  Netflix

## Lámina 54

Bibliografía

Len Bass, Paul Clements, Rick Kazman. Software Architecture in Practice. 4th Edition. SEI / Addison-Wesley, 2022​

## Lámina 55

_(sin texto: la lámina es una imagen)_
