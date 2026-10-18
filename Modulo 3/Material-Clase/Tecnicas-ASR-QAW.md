# Técnicas ASR / QAW — deck oficial del Módulo 3

> **Tipo:** `material-oficial` (Recursos complementarios → «Presentaciones Adicionales», Brightspace, Unidad 4 de 5).
> **Fuente:** `TecnicasASR-QAW.pptx` (35 láminas), descargado el 2026-10-18 con sesión de Danny.
> **Extraído:** 2026-10-18, texto de las láminas tal cual. Las **notas del orador** se incluyen aparte
>  porque traen contenido (a menudo en inglés, del libro de referencia); las que solo tienen un número se omiten.
> **Límite de la extracción:** solo texto. Diagramas, figuras y tablas dibujadas como imagen NO están.
> **Este archivo no se edita.** Las notas y críticas van en `Aportes/`.

---

## Lámina 1

DIPLOMADO EN

ARQUITECTURA DE SOFTWARE

TÉCNICAS: ASR / QAW

> **Notas del orador:** Many architects believe that if the architecture decision involves any specific technology, then it’s not an architecture decision, but rather a technical decision. This is not always true. If an architect makes a decision to use a particular technology because it directly supports a particular architecture characteristic (such as performance or scalability), then it’s an architecture decision. Michael Nygard , a well-known software architect and author of  Release It!  (Pragmatic Bookshelf), addressed the problem of what decisions an architect should be responsible for (and hence what is an architecture decision) by coining the term  architecturally significant . According to Michael, architecturally significant decisions are those decisions that affect the structure, nonfunctional characteristics, dependencies, interfaces, or construction techniques. 4

---

## Lámina 2

REQUERIMIENTOS

ARQUITECTONICAMENTE SIGNIFICATIVOS

ASR

> **Notas del orador:** The  structure  refers to decisions that impact the patterns or styles of architecture being used. An example of this is the decision to share data between a set of microservices. This decision impacts the bounded context of the microservice, and as such affects the structure of the application. The  nonfunctional characteristics  are the architecture characteristics (“- ilities ”) that are important for the application or system being developed or maintained. If a choice of technology impacts performance, and performance is an important aspect of the application, then it becomes an architecture decision. Dependencies  refer to coupling points between components and/or services within the system, which in turn impact overall scalability, modularity, agility, testability, reliability, and so on. Interfaces  refer to how services and components are accessed and orchestrated, usually through a gateway, integration hub, service bus, or API proxy. Interfaces usually involve defining contracts, including the versioning and deprecation strategy of those contracts. Interfaces impact others using the system and hence are architecturally significant. Finally,  construction techniques  refer to decisions about platforms, frameworks, tools, and even processes that, although technical in nature, might impact some aspect of the architecture. 5

---

## Lámina 3

Técnicas de Arquitectura - ASR

Muchos arquitectos creen que si la decisión de arquitectura involucra alguna tecnología específica, entonces no es una decisión de arquitectura, sino más bien una decisión técnica. Esto no siempre es cierto. Si un arquitecto toma la decisión de usar una tecnología en particular porque soporta directamente una característica de arquitectura en particular (como el rendimiento o la escalabilidad), entonces es una decisión de arquitectura.

Michael Nygard, un conocido arquitecto de software y autor de Release It!, abordó el problema de las decisiones de las que un arquitecto debería ser responsable al acuñar el término arquitectónicamente significativo. Según Michael, las decisiones arquitectónicamente significativas son aquellas decisiones que afectan la estructura, las características no funcionales, las dependencias, las interfaces o las técnicas de construcción.

Arquitectónicamente Significativo

