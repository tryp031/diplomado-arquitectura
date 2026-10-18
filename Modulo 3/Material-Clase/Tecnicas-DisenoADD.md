# Técnicas de Diseño (ADD) — deck oficial del Módulo 3

> **Tipo:** `material-oficial` (Recursos complementarios → «Presentaciones Adicionales», Brightspace, Unidad 4 de 5).
> **Fuente:** `TecnicasDisenoADD.pptx` (26 láminas), descargado el 2026-10-18 con sesión de Danny.
> **Extraído:** 2026-10-18, texto de las láminas tal cual. Las **notas del orador** se incluyen aparte
>  porque traen contenido (a menudo en inglés, del libro de referencia); las que solo tienen un número se omiten.
> **Límite de la extracción:** solo texto. Diagramas, figuras y tablas dibujadas como imagen NO están.
> **Este archivo no se edita.** Las notas y críticas van en `Aportes/`.

---

## Lámina 1

DIPLOMADO EN

ARQUITECTURA DE SOFTWARE

TÉCNICAS: DISEÑO ADD

---

## Lámina 2

ATTRIBUTE-DRIVEN DESIGN (ADD)

> **Notas del orador:** Architectural design for software systems is no different than design in general: It involves making decisions, and working with the available materials and skills, to satisfy requirements and constraints. In architectural design, we turn decisions about architectural drivers into structures, as shown in  Figure 20.1 . Architectural drivers comprise architecturally significant requirements (ASRs—the topic of  Chapter 19 ), but also include functionality, constraints, architectural concerns, and design purpose. The resulting structures are then used to guide the project in the many ways we laid out in  Chapter 2 : They guide analysis and construction. They serve as the foundation for educating a new project member. They guide cost and schedule estimations, team formation, risk analysis and mitigation, and, of course, implementation. 5

---

## Lámina 3

Técnicas de Arquitectura - Diseño

El diseño, incluido el diseño arquitectónico, es una actividad compleja de realizar. Implica tomar una miríada de decisiones que toman en cuenta muchos aspectos de un sistema. En el pasado, esta tarea solo se confiaba a ingenieros de software sénior (gurús) con décadas de experiencia ganada con esfuerzo. Un método sistemático proporciona orientación en la realización de esta actividad compleja para que pueda ser aprendida y realizada hábilmente por meros mortales.

Diseño basado en Atributos (ADD): permite diseñar una arquitectura de manera sistemática, repetible y rentable. La repetibilidad y la capacidad de aprendizaje son los sellos distintivos de una disciplina de ingeniería. Para hacer que un método sea repetible y enseñable, necesitamos un conjunto de pasos que cualquier ingeniero debidamente capacitado pueda seguir.

Introducción

---

## Lámina 4

Técnicas de Arquitectura - Diseño

El diseño arquitectónico para sistemas de software no es diferente del diseño en general: implica tomar decisiones y trabajar con los materiales y habilidades disponibles para satisfacer los requisitos y las limitaciones. En el diseño arquitectónico, convertimos las decisiones sobre los impulsores arquitectónicos en estructuras. Los drivers arquitectónicos comprenden requisitos significativos desde el punto de vista arquitectónico (ASR), pero también incluyen funcionalidad, restricciones, preocupaciones arquitectónicas y propósito de diseño. Luego, las estructuras resultantes se utilizan para guiar el proyecto de muchas formas. Sirven como base para educar a un nuevo miembro del proyecto. Guían las estimaciones de costos y cronogramas, la formación de equipos, el análisis y la mitigación de riesgos y, por supuesto, la implementación.

Attribute-Driven Design (ADD)

---

## Lámina 5

Técnicas de Arquitectura - Diseño

Descripción general de la actividad de diseño de arquitectura

Attribute-Driven Design (ADD)

---

## Lámina 6

Técnicas de Arquitectura - Diseño

Antes de comenzar el diseño de la arquitectura, es importante determinar el alcance del sistema: qué hay dentro y qué hay fuera del sistema que está creando y con qué entidades externas interactuará el sistema. Este contexto se puede representar usando un diagrama de contexto del sistema.

Attribute-Driven Design (ADD)

