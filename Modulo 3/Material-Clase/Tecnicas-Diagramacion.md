# Técnicas de Diagramación — deck oficial del Módulo 3

> **Tipo:** `material-oficial` (Recursos complementarios → «Presentaciones Adicionales», Brightspace, Unidad 4 de 5).
> **Fuente:** `TecnicasDiagramacion.pptx` (31 láminas), descargado el 2026-10-18 con sesión de Danny.
> **Extraído:** 2026-10-18, texto de las láminas tal cual. Las **notas del orador** se incluyen aparte
>  porque traen contenido (a menudo en inglés, del libro de referencia); las que solo tienen un número se omiten.
> **Límite de la extracción:** solo texto. Diagramas, figuras y tablas dibujadas como imagen NO están.
> **Este archivo no se edita.** Las notas y críticas van en `Aportes/`.

---

## Lámina 1

DIPLOMADO EN

ARQUITECTURA DE SOFTWARE

TÉCNICAS: DIAGRAMACIÓN

> **Notas del orador:** When visually describing an architecture, the creator often must show different views of the architecture. For example, the architect will likely show an overview of the entire architecture topology, then drill into individual parts to delve into design details. However, if the architect shows a portion without indicating where it lies within the overall architecture, it confuses viewers.  Representational consistency  is the practice of always showing the relationship between parts of an architecture, either in diagrams or presentations, before changing views.   4

---

## Lámina 2

DIAGRAMACIÓN

---

## Lámina 3

Diagramando la Arquitectura

Al describir visualmente una arquitectura, el creador a menudo debe mostrar diferentes puntos de vista. Por ejemplo, es probable que el arquitecto muestre una descripción general de toda la topología de la arquitectura y luego profundice en las partes individuales para profundizar en los detalles del diseño. Sin embargo, si el arquitecto muestra una parte sin indicar dónde se encuentra dentro de la arquitectura general, confunde a los espectadores. La consistencia representacional es la práctica de mostrar siempre la relación entre las partes de una arquitectura, ya sea en diagramas o presentaciones, antes de cambiar de vista.

Introducción

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Documenting an architecture requires behavior documentation that complements the structural views by describing how architecture elements interact with each other. Reasoning about characteristics such as a system’s potential to deadlock, a system’s ability to complete a task in the desired amount of time, or maximum memory consumption requires that the architecture description provide information about the characteristics of individual elements and their resource consumption, as well as patterns of interaction among them—that is, how they behave in relation to each other. In this section, we provide guidance as to what types of things you will want to document to reap these benefits. 7

---

## Lámina 4

UML

> **Notas del orador:** A UML  sequence diagram  shows a sequence of interactions among instances of elements pulled from the structural documentation. It is useful, when designing a system, for identifying where interfaces need to be defined. The sequence diagram shows only the instances participating in the scenario being documented. It has two dimensions: vertical, representing time, and horizontal, representing the various instances. The interactions are arranged in time sequence from top to bottom 8

---

## Lámina 5

Diagramando la Arquitectura

El lenguaje de modelado unificado (UML) fue un estándar que unificó tres filosofías de diseño en competencia que coexistieron en la década de 1980. Se suponía que era lo mejor de todos los mundos, pero, como muchas cosas diseñadas por el comité, no logró crear mucho impacto fuera de las organizaciones que exigían su uso. Los arquitectos y desarrolladores todavía usan diagramas de secuencia y clase UML para comunicar la estructura y el flujo de trabajo, pero la mayoría de los otros tipos de diagramas UML han caído en desuso.

Estándares de Diagramación - UML

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** UML  activity diagrams  are similar to flowcharts. They show a business process as a sequence of steps (called actions) and include notation to express conditional branching and concurrency, as well as to show sending and receiving events. Arrows between actions indicate the flow of control. Optionally, activity diagrams can indicate the architecture element or actor performing the actions. Notably, activity diagrams can express concurrency. A fork node (depicted as a thick bar orthogonal to the flow arrows) splits the flow into two or more concurrent flows of actions. These concurrent flows may later be synchronized into a single flow through a join node (also depicted as an orthogonal bar). The join node waits for all incoming flows to complete before proceeding. 9

---

## Lámina 6

Diagramando la Arquitectura

Documentar una arquitectura requiere una documentación del comportamiento que complemente las vistas estructurales al describir cómo interactúan los elementos de la arquitectura entre sí. Razonar sobre características tales como el potencial de un sistema para bloquearse, la capacidad de un sistema para completar una tarea en la cantidad de tiempo deseada o el consumo máximo de memoria requiere que la descripción de la arquitectura proporcione información sobre las características de los elementos individuales y su consumo de recursos, así como patrones de interacción entre ellos, es decir, cómo se comportan entre sí.