> **Notas del orador:** The  structure  refers to decisions that impact the patterns or styles of architecture being used. An example of this is the decision to share data between a set of microservices. This decision impacts the bounded context of the microservice, and as such affects the structure of the application. The  nonfunctional characteristics  are the architecture characteristics (“- ilities ”) that are important for the application or system being developed or maintained. If a choice of technology impacts performance, and performance is an important aspect of the application, then it becomes an architecture decision. Dependencies  refer to coupling points between components and/or services within the system, which in turn impact overall scalability, modularity, agility, testability, reliability, and so on. Interfaces  refer to how services and components are accessed and orchestrated, usually through a gateway, integration hub, service bus, or API proxy. Interfaces usually involve defining contracts, including the versioning and deprecation strategy of those contracts. Interfaces impact others using the system and hence are architecturally significant. Finally,  construction techniques  refer to decisions about platforms, frameworks, tools, and even processes that, although technical in nature, might impact some aspect of the architecture. 6

---

## Lámina 4

Técnicas de Arquitectura - ASR

La estructura se refiere a decisiones que impactan los patrones o estilos de arquitectura que se utilizan. Un ejemplo de esto es la decisión de compartir datos entre un conjunto de microservicios. Esta decisión afecta el contexto delimitado del microservicio y, como tal, afecta la estructura de la aplicación.

Las características no funcionales son las características de la arquitectura ("-ilities") que son importantes para la aplicación o el sistema que se está desarrollando o manteniendo. Si una elección de tecnología afecta el rendimiento y el rendimiento es un aspecto importante de la aplicación, entonces se convierte en una decisión de arquitectura.

Arquitectónicamente Significativo

> **Notas del orador:** The  structure  refers to decisions that impact the patterns or styles of architecture being used. An example of this is the decision to share data between a set of microservices. This decision impacts the bounded context of the microservice, and as such affects the structure of the application. The  nonfunctional characteristics  are the architecture characteristics (“- ilities ”) that are important for the application or system being developed or maintained. If a choice of technology impacts performance, and performance is an important aspect of the application, then it becomes an architecture decision. Dependencies  refer to coupling points between components and/or services within the system, which in turn impact overall scalability, modularity, agility, testability, reliability, and so on. Interfaces  refer to how services and components are accessed and orchestrated, usually through a gateway, integration hub, service bus, or API proxy. Interfaces usually involve defining contracts, including the versioning and deprecation strategy of those contracts. Interfaces impact others using the system and hence are architecturally significant. Finally,  construction techniques  refer to decisions about platforms, frameworks, tools, and even processes that, although technical in nature, might impact some aspect of the architecture. 7

---

## Lámina 5

Técnicas de Arquitectura - ASR

Las dependencias se refieren a puntos de acoplamiento entre componentes y/o servicios dentro del sistema, que a su vez afectan la escalabilidad general, la modularidad, la agilidad, la capacidad de prueba, la confiabilidad, etc.

Las interfaces se refieren a cómo se accede a los servicios y componentes y cómo se organizan, generalmente a través de una puerta de enlace, un centro de integración, un bus de servicio o un proxy API. Las interfaces generalmente involucran la definición de contratos, incluida la estrategia de versiones y obsolescencia de esos contratos. Las interfaces impactan a otros que usan el sistema y, por lo tanto, son arquitectónicamente significativas.

Arquitectónicamente Significativo

---

## Lámina 6

Técnicas de Arquitectura - ASR

Finalmente, las técnicas de construcción se refieren a decisiones sobre plataformas, frameworks, herramientas e incluso procesos que, aunque de naturaleza técnica, pueden afectar algún aspecto de la arquitectura.

Arquitectónicamente Significativo

---

## Lámina 7

Técnicas de Arquitectura - ASR

Las arquitecturas existen para construir sistemas que satisfagan los requisitos. Por "requisitos", no necesariamente nos referimos a un catálogo documentado producido utilizando las mejores técnicas que ofrece la ingeniería de requisitos. En cambio, nos referimos al conjunto de propiedades que, si su sistema no las satisface, harán que el sistema falle. Los requisitos existen en tantas formas como proyectos de desarrollo de software, desde especificaciones pulidas hasta entendimiento verbal compartido (real o imaginario) entre los principales interesados.

Requisito Arquitectónicamente Significativo (ASR)

---

## Lámina 8

