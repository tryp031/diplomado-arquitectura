# Tácticas de Usabilidad — deck oficial del Módulo 2

> **Tipo:** `material-oficial` (Recursos complementarios, Brightspace, Unidad 3 de 5).
> **Fuente:** `TacticasUsabilidad.pptx` — Bass, Clements, Kazman, *Software Architecture in Practice*, 4th ed. (citado en el propio deck).
> **Extraído:** 2026-09-30, texto de las láminas tal cual. Se tradujo del inglés con traducción automática en el deck original (hay frases torpes).
> **Límite de la extracción:** solo texto. Los diagramas, figuras y tablas dibujadas como imagen NO están; las láminas que quedan vacías o con solo título dependen de una imagen.
> **Este archivo no se edita.** Las notas y críticas van en `Aportes/`.

---

## Lámina 1

USABILIDAD

(USABILITY)

## Lámina 2

Usabilidad - Usability

La Usabilidad se refiere a qué tan fácil es para el usuario realizar una tarea deseada y el tipo de soporte al usuario que proporciona el sistema. A lo largo de los años, un enfoque en la usabilidad ha demostrado ser una de las formas más baratas y fáciles de mejorar la calidad de un sistema (o más precisamente, la percepción de la calidad por parte del usuario) y, por lo tanto, la satisfacción del usuario final.

Definición

## Lámina 3

Usabilidad - Usability

Características del sistema de aprendizaje. Si el usuario no está familiarizado con un sistema en particular o un aspecto particular del mismo, ¿qué puede hacer el sistema para facilitar la tarea de aprender? Esto podría incluir proporcionar funciones de ayuda.

Usar un sistema de manera eficiente. ¿Qué puede hacer el sistema para que el usuario sea más eficiente en su funcionamiento? Esto podría incluir permitir que el usuario redirija el sistema después de emitir un comando. Por ejemplo, el usuario puede desear suspender una tarea, realizar varias operaciones y luego reanudar esa tarea.

Definición

## Lámina 4

Usabilidad - Usability

Minimizar el impacto de los errores de los usuarios. ¿Qué puede hacer el sistema para garantizar que un error de usuario tenga un impacto mínimo? Por ejemplo, el usuario puede querer cancelar un comando emitido incorrectamente o deshacer sus efectos.

Adaptación del sistema a las necesidades del usuario. ¿Cómo puede el usuario (o el propio sistema) adaptarse para facilitar la tarea del usuario? Por ejemplo, el sistema puede completar automáticamente las URL en función de las entradas anteriores de un usuario.

Definición

## Lámina 5

Usabilidad - Usability

Aumento de la confianza y la satisfacción. ¿Qué hace el sistema para darle al usuario la confianza de que se está tomando la acción correcta? Por ejemplo, proporcionar comentarios que indiquen que el sistema está realizando una tarea de larga duración, junto con el porcentaje de finalización hasta el momento, aumentará la confianza del usuario en el sistema.

Definición

## Lámina 6

ESCENARIO

## Lámina 7

Usabilidad - Usability

Escenario General

Portion of Scenario

Description

Possible Values

Source

Where does the stimulus come from?

The end user (who may be in a specialized role, such as a system or network administrator) is the primary source of the stimulus for usability.

An external event arriving at a system (to which the user may react) may also be a stimulus source.

Stimulus

What does the end user want?

End user wants to:

Use a system efficiently

Learn to use the system

Minimize the impact of errors

Adapt the system

Configure the system

## Lámina 8

Usabilidad - Usability

Escenario General

Portion of Scenario

Description

Possible Values

Artifacts

What portion of the system is being stimulated?

Common examples include:

A GUI

A command-line interface

A voice interface

A touch screen

Environment

When does the stimulus reach the system?

The user actions with which usability is concerned always occur at runtime or at system configuration time.

Response

How should the system respond?

The system should:

Provide the user with the features needed

Anticipate the user’s needs

Provide appropriate feedback to the user

## Lámina 9

Usabilidad - Usability

Escenario General

Portion of Scenario

Description

Possible Values

Response measure

How is the response measured?

One or more of the following:

Task time

Number of errors

Learning time

Ratio of learning time to task time

Number of tasks accomplished

User satisfaction

Gain of user knowledge

Ratio of successful operations to total operations

Amount of time or data lost when an error occurs

## Lámina 10

Usabilidad - Usability

Ejemplo de un Escenario concreto

El usuario descarga una nueva aplicación y la usa productivamente después de 2 minutos de experimentación.

## Lámina 11

TÁCTICAS

## Lámina 12

Usabilidad - Usability

Tácticas

## Lámina 13

Usabilidad - Usability

Tácticas

Fuente: Software Architecture in Practice, 4th Edition

## Lámina 14

Usabilidad - Usability

Tácticas - Soportar la Iniciativa de Usuario