Estándares de Diagramación - UML

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** C4 C4 is a diagramming technique developed by Simon Brown to address deficiencies in UML and modernize its approach. The four C’s in C4 are as follows: Context Represents the entire context of the system, including the roles of users and external dependencies. Container The physical (and often logical) deployment boundaries and containers within the architecture. This view forms a good meeting point for operations and architects. Component The component view of the system; this most neatly aligns with an architect’s view of the system. Class C4 uses the same style of class diagrams from UML, which are effective, so there is no need to replace them. If a company seeks to standardize on a diagramming technique, C4 offers a good alternative. However, like all technical diagramming tools, it suffers from an inability to express every kind of design an architecture might undertake. C4 is best suited for monolithic architectures where the container and component relationships may differ, and it’s less suited to distributed architectures, such as microservices. 11

---

## Lámina 7

Diagramando la Arquitectura

Un diagrama de secuencia UML muestra una secuencia de interacciones entre instancias de elementos extraídos de la documentación estructural. Es útil, al diseñar un sistema, para identificar dónde se deben definir las interfaces. El diagrama de secuencia muestra solo las instancias que participan en el escenario que se está documentando. Tiene dos dimensiones: vertical, que representa el tiempo, y horizontal, que representa las distintas instancias. Las interacciones se organizan en secuencia de tiempo de arriba a abajo.

Estándares de Diagramación - UML

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** C4 C4 is a diagramming technique developed by Simon Brown to address deficiencies in UML and modernize its approach. The four C’s in C4 are as follows: Context Represents the entire context of the system, including the roles of users and external dependencies. Container The physical (and often logical) deployment boundaries and containers within the architecture. This view forms a good meeting point for operations and architects. Component The component view of the system; this most neatly aligns with an architect’s view of the system. Class C4 uses the same style of class diagrams from UML, which are effective, so there is no need to replace them. If a company seeks to standardize on a diagramming technique, C4 offers a good alternative. However, like all technical diagramming tools, it suffers from an inability to express every kind of design an architecture might undertake. C4 is best suited for monolithic architectures where the container and component relationships may differ, and it’s less suited to distributed architectures, such as microservices. 12

---

## Lámina 8

Diagramando la Arquitectura

Los diagramas de actividad UML son similares a los diagramas de flujo. Muestran un proceso de negocio como una secuencia de pasos (llamados acciones) e incluyen notación para expresar ramificación condicional y concurrencia, así como para mostrar eventos de envío y recepción. Las flechas entre las acciones indican el flujo de control. Opcionalmente, los diagramas de actividad pueden indicar el elemento de la arquitectura o el actor que realiza las acciones. En particular, los diagramas de actividad pueden expresar concurrencia.

Estándares de Diagramación - UML

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 9

C4

---

## Lámina 10

Diagramando la Arquitectura

C4 es una técnica de diagramación desarrollada por Simon Brown para abordar las deficiencias en UML y modernizar su enfoque. Las cuatro C en C4 son las siguientes:

Contexto: Representa todo el contexto del sistema, incluidas las funciones de los usuarios y las dependencias externas.

Contenedores: Los límites y contenedores de implementación físicos (y a menudo lógicos) dentro de la arquitectura. Esta vista constituye un buen punto de encuentro para operaciones y arquitectos.

Estándares de Diagramación - C4

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 11

Diagramando la Arquitectura

Componente: La vista de componentes del sistema; esto se alinea más claramente con la visión del sistema de un arquitecto.

Clases / Código: C4 usa el mismo estilo de diagramas de clases de UML, que son efectivos, por lo que no es necesario reemplazarlos.

Estándares de Diagramación - C4

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 12

Diagramando la Arquitectura

Estándares de Diagramación - C4

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 13

Diagramando la Arquitectura

Estándares de Diagramación - C4

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 14

Diagramando la Arquitectura

Estándares de Diagramación - C4 - Contexto

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** ArchiMate ArchiMate (an amalgam of Arch* itecture -Ani*mate) is an open source enterprise architecture modeling language to support the description, analysis, and visualization of architecture within and across business domains. ArchiMate is a technical standard from The Open Group, and it offers a lighter-weight modeling language for enterprise ecosystems. The goal of ArchiMate is to be “as small as possible,” not to cover every edge case scenario. As such, it has become a popular choice among many architects. 20

---