Técnicas de Arquitectura - ASR

Para un arquitecto, no todos los requisitos son iguales. Algunos tienen un efecto mucho más profundo en la arquitectura que otros. Un requisito arquitectónicamente significativo (ASR) es un requisito que tendrá un efecto profundo en la arquitectura, es decir, la arquitectura bien podría ser dramáticamente diferente en ausencia de dicho requisito.

Requisito Arquitectónicamente Significativo (ASR)

---

## Lámina 9

Técnicas de Arquitectura - ASR

Muchos proyectos no crean ni mantienen el tipo de documento de requisitos que a los profesores en las clases de ingeniería de software o a los autores de libros tradicionales de ingeniería de software les encanta prescribir. Además, ningún arquitecto simplemente se sienta y espera hasta que los requisitos estén "terminados" antes de comenzar a trabajar. El arquitecto debe comenzar mientras los requisitos aún están cambiando.

Recopilando ASR a partir de documentos de requisitos

---

## Lámina 10

Técnicas de Arquitectura - ASR

Los documentos de requisitos a menudo le fallan a un arquitecto de dos maneras:

La mayor parte de la información que se encuentra en una especificación de requisitos no afecta a la arquitectura. Como hemos visto una y otra vez, las arquitecturas son impulsadas o “moldeadas” principalmente por los requisitos de atributos de calidad.

Mucho de lo que es útil para un arquitecto no se encontrará ni siquiera en el mejor documento de requisitos.

Recopilando ASR a partir de documentos de requisitos

---

## Lámina 11

Técnicas de Arquitectura - ASR

Si bien los documentos de requisitos no le contarán a un arquitecto toda la historia, siguen siendo una fuente importante de ASR. Por supuesto, los ASR no estarán convenientemente etiquetados como tales; el arquitecto debe esperar realizar un poco de investigación y arqueología para descubrirlos. Algunas cosas específicas para buscar son las siguientes categorías de información:

Uso. Roles de usuario versus modos de sistema, internacionalización, distinciones de idioma.

Tiempo. Puntualidad y coordinación de elementos. Elementos externos. Sistemas externos, protocolos, sensores o actuadores (dispositivos), middleware.

Recopilando  ASR a partir de documentos de requisitos

---

## Lámina 12

Técnicas de Arquitectura - ASR

Redes. Propiedades y configuraciones de red (incluidas sus propiedades de seguridad).

Orquestación. Pasos de procesamiento, flujos de información.

Propiedades de seguridad. Roles de usuario, permisos, autenticación.

Datos. Persistencia y actualidad.

Recursos. Tiempo, concurrencia, uso de memoria, programación, múltiples usuarios, múltiples actividades, dispositivos, uso de energía, recursos flexibles (por ejemplo, búferes, colas) y requisitos de escalabilidad.

Recopilando  ASR a partir de documentos de requisitos

---

## Lámina 13

Técnicas de Arquitectura - ASR

Gestión de proyectos. Planes de trabajo en equipo, conjuntos de habilidades, formación, coordinación de equipos. Opciones de hardware. Procesadores, familias de procesadores, evolución de procesadores. Flexibilidad de funcionalidad, portabilidad, calibraciones, configuraciones. Tecnologías nombradas, paquetes comerciales.

Opciones de hardware. Procesadores, familias de procesadores, evolución de procesadores.

Flexibilidad de funcionalidad, portabilidad, calibraciones, configuraciones.

Tecnologías nombradas, paquetes comerciales.

Recopilando ASR a partir de documentos de requisitos

---

## Lámina 14

Técnicas de Arquitectura - ASR

Primero, las partes interesadas a menudo no saben cuáles son realmente sus requisitos no funcionales. En ese caso, se pide a los arquitectos que ayuden a establecer los requisitos de QA para un sistema. Los proyectos que reconocen esta necesidad de colaboración y la fomentan tienen muchas más probabilidades de éxito que los que no lo hacen.