> **Notas del orador:** Architectural design for software systems is no different than design in general: It involves making decisions, and working with the available materials and skills, to satisfy requirements and constraints. In architectural design, we turn decisions about architectural drivers into structures, as shown in  Figure 20.1 . Architectural drivers comprise architecturally significant requirements (ASRs—the topic of  Chapter 19 ), but also include functionality, constraints, architectural concerns, and design purpose. The resulting structures are then used to guide the project in the many ways we laid out in  Chapter 2 : They guide analysis and construction. They serve as the foundation for educating a new project member. They guide cost and schedule estimations, team formation, risk analysis and mitigation, and, of course, implementation. 9

---

## Lámina 7

Técnicas de Arquitectura - Diseño

Attribute-Driven Design (ADD)

> **Notas del orador:** Architectural design for software systems is no different than design in general: It involves making decisions, and working with the available materials and skills, to satisfy requirements and constraints. In architectural design, we turn decisions about architectural drivers into structures, as shown in  Figure 20.1 . Architectural drivers comprise architecturally significant requirements (ASRs—the topic of  Chapter 19 ), but also include functionality, constraints, architectural concerns, and design purpose. The resulting structures are then used to guide the project in the many ways we laid out in  Chapter 2 : They guide analysis and construction. They serve as the foundation for educating a new project member. They guide cost and schedule estimations, team formation, risk analysis and mitigation, and, of course, implementation. 10

---

## Lámina 8

Técnicas de Arquitectura - Diseño

Paso 1: Revise las entradas

Antes de comenzar una ronda de diseño, debe asegurarse de que los drivers arquitectónicos (las entradas del proceso de diseño) estén disponibles y sean correctos. Éstas incluyen:

El propósito de la ronda de diseño.

Los requisitos funcionales primarios.

Los escenarios de atributos de calidad primarios (QA)

Cualquier restricción

Cualquier preocupación

Attribute-Driven Design (ADD)

> **Notas del orador:** Architectural design for software systems is no different than design in general: It involves making decisions, and working with the available materials and skills, to satisfy requirements and constraints. In architectural design, we turn decisions about architectural drivers into structures, as shown in  Figure 20.1 . Architectural drivers comprise architecturally significant requirements (ASRs—the topic of  Chapter 19 ), but also include functionality, constraints, architectural concerns, and design purpose. The resulting structures are then used to guide the project in the many ways we laid out in  Chapter 2 : They guide analysis and construction. They serve as the foundation for educating a new project member. They guide cost and schedule estimations, team formation, risk analysis and mitigation, and, of course, implementation. 11

---

## Lámina 9

Técnicas de Arquitectura - Diseño

Paso 2: Establecer el objetivo de la iteración mediante la selección de drivers

Cada iteración de diseño se enfoca en lograr un objetivo particular. Tal objetivo generalmente implica diseñar para satisfacer un subconjunto de los drivers. Por ejemplo, un objetivo de iteración podría ser crear estructuras a partir de elementos que permitan lograr un escenario de rendimiento particular o un caso de uso. Por este motivo, al realizar actividades de diseño, debe establecer un objetivo antes de iniciar una iteración de diseño en particular.

Attribute-Driven Design (ADD)

> **Notas del orador:** Architectural design for software systems is no different than design in general: It involves making decisions, and working with the available materials and skills, to satisfy requirements and constraints. In architectural design, we turn decisions about architectural drivers into structures, as shown in  Figure 20.1 . Architectural drivers comprise architecturally significant requirements (ASRs—the topic of  Chapter 19 ), but also include functionality, constraints, architectural concerns, and design purpose. The resulting structures are then used to guide the project in the many ways we laid out in  Chapter 2 : They guide analysis and construction. They serve as the foundation for educating a new project member. They guide cost and schedule estimations, team formation, risk analysis and mitigation, and, of course, implementation. 12

---

## Lámina 10

Técnicas de Arquitectura - Diseño

Paso 3: Elegir uno o más elementos del sistema para refinar

Satisfacer los drivers requiere que tome decisiones de diseño arquitectónico, que luego se manifiestan en una o más estructuras arquitectónicas. Estas estructuras se componen de elementos interrelacionados (módulos y/o componentes) y estos elementos generalmente se obtienen al refinar otros elementos que identificó previamente en una iteración anterior. El refinamiento puede significar la descomposición en elementos de grano más fino (enfoque de arriba hacia abajo), la combinación de elementos en elementos de grano más grueso (enfoque de abajo hacia arriba) o la mejora de elementos previamente identificados.

Attribute-Driven Design (ADD)