Cancelar. Cuando el usuario emite un comando de cancelación, el sistema debe estar escuchando (por lo tanto, existe la responsabilidad de tener un oyente constante que no esté bloqueado por las acciones de lo que sea que se esté cancelando); la actividad que se cancela debe ser terminada; cualquier recurso que esté siendo utilizado por la actividad cancelada debe ser liberado; y los componentes que estén colaborando con la actividad cancelada deberán ser informados para que ellos también tomen las medidas correspondientes.

## Lámina 15

Usabilidad - Usability

Tácticas - Soportar la Iniciativa de Usuario

Deshacer. Para admitir la capacidad de deshacer, el sistema debe mantener una cantidad suficiente de información sobre el estado del sistema para que se pueda restaurar un estado anterior, a pedido del usuario. Tal registro puede tomar la forma de "instantáneas" de estado, por ejemplo, puntos de control, o un conjunto de operaciones reversibles. Deshacer viene en sabores. Algunos sistemas permiten un solo deshacer (donde invocar deshacer nuevamente lo revierte al estado en el que ordenó el primer deshacer, esencialmente deshacer el deshacer). En otros sistemas, ordenar múltiples operaciones de deshacer lo lleva a través de muchos estados anteriores, ya sea hasta cierto límite o hasta el momento en que se abrió la aplicación por última vez.

## Lámina 16

Usabilidad - Usability

Tácticas - Soportar la Iniciativa de Usuario

Pausa/reanudar. Cuando un usuario ha iniciado una operación de larga duración, por ejemplo, descargar un archivo grande o un conjunto de archivos de un servidor, a menudo es útil proporcionar la capacidad de pausar y reanudar la operación. Se puede pausar una operación de ejecución prolongada para liberar temporalmente recursos para que puedan reasignarse a otras tareas.

## Lámina 17

Usabilidad - Usability

Tácticas - Soportar la Iniciativa de Usuario

Agregar. Cuando un usuario realiza operaciones repetitivas u operaciones que afectan a una gran cantidad de objetos de la misma manera, es útil proporcionar la capacidad de agregar los objetos de nivel inferior en un solo grupo, de modo que la operación pueda aplicarse al grupo, liberando así al usuario de la monotonía y la posibilidad de cometer errores al realizar la misma operación repetidamente. Un ejemplo es agregar todos los objetos en una diapositiva y cambiar el texto a una fuente de 14 puntos.

## Lámina 18

Usabilidad - Usability

Tácticas - Soportar la Iniciativa del Sistema

Mantener el modelo de tareas. El modelo de tarea se utiliza para determinar el contexto, de modo que el sistema pueda tener una idea de lo que el usuario está intentando hacer y brindar asistencia. Por ejemplo, muchos motores de búsqueda brindan capacidades predictivas de escritura anticipada y muchos clientes de correo brindan corrección ortográfica. Ambas funciones se basan en modelos de tareas.

## Lámina 19

Usabilidad - Usability

Tácticas - Soportar la Iniciativa del Sistema

Mantener el modelo de usuario. Este modelo representa explícitamente el conocimiento del sistema por parte del usuario, el comportamiento del usuario en términos del tiempo de respuesta esperado y otros aspectos específicos de un usuario o una clase de usuarios. Por ejemplo, las aplicaciones de aprendizaje de idiomas monitorean constantemente las áreas donde un usuario comete errores y luego brindan ejercicios adicionales para corregir esos comportamientos. Un caso especial de esta táctica se encuentra comúnmente en la personalización de la interfaz de usuario, en la que un usuario puede modificar explícitamente el modelo de usuario del sistema.

## Lámina 20

Usabilidad - Usability

Tácticas - Soportar la Iniciativa del Sistema

Mantener el modelo del sistema. El sistema mantiene un modelo explícito de sí mismo. Esto se utiliza para determinar el comportamiento esperado del sistema de modo que se pueda proporcionar al usuario la información adecuada. Una manifestación común de un modelo de sistema es una barra de progreso que predice el tiempo necesario para completar la actividad actual

## Lámina 21

PATRONES

## Lámina 22

Usabilidad - Usability

Patrones - Model-View-Controller

MVC es probablemente el patrón de usabilidad más conocido. Viene en muchas variantes, como MVP (modelo-vista-presentador), MVVM (modelo-vista-vista-modelo), MVA (modelo-vista-adaptador), etc. Esencialmente, todos estos patrones se centran en separar el modelo, la lógica de "negocios" subyacente del sistema, de su realización en una o más vistas de la interfaz de usuario. En el modelo MVC original, el modelo enviaría actualizaciones a una vista, que un usuario vería e interactuaría. Las interacciones del usuario (pulsaciones de teclas, clics de botones, movimientos del mouse, etc.) se transmiten al controlador, que las interpreta como operaciones en el modelo y luego envía esas operaciones al modelo, que cambia su estado en respuesta. La ruta inversa también era una parte del patrón MVC original. Es decir, el modelo podría cambiarse y el controlador enviaría actualizaciones a la vista.