Los arquitectos experimentados a menudo tienen conocimientos profundos sobre qué respuestas de QA han sido exhibidas por sistemas similares y qué respuestas de control de calidad son razonables esperar y proporcionar en el contexto actual. Los arquitectos generalmente también pueden brindar comentarios rápidos sobre qué respuestas de QA serán fáciles de lograr y cuáles probablemente serán problemáticas o incluso prohibitivas.

Recopilando ASR mediante entrevistas a los stakeholders

---

## Lámina 15

Técnicas de Arquitectura - ASR

Taller de Atributos de Calidad (QAW).

La recopilación de esta información de las partes interesadas puede lograrse mediante muchos métodos. Uno de esos métodos es el Taller de Atributos de Calidad (QAW).

El QAW es un método facilitado y centrado en los stakeholders para generar, priorizar y refinar escenarios de atributos de calidad antes de que se complete la arquitectura del software. Enfatiza las preocupaciones a nivel del sistema y, específicamente, el papel que desempeñará el software en el sistema. El QAW depende en gran medida de la participación de las partes interesadas del sistema.

Recopilando ASR mediante entrevistas a los stakeholders

---

## Lámina 16

Técnicas de Arquitectura - ASR

Taller de Atributos de Calidad (QAW).

El QAW tiene los siguientes elementos:

1. Presentación de la misión de negocio. La parte interesada que representa las preocupaciones de negocio detrás del sistema (generalmente un gerente o un representante de la gerencia) dedica aproximadamente una hora a presentar el contexto de negocio del sistema, los requisitos funcionales generales, las restricciones y los requisitos de control de calidad conocidos. Los QA que se refinarán en pasos posteriores se derivarán en gran medida de las necesidades de negocio/misionales presentadas en este paso.

Recopilando ASR mediante entrevistas a los stakeholders

---

## Lámina 17

Técnicas de Arquitectura - ASR

Taller de Atributos de Calidad (QAW).

2. Presentación del plano arquitectónico. Si bien es posible que no exista un sistema detallado o una arquitectura de software, es posible que se hayan creado descripciones amplias del sistema, dibujos de contexto u otros artefactos que describan algunos de los detalles técnicos del sistema. En este punto del taller, el arquitecto presentará los planos arquitectónicos del sistema tal como están. Esto permite a las partes interesadas conocer el pensamiento arquitectónico actual, en la medida en que exista.

Recopilando ASR mediante entrevistas a los stakeholders

---

## Lámina 18

Técnicas de Arquitectura - ASR

Taller de Atributos de Calidad (QAW).

3. Identificación de drivers de arquitectura. Los facilitadores compartirán su lista de impulsores arquitectónicos clave que reunieron en los dos pasos anteriores y pedirán a las partes interesadas aclaraciones, adiciones, eliminaciones y correcciones. La idea es llegar a un consenso sobre una lista depurada de impulsores arquitectónicos que incluya requisitos generales, impulsores de negocio, restricciones y atributos de calidad.

Recopilando ASR mediante entrevistas a los stakeholders

---

## Lámina 19

Técnicas de Arquitectura - ASR

Taller de Atributos de Calidad (QAW).

4. Lluvia de ideas sobre escenarios. Cada actor expresa un escenario que representa sus preocupaciones con respecto al sistema. Los facilitadores se aseguran de que cada escenario aborde una inquietud de QA, especificando un estímulo y una respuesta explícitos.

Recopilando ASR mediante entrevistas a los stakeholders

---

## Lámina 20

Técnicas de Arquitectura - ASR

Taller de Atributos de Calidad (QAW).

5. Consolidación de escenarios. Después de la lluvia de ideas de escenarios, los escenarios similares se consolidan donde sea razonable. Los facilitadores piden a las partes interesadas que identifiquen los escenarios que son muy similares en contenido. Los escenarios que son similares se fusionan, siempre que las personas que los propusieron estén de acuerdo y sientan que sus escenarios no se diluirán en el proceso.

Recopilando ASR mediante entrevistas a los stakeholders

---

## Lámina 21

Técnicas de Arquitectura - ASR