> **Notas del orador:** Architectural design for software systems is no different than design in general: It involves making decisions, and working with the available materials and skills, to satisfy requirements and constraints. In architectural design, we turn decisions about architectural drivers into structures, as shown in  Figure 20.1 . Architectural drivers comprise architecturally significant requirements (ASRs—the topic of  Chapter 19 ), but also include functionality, constraints, architectural concerns, and design purpose. The resulting structures are then used to guide the project in the many ways we laid out in  Chapter 2 : They guide analysis and construction. They serve as the foundation for educating a new project member. They guide cost and schedule estimations, team formation, risk analysis and mitigation, and, of course, implementation. 13

---

## Lámina 11

Técnicas de Arquitectura - Diseño

Paso 3: Elegir uno o más elementos del sistema para refinar

Para el desarrollo totalmente nuevo, puede comenzar por establecer el contexto del sistema y luego seleccionar el único elemento disponible, es decir, el sistema mismo, para refinarlo mediante descomposición. Para sistemas existentes o para iteraciones de diseño posteriores en sistemas totalmente nuevos, normalmente elige refinar elementos que se identificaron en iteraciones anteriores.

Attribute-Driven Design (ADD)

> **Notas del orador:** Architectural design for software systems is no different than design in general: It involves making decisions, and working with the available materials and skills, to satisfy requirements and constraints. In architectural design, we turn decisions about architectural drivers into structures, as shown in  Figure 20.1 . Architectural drivers comprise architecturally significant requirements (ASRs—the topic of  Chapter 19 ), but also include functionality, constraints, architectural concerns, and design purpose. The resulting structures are then used to guide the project in the many ways we laid out in  Chapter 2 : They guide analysis and construction. They serve as the foundation for educating a new project member. They guide cost and schedule estimations, team formation, risk analysis and mitigation, and, of course, implementation. 14

---

## Lámina 12

Técnicas de Arquitectura - Diseño

Paso 3: Elegir uno o más elementos del sistema para refinar

Los elementos que seleccionará son los que intervienen en la satisfacción de drivers específicos. Por esta razón, cuando el diseño aborda un sistema existente, debe tener una buena comprensión de los elementos que forman parte de la arquitectura construida del sistema. La obtención de esta información puede implicar algún "trabajo de detective", ingeniería inversa o conversaciones con los desarrolladores.

Attribute-Driven Design (ADD)

> **Notas del orador:** Architectural design for software systems is no different than design in general: It involves making decisions, and working with the available materials and skills, to satisfy requirements and constraints. In architectural design, we turn decisions about architectural drivers into structures, as shown in  Figure 20.1 . Architectural drivers comprise architecturally significant requirements (ASRs—the topic of  Chapter 19 ), but also include functionality, constraints, architectural concerns, and design purpose. The resulting structures are then used to guide the project in the many ways we laid out in  Chapter 2 : They guide analysis and construction. They serve as the foundation for educating a new project member. They guide cost and schedule estimations, team formation, risk analysis and mitigation, and, of course, implementation. 15

---

## Lámina 13

Técnicas de Arquitectura - Diseño

Paso 3: Elegir uno o más elementos del sistema para refinar

En algunos casos, es posible que deba invertir el orden de los pasos 2 y 3. Por ejemplo, al diseñar un sistema totalmente nuevo o al desarrollar ciertos tipos de arquitecturas de referencia, al menos en las primeras etapas del diseño, se centrará en los elementos del sistema y comience la iteración seleccionando un elemento en particular y luego considerando los controladores que desea abordar.

Attribute-Driven Design (ADD)

> **Notas del orador:** Architectural design for software systems is no different than design in general: It involves making decisions, and working with the available materials and skills, to satisfy requirements and constraints. In architectural design, we turn decisions about architectural drivers into structures, as shown in  Figure 20.1 . Architectural drivers comprise architecturally significant requirements (ASRs—the topic of  Chapter 19 ), but also include functionality, constraints, architectural concerns, and design purpose. The resulting structures are then used to guide the project in the many ways we laid out in  Chapter 2 : They guide analysis and construction. They serve as the foundation for educating a new project member. They guide cost and schedule estimations, team formation, risk analysis and mitigation, and, of course, implementation. 16

---

## Lámina 14

Técnicas de Arquitectura - Diseño

Paso 4: Elegir uno o más conceptos de diseño que satisfagan los drivers seleccionados