## Lámina 23

Usabilidad - Usability

Patrones - Model-View-Controller

Beneficios

Debido a que MVC promueve una clara separación de preocupaciones, los cambios en un aspecto del sistema, como el diseño de la interfaz de usuario (la vista), a menudo no tienen consecuencias para el modelo o el controlador.

Además, debido a que MVC promueve la separación de preocupaciones, los desarrolladores pueden trabajar en todos los aspectos del patrón (modelo, vista y controlador) de manera relativamente independiente y en paralelo. Estos aspectos separados también se pueden probar en paralelo.

Un modelo puede usarse en sistemas con diferentes vistas, o una vista puede usarse en sistemas con diferentes modelos.

## Lámina 24

Usabilidad - Usability

Patrones - Model-View-Controller

Tradeoffs

MVC puede volverse una carga para las interfaces de usuario complejas, ya que la información a menudo se distribuye en varios componentes. Por ejemplo, si hay varias vistas del mismo modelo, un cambio en el modelo puede requerir cambios en varios componentes que de otro modo no estarían relacionados.

Para interfaces de usuario simples, MVC agrega una complejidad inicial que puede no compensar los ahorros posteriores.

MVC agrega una pequeña cantidad de latencia a las interacciones del usuario. Si bien esto es generalmente aceptable, puede ser problemático para las aplicaciones que requieren una latencia muy baja.

## Lámina 25

Usabilidad - Usability

Patrones - Observer

El patrón de observador es una forma de vincular alguna funcionalidad con una o más vistas. Este patrón tiene un sujeto, la entidad que se observa, y uno o más observadores de ese sujeto. Los observadores necesitan registrarse con el sujeto; luego, cuando cambia el estado del sujeto, se notifica a los observadores. Este patrón se usa a menudo para implementar MVC (y sus variantes), por ejemplo, como una forma de notificar a las distintas vistas de los cambios en el modelo.

## Lámina 26

Usabilidad - Usability

Patrones - Observer

Beneficios

Este patrón separa alguna funcionalidad subyacente de la preocupación de cómo y cuántas veces se presenta esta funcionalidad.

El patrón de observador facilita el cambio de enlaces entre el sujeto y los observadores en tiempo de ejecución.

## Lámina 27

Usabilidad - Usability

Patrones - Observer

Tradeoffs

El patrón de observador es excesivo si no se requieren múltiples vistas del sujeto. El patrón del observador requiere que todos los observadores se registren y desregistren con el sujeto. Si los observadores se niegan a cancelar el registro, su memoria nunca se libera, lo que resulta en una fuga de memoria. Además, esto puede afectar negativamente al rendimiento, ya que se seguirán invocando observadores obsoletos.

Es posible que los observadores deban realizar un trabajo considerable para determinar si reflejar una actualización de estado y cómo, y este trabajo puede repetirse para cada observador.

## Lámina 28

Usabilidad - Usability

Patrones - Memento

El patrón memento es una forma común de implementar la táctica de deshacer. Este patrón presenta tres componentes principales: el creador, el cuidador y el recuerdo. El originador está procesando algún flujo de eventos que cambian su estado (originados por la interacción del usuario). El cuidador está enviando eventos al originador que hacen que cambie su estado. Cuando el cuidador está a punto de cambiar el estado del originador, puede solicitar un recuerdo, una instantánea del estado existente, y puede usar este artefacto para restaurar ese estado existente si es necesario, simplemente devolviéndole el recuerdo al originador. De esta forma, el cuidador no sabe nada de cómo se maneja el estado; el memento es simplemente una abstracción que emplea el cuidador.

## Lámina 29

Usabilidad - Usability

Patrones - Memento

Beneficios

El beneficio obvio de este patrón es que delega el complicado proceso de implementar deshacer y determinar qué estado conservar a la clase que realmente está creando y administrando ese estado. En consecuencia, se conserva la abstracción del originador y el resto del sistema no necesita conocer los detalles.

## Lámina 30

Usabilidad - Usability

Patrones - Memento

Tradeoffs

Según la naturaleza del estado que se conserva, el memento puede consumir cantidades arbitrariamente grandes de memoria, lo que puede afectar el rendimiento. En un documento muy grande, intente cortar y pegar muchas secciones grandes y luego deshacer todo eso. Es probable que esto haga que su procesador de texto se ralentice notablemente.

## Lámina 31

Bibliografía

Len Bass, Paul Clements, Rick Kazman. Software Architecture in Practice. 4th Edition. SEI / Addison-Wesley, 2022​

## Lámina 32

_(sin texto: la lámina es una imagen)_