Taller de Atributos de Calidad (QAW).

6. Priorización de escenarios. La priorización de los escenarios se logra asignando a cada parte interesada un número de votos equivalente al 30 por ciento del número total de escenarios generados después de la consolidación. Las partes interesadas pueden asignar cualquier número de sus votos a cualquier escenario o combinación de escenarios. Los votos se cuentan y los escenarios se priorizan en consecuencia.

Recopilando ASR mediante entrevistas a los stakeholders

---

## Lámina 22

Técnicas de Arquitectura - ASR

Taller de Atributos de Calidad (QAW).

7. Refinamiento de escenarios. Después de la priorización, los principales escenarios se refinan y elaboran. Los facilitadores ayudan a las partes interesadas a poner los escenarios en la forma de escenario de seis partes de medida de fuente-estímulo-artefacto-entorno-respuesta-respuesta. A medida que se refinan los escenarios, surgirán problemas relacionados con su satisfacción y deben registrarse . Este paso dura mientras el tiempo y los recursos lo permitan.

Recopilando ASR mediante entrevistas a los stakeholders

---

## Lámina 23

Técnicas de Arquitectura - ASR

Los resultados de las entrevistas con las partes interesadas deben incluir una lista de impulsores arquitectónicos y un conjunto de escenarios de QA que las partes interesadas (como grupo) priorizaron. Esta información puede ser utilizada para los siguientes propósitos:

Refinar los requisitos del sistema y del software.

Comprender y aclarar los drivers arquitectónicos del sistema.

Proporcionar una justificación de por qué el arquitecto tomó posteriormente ciertas decisiones de diseño.

Guiar el desarrollo de prototipos y simulaciones.

Influir en el orden en que se desarrolla la arquitectura.

Recopilando ASR mediante entrevistas a los stakeholders

---

## Lámina 24

Técnicas de Arquitectura - ASR

Los Objetivos de negocio son la razón de ser para construir un sistema. Ninguna organización construye un sistema sin una razón; más bien, las personas involucradas quieren promover la misión y las ambiciones de su organización y de ellos mismos. Los objetivos de negocio comunes incluyen obtener ganancias, por supuesto, pero la mayoría de las organizaciones tienen muchas más preocupaciones que simplemente obtener ganancias.

Los objetivos de negocio son de interés para los arquitectos porque con frecuencia conducen directamente a ASR. Hay tres relaciones posibles entre los objetivos de negocio y una arquitectura:

Recopilando ASR mediante la comprensión de objetivos de negocio

---

## Lámina 25

Técnicas de Arquitectura - ASR

Los Objetivos de Negocio a menudo conducen a requisitos de atributos de calidad. Cada requisito de atributo de calidad, como el tiempo de respuesta visible para el usuario, la flexibilidad de la plataforma, la seguridad inquebrantable o cualquiera de una docena de otras necesidades, se origina en algún propósito superior que puede describirse en términos de valor agregado

Los Objetivos de Negocio pueden afectar la arquitectura sin inducir en absoluto un requisito de atributo de calidad.

Sin influencia de un Objetivo de Negocio en la arquitectura. No todos los objetivos de negocio conducen a atributos de calidad.

Recopilando ASR mediante la comprensión de objetivos de negocio

---

## Lámina 26

Técnicas de Arquitectura - ASR

Algunos objetivos de negocio pueden conducir a requisitos de atributos de calidad, directamente a decisiones arquitectónicas o a soluciones no arquitectónicas.

Recopilando ASR mediante la comprensión de objetivos de negocio

---

## Lámina 27

Técnicas de Arquitectura - ASR

En un mundo perfecto, las técnicas descritas anteriormente se aplicarían al principio de su proceso de desarrollo: entrevistar a las partes interesadas clave, obtener sus objetivos de negocio y requisitos arquitectónicos impulsores, y la priorización de todas estas entradas. Por supuesto, el mundo real, lamentablemente, es menos que perfecto. A menudo sucede que no tiene acceso a estas partes interesadas cuando las necesita, por razones organizativas o comerciales. Entonces, ¿Qué haces?