Elegir los conceptos de diseño es probablemente la decisión más difícil a la que se enfrentará en el proceso de diseño, ya que requiere que identifique los diversos conceptos de diseño que podrían usarse para lograr su objetivo de iteración y luego hacer una selección de esas alternativas. Hay muchos tipos diferentes de conceptos de diseño disponibles, por ejemplo, tácticas, patrones, arquitecturas de referencia y componentes desarrollados externamente y, para cada tipo, pueden existir muchas opciones. Esto puede resultar en un número considerable de alternativas que necesitan ser analizadas antes de tomar la decisión final.

Attribute-Driven Design (ADD)

> **Notas del orador:** Architectural design for software systems is no different than design in general: It involves making decisions, and working with the available materials and skills, to satisfy requirements and constraints. In architectural design, we turn decisions about architectural drivers into structures, as shown in  Figure 20.1 . Architectural drivers comprise architecturally significant requirements (ASRs—the topic of  Chapter 19 ), but also include functionality, constraints, architectural concerns, and design purpose. The resulting structures are then used to guide the project in the many ways we laid out in  Chapter 2 : They guide analysis and construction. They serve as the foundation for educating a new project member. They guide cost and schedule estimations, team formation, risk analysis and mitigation, and, of course, implementation. 17

---

## Lámina 15

Técnicas de Arquitectura - Diseño

Paso 5: Crear instancias de elementos arquitectónicos, asignar responsabilidades y definir interfaces

Una vez que haya seleccionado uno o más conceptos de diseño, debe tomar otro tipo de decisión de diseño: cómo instanciar elementos a partir de los conceptos de diseño que acaba de seleccionar. Por ejemplo, si seleccionó el patrón de capas como concepto de diseño, debe decidir cuántas capas se utilizarán y sus relaciones permitidas, ya que el patrón en sí no las prescribe.

Attribute-Driven Design (ADD)

> **Notas del orador:** Architectural design for software systems is no different than design in general: It involves making decisions, and working with the available materials and skills, to satisfy requirements and constraints. In architectural design, we turn decisions about architectural drivers into structures, as shown in  Figure 20.1 . Architectural drivers comprise architecturally significant requirements (ASRs—the topic of  Chapter 19 ), but also include functionality, constraints, architectural concerns, and design purpose. The resulting structures are then used to guide the project in the many ways we laid out in  Chapter 2 : They guide analysis and construction. They serve as the foundation for educating a new project member. They guide cost and schedule estimations, team formation, risk analysis and mitigation, and, of course, implementation. 18

---

## Lámina 16

Técnicas de Arquitectura - Diseño

Paso 5: Crear instancias de elementos arquitectónicos, asignar responsabilidades y definir interfaces

Después de instanciar los elementos, debe asignar responsabilidades a cada uno de ellos. Por ejemplo, en una aplicación, suelen estar presentes al menos tres capas: presentación, negocio y datos. Las responsabilidades de estas capas difieren: las responsabilidades de la capa de presentación incluyen la gestión de todas las interacciones del usuario, la capa empresarial gestiona la lógica de la aplicación y hace cumplir las reglas empresariales, y la capa de datos gestiona la persistencia y coherencia de los datos.

Attribute-Driven Design (ADD)

---

## Lámina 17

Técnicas de Arquitectura - Diseño

Paso 5: Crear instancias de elementos arquitectónicos, asignar responsabilidades y definir interfaces

Instanciar elementos es solo una parte de la creación de estructuras que satisfagan un driver o una preocupación. Los elementos que se han instanciado también deben estar conectados, lo que les permite colaborar entre sí. Esto requiere la existencia de relaciones entre los elementos y el intercambio de información a través de algún tipo de interfaz. La interfaz es una especificación contractual que indica cómo debe fluir la información entre los elementos.

Attribute-Driven Design (ADD)

---

## Lámina 18

Técnicas de Arquitectura - Diseño

Paso 6: Diagramar las vistas y registrar las decisiones de diseño.

En este punto, ha terminado de realizar las actividades de diseño para la iteración. Sin embargo, es posible que no haya tomado ninguna medida para asegurarse de que las vistas, las representaciones de las estructuras que creó, se conserven. Por ejemplo, si realizó el paso 5 en una sala de conferencias, probablemente terminó con una serie de diagramas en una pizarra. Esta información es esencial para el resto del proceso y debe capturarla para luego analizarla y comunicarla a otras partes interesadas. Capturar las vistas puede ser tan simple como tomar una foto de la pizarra.