## Lámina 15

Diagramando la Arquitectura

Estándares de Diagramación - C4 - Contenedores

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 16

Diagramando la Arquitectura

Estándares de Diagramación - C4 - Componentes

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** The ArchiMate core language defines a structure of generic elements and their relationships, which can be specialized in different layers. Three layers are defined within the ArchiMate core language as follows: Business Layer The Business Layer offers products and services to external customers, which are realized in the organization by business processes performed by business actors. Application Layer The Application Layer supports the business layer with application services which are realized by (software) applications. Technology Layer The Technology Layer offers infrastructure services (e.g., processing, storage, and communication services) needed to run applications, realized by computer and communication hardware and system software. These layers are shared by other frameworks, most important of which is TOGAF, although TOGAF call them Business, Information System (Application and Data) and Information Technology. 22

---

## Lámina 17

Diagramando la Arquitectura

Estándares de Diagramación - C4 - Código/Clases

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** The ArchiMate core language defines a structure of generic elements and their relationships, which can be specialized in different layers. Three layers are defined within the ArchiMate core language as follows: Business Layer:  The Business Layer offers products and services to external customers, which are realized in the organization by business processes performed by business actors. Application Layer:  The Application Layer supports the business layer with application services which are realized by (software) applications. Technology Layer:  The Technology Layer offers infrastructure services (e.g., processing, storage, and communication services) needed to run applications, realized by computer and communication hardware and system software. These layers are shared by other frameworks, most important of which is TOGAF, although TOGAF call them Business, Information System (Application and Data) and Information Technology. 23

---

## Lámina 18

ARCHIMATE

---

## Lámina 19

Diagramando la Arquitectura

ArchiMate (una amalgama de Arch*itecture-Ani*mate) es un lenguaje de modelado de arquitectura empresarial de código abierto para respaldar la descripción, el análisis y la visualización de la arquitectura dentro y entre los dominios de negocio. ArchiMate es un estándar técnico de The Open Group y ofrece un lenguaje de modelado más liviano para ecosistemas empresariales. El objetivo de ArchiMate es ser "lo más pequeño posible", no cubrir todos los escenarios de casos extremos. Como tal, se ha convertido en una opción popular entre muchos arquitectos.

Estándares de Diagramación - ArchiMate

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 20

Diagramando la Arquitectura

Estándares de Diagramación - ArchiMate

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 21

Diagramando la Arquitectura

El lenguaje core de ArchiMate define una estructura de elementos genéricos y sus relaciones, que pueden especializarse en diferentes capas. Tres capas se definen dentro del lenguaje de ArchiMate de la siguiente manera:

Capa empresarial: ofrece productos y servicios a clientes externos, que se realizan en la organización por procesos de negocio ejecutados por actores de negocio.

Estándares de Diagramación - ArchiMate

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 22

Diagramando la Arquitectura

Capa de aplicación Esta capa soporta la capa empresarial con servicios de aplicación que son realizados por aplicaciones (software).

Capa de tecnología La capa de tecnología ofrece servicios de infraestructura (por ejemplo, procesamiento, almacenamiento y servicios de comunicación) necesarios para ejecutar aplicaciones, realizados por computadora y hardware de comunicación y software del sistema.

Estándares de Diagramación - ArchiMate

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 23

Diagramando la Arquitectura

Estándares de Diagramación - ArchiMate

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 24

Diagramando la Arquitectura

Estándares de Diagramación - ArchiMate

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 25

Diagramando la Arquitectura

Estándares de Diagramación - ArchiMate

Maestría en Ingeniería de Software – Arquitectura de Software

Elementos de Estructuras Activas

---

## Lámina 26

Diagramando la Arquitectura

Estándares de Diagramación - ArchiMate

Maestría en Ingeniería de Software – Arquitectura de Software

Elementos de Comportamiento

---

## Lámina 27

Diagramando la Arquitectura

Estándares de Diagramación - ArchiMate

Maestría en Ingeniería de Software – Arquitectura de Software

Elementos de Estructuras Pasivas

---

## Lámina 28

Diagramando la Arquitectura

Estándares de Diagramación - ArchiMate

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 29

Diagramando la Arquitectura

Estándares de Diagramación - Tools

Maestría en Ingeniería de Software – Arquitectura de Software

https://softwarearchitecture.tools/

---

## Lámina 30

Bibliografía

Mark Richards, Neal  Ford. Fundamentals of Software Architecture: An Engineering Approach. O'Reilly, 2020.

---

## Lámina 31

_(sin texto: la lámina es una imagen)_