Los arquitectos pueden usar una herramienta llamada árbol de utilidades cuando las "fuentes primarias" de requisitos no están disponibles. Un árbol de utilidades es una representación de arriba hacia abajo de lo que usted, como arquitecto, cree que son los ASR relacionados con los QA que son críticos para el éxito del sistema.

Recopilando ASR mediante el Árbol de Utilidades

---

## Lámina 28

Técnicas de Arquitectura - ASR

Un Árbol de Utilidades comienza con la palabra "Utilidad" como nodo raíz. La utilidad es una expresión de la "bondad" general del sistema. Luego elabora este nodo raíz enumerando los principales controles de calidad que el sistema debe exhibir.

Debajo de cada control de calidad, registre los refinamientos específicos de ese atributo de calidad. Por ejemplo, el rendimiento puede descomponerse en "latencia de datos" y "rendimiento de transacciones" o, alternativamente, "tiempo de espera del usuario" y "tiempo para actualizar la página web". Los refinamientos que elija deben ser los que sean relevantes para su sistema. Debajo de cada refinamiento, puede registrar los ASR específicos, expresados como escenarios de control de calidad.

Recopilando ASR mediante el Árbol de Utilidades

---

## Lámina 29

Técnicas de Arquitectura - ASR

Una vez que los ASR se registran como escenarios y se colocan en las hojas del árbol, puede evaluar estos escenarios según dos criterios: el valor de negocio del escenario candidato y el riesgo técnico de lograrlo. Puede usar cualquier escala que desee, pero encontramos que un sistema de puntuación simple "H" (alto), "M" (medio) y "L" (bajo) es suficiente para cada criterio.

El valor de negocio, "alto" designa un requisito imprescindible, "medio" identifica un requisito que es importante pero que no conduciría al fracaso del proyecto si se omitiera, y "bajo" describe un requisito deseable para cumplir pero no es algo que valga mucho el esfuerzo

Recopilando ASR mediante el Árbol de Utilidades

---

## Lámina 30

Técnicas de Arquitectura - ASR

Para el riesgo técnico, "alto" significa que cumplir con este ASR lo mantiene despierto por la noche, "medio" significa que cumplir con este ASR es preocupante pero no conlleva un alto riesgo, y "bajo" significa que tiene confianza en su capacidad para cumplir ese ASR.

Recopilando ASR mediante el Árbol de Utilidades

---

## Lámina 31

Técnicas de Arquitectura - ASR

Recopilando ASR mediante el Árbol de Utilidades

---

## Lámina 32

Técnicas de Arquitectura - ASR

Una vez que haya completado un árbol de utilidades, puede usarlo para realizar comprobaciones importantes. Por ejemplo: Un QA o un refinamiento de QA sin ningún escenario de ASR no es necesariamente un error u omisión que deba corregirse, sino más bien una indicación de que debe investigar si hay escenarios de ASR no registrados en esa área. Los escenarios ASR que reciben una calificación (H, H) son obviamente los que merecen la mayor atención de su parte; estos son los más significativos de los requisitos. Una gran cantidad de estos escenarios podría ser motivo de preocupación con respecto a si el sistema es, de hecho, alcanzable.

Recopilando ASR mediante el Árbol de Utilidades

---

## Lámina 33

SEI - Quality Attribute Workshop Collection

The SEI Quality Attribute Workshop (Fact Sheet)

Quality Attribute Workshops (QAWs), Third Edition

Quality Attribute Workshop Participants Handbook (Special Report)

Lecturas

---

## Lámina 34

Humberto Cervantes, Rick Kazman. Designing Software Architectures: A Practical Approach. SEI / Addison-Wesley, 2016.

Bibliografía

Len Bass, Paul Clements, Rick Kazman. Software Architecture in Practice. 4th Edition. SEI / Addison-Wesley, 2022​

---

## Lámina 35

_(sin texto: la lámina es una imagen)_