Attribute-Driven Design (ADD)

---

## Lámina 19

Técnicas de Arquitectura - Diseño

Paso 6: Diagramar las vistas y registrar las decisiones de diseño.

Es casi seguro que las vistas que ha creado no están completas; por lo tanto, es posible que estos diagramas deban revisarse y refinarse en una iteración posterior. Esto normalmente se hace para acomodar elementos resultantes de otras decisiones de diseño que tomará para admitir controladores adicionales. Es por esto que hablamos de “bocetar” las vistas en ADD, donde un “boceto” se refiere a un tipo de documentación preliminar. La documentación más formal y completa de estas vistas, en caso de que decida producirla, ocurre solo después de que se hayan terminado las iteraciones de diseño (como parte de la actividad de documentación arquitectónica).

Attribute-Driven Design (ADD)

---

## Lámina 20

Técnicas de Arquitectura - Diseño

Paso 6: Diagramar las vistas y registrar las decisiones de diseño.

Además de capturar los bocetos de las vistas, debe registrar las decisiones importantes tomadas en la iteración del diseño, así como las razones que motivaron estas decisiones (es decir, la justificación), para facilitar el análisis y la comprensión posteriores de las decisiones. Por ejemplo, las decisiones sobre tradeoffs importantes deben registrarse en este momento. Durante una iteración de diseño, las decisiones se toman principalmente en los pasos 4 y 5.

Attribute-Driven Design (ADD)

---

## Lámina 21

Técnicas de Arquitectura - Diseño

Paso 7: Realizar un análisis del diseño actual y revisar el objetivo de la iteración y el logro del propósito del diseño

Para este paso, debería haber creado un diseño parcial que aborde el objetivo establecido para la iteración. Asegurarse de que este caso sea realmente una buena idea, para evitar stakeholders insatisfechos y reprocesos. Puede realizar el análisis usted mismo revisando los bocetos de las vistas y las decisiones de diseño que capturó, pero una idea aún mejor es que alguien más lo ayude a revisar este diseño. Hacemos esto por la misma razón por la que las organizaciones suelen tener un grupo de pruebas/control de calidad separado: otra persona no compartirá sus suposiciones y tendrá una base de experiencia diferente y una perspectiva diferente.

Attribute-Driven Design (ADD)

---

## Lámina 22

Técnicas de Arquitectura - Diseño

Paso 7: Realizar un análisis del diseño actual y revisar el objetivo de la iteración y el logro del propósito del diseño

Una vez que se haya analizado el diseño realizado en la iteración, debe revisar el estado de su arquitectura en términos de su propósito de diseño establecido. Esto significa considerar si, en este punto, ha realizado suficientes iteraciones de diseño para satisfacer los controladores asociados con la ronda de diseño. También significa considerar si se ha logrado el propósito del diseño o si se necesitan rondas de diseño adicionales en futuros incrementos del proyecto.

Attribute-Driven Design (ADD)

---

## Lámina 23

Técnicas de Arquitectura - Diseño

Iterar si es necesario

Debe realizar iteraciones adicionales y repetir los pasos 2 a 7 para cada driver que se consideró. Sin embargo, la mayoría de las veces, este tipo de repetición no será posible debido a limitaciones de tiempo o de recursos que lo obligan a detener las actividades de diseño y pasar a la implementación. ¿Cuáles son los criterios para evaluar si son necesarias más iteraciones de diseño? Deje que el riesgo sea su guía. Al menos debería haberse dirigido a los controladores con la mayor prioridad. Idealmente, debe tener la certeza de que los controladores críticos están satisfechos o, al menos, que el diseño es "suficientemente bueno" para satisfacerlos.

Attribute-Driven Design (ADD)

---

## Lámina 24

Técnicas de Arquitectura - Diseño

Attribute-Driven Design (ADD)

https://smartdecisionsgame.com/

---

## Lámina 25

Humberto Cervantes, Rick Kazman. Designing Software Architectures: A Practical Approach. SEI / Addison-Wesley, 2016.

Bibliografía

Len Bass, Paul Clements, Rick Kazman. Software Architecture in Practice. 4th Edition. SEI / Addison-Wesley, 2022​

---

## Lámina 26

_(sin texto: la lámina es una imagen)_
