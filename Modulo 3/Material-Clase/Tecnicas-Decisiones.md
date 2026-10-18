# Técnicas de Decisiones — deck oficial del Módulo 3

> **Tipo:** `material-oficial` (Recursos complementarios → «Presentaciones Adicionales», Brightspace, Unidad 4 de 5).
> **Fuente:** `TecnicasDecisiones.pptx` (40 láminas), descargado el 2026-10-18 con sesión de Danny.
> **Extraído:** 2026-10-18, texto de las láminas tal cual. Las **notas del orador** se incluyen aparte
>  porque traen contenido (a menudo en inglés, del libro de referencia); las que solo tienen un número se omiten.
> **Límite de la extracción:** solo texto. Diagramas, figuras y tablas dibujadas como imagen NO están.
> **Este archivo no se edita.** Las notas y críticas van en `Aportes/`.

---

## Lámina 1

DIPLOMADO EN

ARQUITECTURA DE SOFTWARE

TÉCNICAS: DECISIONES

> **Notas del orador:** One of the core expectations of an architect is to make architecture decisions. Architecture decisions usually involve the structure of the application or system, but they may involve technology decisions as well, particularly when those technology decisions impact architecture characteristics. Whatever the context, a good architecture decision is one that helps guide development teams in making the right technical choices. Making architecture decisions involves gathering enough relevant information, justifying the decision, documenting the decision, and effectively communicating that decision to the right stakeholders.   4

---

## Lámina 2

DECISIONES DE ARQUITECTURA

> **Notas del orador:** One of the core expectations of an architect is to make architecture decisions. Architecture decisions usually involve the structure of the application or system, but they may involve technology decisions as well, particularly when those technology decisions impact architecture characteristics. Whatever the context, a good architecture decision is one that helps guide development teams in making the right technical choices. Making architecture decisions involves gathering enough relevant information, justifying the decision, documenting the decision, and effectively communicating that decision to the right stakeholders.   5

---

## Lámina 3

Técnicas de Arquitectura - Decisiones

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** One of the core expectations of an architect is to make architecture decisions. Architecture decisions usually involve the structure of the application or system, but they may involve technology decisions as well, particularly when those technology decisions impact architecture characteristics. Whatever the context, a good architecture decision is one that helps guide development teams in making the right technical choices. Making architecture decisions involves gathering enough relevant information, justifying the decision, documenting the decision, and effectively communicating that decision to the right stakeholders.   7

---

## Lámina 4

Técnicas de Arquitectura - Decisiones

Una de las principales expectativas de un arquitecto es tomar decisiones de arquitectura. Las decisiones de arquitectura generalmente involucran la estructura de la aplicación o el sistema, pero también pueden involucrar decisiones de tecnología, particularmente cuando esas decisiones de tecnología afectan las características de la arquitectura.

Una buena decisión de arquitectura es aquella que ayuda a guiar a los equipos de desarrollo a tomar las decisiones técnicas correctas. Tomar decisiones de arquitectura implica recopilar suficiente información relevante, justificar la decisión, documentar la decisión y comunicar efectivamente esa decisión a las partes interesadas correctas.

Introducción

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Covering Your Assets Anti-Pattern The first anti-pattern to emerge when trying to make architecture decisions is the Covering Your Assets anti-pattern. This anti-pattern occurs when an architect avoids or defers making an architecture decision out of fear of making the wrong choice. There are two ways to overcome this anti-pattern. The first is to wait until the  last responsible moment  to make an important architecture decision. The last responsible moment means waiting until you have enough information to justify and validate your decision, but not waiting so long that you hold up development teams or fall into the  Analysis Paralysis  anti-pattern. The second way to avoid this anti-pattern is to continually collaborate with development teams to ensure that the decision you made can be implemented as expected. This is vitally important because it is not feasible as an architect to possibly know every single detail about a particular technology and all the associated issues. By closely collaborating with development teams, the architect can respond quickly to a change in the architecture decision if issues occur. To illustrate this point, suppose an architect makes the decision that all product-related reference data (product description, weight, and dimensions) be cached in all service instances needing that information using a read-only replicated cache, with the primary replica owned by the catalog service. A replicated cache means that if there are any changes to product information (or a new product is added), the catalog service would update its cache, which would then be replicated to all other services requiring that data through a replicated (in-memory) cache product. A good justification for this decision is to reduce coupling between the services and to effectively share data without having to make an interservice call. However, the development teams implementing this architecture decision find that due to certain scalability requirements of some of the services, this decision would require more in-process memory than is available. By closely collaborating with the development teams, the architect can quickly become aware of the issue and adjust the architecture decision to accommodate these situations.   8

---

## Lámina 5

ANTIPATRONES

> **Notas del orador:** Groundhog Day Anti-Pattern Once an architect overcomes the Covering Your Assets anti-pattern and starts making decisions, a second anti-pattern emerges: the Groundhog Day anti-pattern. The Groundhog Day anti-pattern occurs when people don’t know why a decision was made, so it keeps getting discussed over and over and over. The Groundhog Day anti-pattern gets it name from the Bill Murray movie  Groundhog Day , where it was February 2 over and over every day. The Groundhog Day anti-pattern occurs because once an architect makes an architecture decision, they fail to provide a justification for the decision (or a complete justification). When justifying architecture decisions it is important to provide both technical and business justifications for your decision. For example, an architect may make the decision to break apart a monolithic application into separate services to decouple the functional aspects of the application so that each part of the application uses fewer virtual machine resources and can be maintained and deployed separately. While this is a good example of a technical justification, what is missing is the business justification—in other words, why should the business pay for this architectural refactoring? A good business justification for this decision might be to deliver new business functionality faster, therefore improving time to market. Another might be to reduce the costs associated with the development and release of new features. Providing the business value when justifying decisions is vitally important for any architecture decision. It is also a good litmus test for determining whether the architecture decision should be made in the first place. If a particular architecture decision does not provide any business value, then perhaps it is not a good decision and should be reconsidered. Four of the most common business justifications include cost, time to market, user satisfaction, and strategic positioning. When focusing on these common business justifications, it is important to take into consideration what is important to the business stakeholders. Justifying a particular decision based on cost savings alone might not be the right decision if the business stakeholders are less concerned about cost and more concerned about time to market. 8

---

## Lámina 6

Técnicas de Arquitectura - Decisiones

La toma de decisiones de arquitectura es un Arte. No en vano, surgen varios antipatrones de arquitectura a la hora de tomar decisiones como arquitecto. El programador Andrew Koenig define un antipatrón como algo que parece una buena idea cuando comienzas, pero te lleva a problemas. Otra definición de antipatrón es un proceso repetible que produce resultados negativos. Los tres principales antipatrones de arquitectura son:

Covering Your Assets

Groundhog Day

Email-Driven Architecture.

Tomar decisiones de arquitectura efectivas y precisas requiere que un arquitecto supere estos tres antipatrones.

Antipatrones

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Groundhog Day Anti-Pattern Once an architect overcomes the Covering Your Assets anti-pattern and starts making decisions, a second anti-pattern emerges: the Groundhog Day anti-pattern. The Groundhog Day anti-pattern occurs when people don’t know why a decision was made, so it keeps getting discussed over and over and over. The Groundhog Day anti-pattern gets it name from the Bill Murray movie  Groundhog Day , where it was February 2 over and over every day. The Groundhog Day anti-pattern occurs because once an architect makes an architecture decision, they fail to provide a justification for the decision (or a complete justification). When justifying architecture decisions it is important to provide both technical and business justifications for your decision. For example, an architect may make the decision to break apart a monolithic application into separate services to decouple the functional aspects of the application so that each part of the application uses fewer virtual machine resources and can be maintained and deployed separately. While this is a good example of a technical justification, what is missing is the business justification—in other words, why should the business pay for this architectural refactoring? A good business justification for this decision might be to deliver new business functionality faster, therefore improving time to market. Another might be to reduce the costs associated with the development and release of new features. Providing the business value when justifying decisions is vitally important for any architecture decision. It is also a good litmus test for determining whether the architecture decision should be made in the first place. If a particular architecture decision does not provide any business value, then perhaps it is not a good decision and should be reconsidered. Four of the most common business justifications include cost, time to market, user satisfaction, and strategic positioning. When focusing on these common business justifications, it is important to take into consideration what is important to the business stakeholders. Justifying a particular decision based on cost savings alone might not be the right decision if the business stakeholders are less concerned about cost and more concerned about time to market. 9

---

## Lámina 7

Técnicas de Arquitectura - Decisiones

Este antipatrón ocurre cuando un arquitecto evita o difiere la toma de una decisión de arquitectura por temor a tomar la decisión equivocada.

Hay dos formas de superar este antipatrón:

La primera es esperar hasta el último momento responsable para tomar una decisión arquitectónica importante. El último momento responsable significa esperar hasta tener suficiente información para justificar y validar su decisión, pero no esperar tanto como para retrasar a los equipos de desarrollo o caer en el antipatrón de Parálisis del Análisis.

La segunda forma de evitar este antipatrón es colaborar continuamente con los equipos de desarrollo para garantizar que la decisión que tomó se pueda implementar como se esperaba

Antipatrones - Covering Your Assets Anti-Pattern

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Email-Driven Architecture Anti-Pattern Once an architect makes decisions and fully justifies those decisions, a third architecture anti-pattern emerges:  Email-Driven Architecture . The Email-Driven Architecture anti-pattern is where people lose, forget, or don’t even know an architecture decision has been made and therefore cannot possibly implement that architecture decision. This anti-pattern is all about effectively communicating your architecture decisions. Email is a great tool for communication, but it makes a poor document repository system. There are many ways to increase the effectiveness of communicating architecture decisions, thereby avoiding the Email-Driven Architecture anti-pattern. The first rule of communicating architecture decisions is to not include the architecture decision in the body of an email. Including the architecture decision in the body of the email creates multiple systems of record for that decision. Many times important details (including the justification) are left out of the email, therefore creating the Groundhog Day anti-pattern all over again. Also, if that architecture decision is ever changed or superseded, how may people received the revised decision? A better approach is to mention only the nature and context of the decision in the body of the email and provide a link to the single system of record for the actual architecture decision and corresponding details (whether it be a link to a wiki page or a document in a filesystem). The second rule of effectively communicating architecture decisions is to only notify those people who really care about the architecture decision. One effective technique is to write the body of the email as follows: “Hi Sandra, I’ve made an important decision regarding communication between services that directly impacts you. Please see the decision using the following link…” Notice the phrasing in the first sentence: “important decision regarding communication between services.” Here, the context of the decision is mentioned, but not the actual decision itself. The second part of the first sentence is even more important: “that directly impacts you.” If an architectural decision doesn’t directly impact the person, then why bother that person with your architecture decision? This is a great litmus test for determining which stakeholders (including developers) should be notified directly of an architecture decision. The second sentence provides a link to the location of the architecture decision so it is located in only one place, hence a single system of record for the decision. 10

---

## Lámina 8

Técnicas de Arquitectura - Decisiones

Una vez que un arquitecto supera el antipatrón Covering Your Assets y comienza a tomar decisiones, surge un segundo antipatrón: el Día de la Marmota. El antipatrón del Día de la Marmota ocurre cuando las personas no saben por qué se tomó una decisión, por lo que se discute una y otra vez. El antipatrón del Día de la Marmota recibe su nombre de la película Groundhog Day de Bill Murray, donde era el 2 de febrero una y otra vez todos los días.

El antipatrón del Día de la Marmota ocurre porque una vez que un arquitecto toma una decisión de arquitectura, no proporciona una justificación para la decisión (o una justificación completa). Al justificar las decisiones de arquitectura, es importante proporcionar justificaciones tanto técnicas como de negocio para su decisión

Antipatrones - Groundhog Day Anti-Pattern

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Email-Driven Architecture Anti-Pattern Once an architect makes decisions and fully justifies those decisions, a third architecture anti-pattern emerges:  Email-Driven Architecture . The Email-Driven Architecture anti-pattern is where people lose, forget, or don’t even know an architecture decision has been made and therefore cannot possibly implement that architecture decision. This anti-pattern is all about effectively communicating your architecture decisions. Email is a great tool for communication, but it makes a poor document repository system. There are many ways to increase the effectiveness of communicating architecture decisions, thereby avoiding the Email-Driven Architecture anti-pattern. The first rule of communicating architecture decisions is to not include the architecture decision in the body of an email. Including the architecture decision in the body of the email creates multiple systems of record for that decision. Many times important details (including the justification) are left out of the email, therefore creating the Groundhog Day anti-pattern all over again. Also, if that architecture decision is ever changed or superseded, how may people received the revised decision? A better approach is to mention only the nature and context of the decision in the body of the email and provide a link to the single system of record for the actual architecture decision and corresponding details (whether it be a link to a wiki page or a document in a filesystem). The second rule of effectively communicating architecture decisions is to only notify those people who really care about the architecture decision. One effective technique is to write the body of the email as follows: “Hi Sandra, I’ve made an important decision regarding communication between services that directly impacts you. Please see the decision using the following link…” Notice the phrasing in the first sentence: “important decision regarding communication between services.” Here, the context of the decision is mentioned, but not the actual decision itself. The second part of the first sentence is even more important: “that directly impacts you.” If an architectural decision doesn’t directly impact the person, then why bother that person with your architecture decision? This is a great litmus test for determining which stakeholders (including developers) should be notified directly of an architecture decision. The second sentence provides a link to the location of the architecture decision so it is located in only one place, hence a single system of record for the decision. 11

---

## Lámina 9

Técnicas de Arquitectura - Decisiones

Proporcionar el valor de negocio al justificar las decisiones es de vital importancia para cualquier decisión de arquitectura. También es una buena prueba de fuego para determinar si la decisión de arquitectura debe tomarse en primer lugar. Si una decisión de arquitectura en particular no proporciona ningún valor para negocio, quizás no sea una buena decisión y deba reconsiderarse.

Cuatro de las justificaciones de negocio más comunes incluyen el costo, el tiempo de comercialización, la satisfacción del usuario y el posicionamiento estratégico.

Justificar una decisión particular basada únicamente en el ahorro de costos podría no ser la decisión correcta si las partes interesadas del negocio están menos preocupadas por los costos y más preocupadas por el tiempo de comercialización.

Antipatrones - Groundhog Day Anti-Pattern

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** One of the most effective ways of documenting architecture decisions is through Architecture Decision Records (ADRs). ADRs were first evangelized by Michael Nygard in a blog post and later marked as “adopt” in the  ThoughtWorks  Technology Radar. An ADR consists of a short text file (usually one to two pages long) describing a specific architecture decision. While ADRs can be written using plain text, they are usually written in some sort of text document format like  AsciiDoc  or Markdown. Alternatively, an ADR can also be written using a wiki page template. 13

---

## Lámina 10

Técnicas de Arquitectura - Decisiones

Una vez que un arquitecto toma decisiones y las justifica por completo, surge un tercer antipatrón de arquitectura: la arquitectura orientada por correo. En este antipatrón las personas pierden, olvidan o ni siquiera saben que se ha tomado una decisión de arquitectura y, por lo tanto, no es posible implementar esa decisión. Este antipatrón tiene que ver con la comunicación efectiva de sus decisiones de arquitectura. El correo electrónico es una gran herramienta para la comunicación, pero es un repositorio de documentos deficiente.

Hay muchas maneras de aumentar la eficacia de la comunicación de las decisiones de arquitectura, evitando así el antipatrón de la arquitectura impulsada por correo electrónico.

Antipatrones - Email-Driven Architecture Anti-Pattern

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** The basic structure of an ADR consists of five main sections:  Title ,  Status ,  Context ,  Decision , and  Consequences . We usually add two additional sections as part of the basic structure:  Compliance  and  Notes . 14

---

## Lámina 11

Técnicas de Arquitectura - Decisiones

La primera regla para comunicar decisiones de arquitectura es no incluir la decisión de arquitectura en el cuerpo de un correo electrónico.

Un mejor enfoque es mencionar solo la naturaleza y el contexto de la decisión en el cuerpo del correo electrónico y proporcionar un enlace al sistema de registro único para la decisión de arquitectura real y los detalles correspondientes (ya sea un enlace a una página wiki o un documento en un sistema de archivos).

La segunda regla para comunicar de manera efectiva las decisiones de arquitectura es notificar solo a aquellas personas que realmente se preocupan por la decisión de arquitectura.

Antipatrones - Email-Driven Architecture Anti-Pattern

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Title The title of an ADR is usually numbered sequentially and contains a short phrase describing the architecture decisions. For example, the decision to use asynchronous messaging between the Order Service and the Payment Service might read: “42. Use of Asynchronous Messaging Between Order and Payment Services.” The title should be descriptive enough to remove any ambiguity about the nature and context of the decision but at the same time be short and concise. Status The status of an ADR can be marked as  Proposed ,  Accepted , or  Superseded .  Proposed  status means the decision must be approved by either a higher-level decision maker or some sort of architectural governance body (such as an architecture review board).  Accepted  status means the decision has been approved and is ready for implementation. A status of  Superseded  means the decision has been changed and superseded by another ADR. Superseded status always assumes the prior ADR status was accepted; in other words, a proposed ADR would never be superseded by another ADR, but rather continued to be modified until accepted. 15

---

## Lámina 12

REGISTROS DE DECISIONES DE ARQUITECTURA (Architecture

Decision Records)

> **Notas del orador:** Status The status of an ADR can be marked as  Proposed ,  Accepted , or  Superseded .  Proposed  status means the decision must be approved by either a higher-level decision maker or some sort of architectural governance body (such as an architecture review board).  Accepted  status means the decision has been approved and is ready for implementation. A status of  Superseded  means the decision has been changed and superseded by another ADR. Superseded status always assumes the prior ADR status was accepted; in other words, a proposed ADR would never be superseded by another ADR, but rather continued to be modified until accepted. 16

---

## Lámina 13

Técnicas de Arquitectura - Decisiones

Una de las formas más efectivas de documentar las decisiones de arquitectura es a través de los registros de decisiones de arquitectura (ADR). Los ADR fueron evangelizados por primera vez por Michael Nygard en una publicación de blog de 2011. Un ADR consiste en un archivo de texto corto (generalmente de una a dos páginas) que describe una decisión de arquitectura específica.

Si bien los ADR se pueden escribir con texto sin formato, generalmente se escriben en algún tipo de formato de documento de texto como AsciiDoc o Markdown. Alternativamente, un ADR también se puede escribir utilizando una plantilla de página wiki.

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** The Superseded status is a powerful way of keeping a historical record of what decisions were made, why they were made at that time, and what the new decision is and why it was changed. Usually, when an ADR has been superseded, it is marked with the decision that superseded it. Similarly, the decision that supersedes another ADR is marked with the ADR it superseded. For example, assume ADR 42 (“Use of Asynchronous Messaging Between Order and Payment Services”) was previously approved, but due to later changes to the implementation and location of the Payment Service, REST must now be used between the two services (ADR 68). The status would look as follows: 17

---

## Lámina 14

Técnicas de Arquitectura - Decisiones

La estructura básica de un ADR consta de cinco secciones principales: Título, Estado, Contexto, Decisión y Consecuencias. Por lo general, agregamos dos secciones adicionales como parte de la estructura básica: Cumplimiento y Notas.

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Another significant aspect of the Status section of an ADR is that it forces an architect to have necessary conversations with their boss or lead architect about the criteria with which they can approve an architecture decision on their own, or whether it must be approved through a higher-level architect, an architecture review board, or some other architecture governing body. 18

---

## Lámina 15

Técnicas de Arquitectura - Decisiones

Título

El título de una ADR suele estar numerado secuencialmente y contiene una frase corta que describe las decisiones de arquitectura. Por ejemplo, la decisión de usar mensajería asincrónica entre el Servicio de pedidos y el Servicio de pago podría decir: “42. Uso de mensajería asíncrona entre los servicios de pedido y pago”. El título debe ser lo suficientemente descriptivo para eliminar cualquier ambigüedad sobre la naturaleza y el contexto de la decisión, pero al mismo tiempo debe ser breve y conciso.

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Context The context section of an ADR specifies the forces at play. In other words, “what situation is forcing me to make this decision?” This section of the ADR allows the architect to describe the specific situation or issue and concisely elaborate on the possible alternatives. If an architect is required to document the analysis of each alternative in detail, then an additional Alternatives section can be added to the ADR rather than adding that analysis to the Context section.   The Context section also provides a way to document the architecture. By describing the context, the architect is also describing the architecture. This is an effective way of documenting a specific area of the architecture in a clear and concise manner. Continuing with the example from the prior section, the context might read as follows: “The order service must pass information to the payment service to pay for an order currently being placed. This could be done using REST or asynchronous messaging.” Notice that this concise statement not only specified the scenario, but also the alternatives. 19

---

## Lámina 16

Técnicas de Arquitectura - Decisiones

Estado:

El estado de una ADR se puede marcar como Propuesto, Aceptado o Reemplazado. El estado propuesto significa que la decisión debe ser aprobada por un tomador de decisiones de alto nivel o algún tipo de organismo de gobierno arquitectónico (como una junta de revisión de arquitectura). El estado aceptado significa que la decisión ha sido aprobada y está lista para su implementación. Un estado de reemplazado significa que la decisión ha sido modificada y reemplazada por otra ADR. El estado reemplazado siempre asume que se aceptó el estado ADR anterior.

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Decision The Decision section of the ADR contains the architecture decision, along with a full justification for the decision. Michael Nygard introduced a great way of stating an architecture decision by using a very affirmative, commanding voice rather than a passive one. For example, the decision to use asynchronous messaging between services would read “we will use asynchronous messaging between services.” This is a much better way of stating a decision as opposed to “I think asynchronous messaging between services would be the best choice.” Notice here it is not clear what the decision is or even if a decision has even been made—only the opinion of the architect is stated.   Perhaps one of the most powerful aspects of the Decision section of ADRs is that it allows an architect to place more emphasis on the why rather than the how. Understanding why a decision was made is far more important than understanding how something works. Most architects and developers can identify how things work by looking at context diagrams, but not why a decision was made. Knowing why a decision was made and the corresponding justification for the decision helps people better understand the context of the problem and avoids possible mistakes through refactoring to another solution that might produce issues.   To illustrate this point, consider an original architecture decision several years ago to use Google’s Remote Procedure Call ( gRPC ) as a means to communicate between two services. Without understanding why that decision was made, another architect several years later makes the choice to override that decision and use messaging instead to better decouple the services. However, implementing this refactoring suddenly causes a significant increase in latency, which in turn ultimately causes time outs to occur in upstream systems. Understanding that the original use of  gRPC  was to significantly reduce latency (at the cost of tightly coupled services) would have prevented the refactoring from happening in the first place. 20

---

## Lámina 17

Técnicas de Arquitectura - Decisiones

Estado:

El estado Reemplazado es una forma poderosa de mantener un registro histórico de qué decisiones se tomaron, por qué se tomaron en ese momento, cuál es la nueva decisión y por qué se cambió. Por lo general, cuando se reemplaza una ADR, se marca con la decisión que la reemplazó. De manera similar, la decisión que reemplaza a otra ADR se marca con la ADR que reemplazó. Por ejemplo:

ADR 42. Use of Asynchronous Messaging Between Order and Payment Services

Status: Superseded by 68

ADR 68. Use of REST Between Order and Payment Services

Status: Accepted, supersedes 42

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Decision The Decision section of the ADR contains the architecture decision, along with a full justification for the decision. Michael Nygard introduced a great way of stating an architecture decision by using a very affirmative, commanding voice rather than a passive one. For example, the decision to use asynchronous messaging between services would read “we will use asynchronous messaging between services.” This is a much better way of stating a decision as opposed to “I think asynchronous messaging between services would be the best choice.” Notice here it is not clear what the decision is or even if a decision has even been made—only the opinion of the architect is stated.   Perhaps one of the most powerful aspects of the Decision section of ADRs is that it allows an architect to place more emphasis on the why rather than the how. Understanding why a decision was made is far more important than understanding how something works. Most architects and developers can identify how things work by looking at context diagrams, but not why a decision was made. Knowing why a decision was made and the corresponding justification for the decision helps people better understand the context of the problem and avoids possible mistakes through refactoring to another solution that might produce issues.   To illustrate this point, consider an original architecture decision several years ago to use Google’s Remote Procedure Call ( gRPC ) as a means to communicate between two services. Without understanding why that decision was made, another architect several years later makes the choice to override that decision and use messaging instead to better decouple the services. However, implementing this refactoring suddenly causes a significant increase in latency, which in turn ultimately causes time outs to occur in upstream systems. Understanding that the original use of  gRPC  was to significantly reduce latency (at the cost of tightly coupled services) would have prevented the refactoring from happening in the first place. 21

---

## Lámina 18

Técnicas de Arquitectura - Decisiones

Estado:

Otro aspecto importante de la sección Estado de un ADR es que obliga a un arquitecto a tener las conversaciones necesarias con su jefe o arquitecto principal sobre los criterios con los que puede aprobar una decisión de arquitectura por su cuenta, o si debe ser aprobada a través de una autoridad superior: arquitecto de alto nivel, una junta de revisión de arquitectura o algún otro organismo rector de la arquitectura.

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Consequences The Consequences section of an ADR is another very powerful section. This section documents the overall impact of an architecture decision. Every architecture decision an architect makes has some sort of impact, both good and bad. Having to specify the impact of an architecture decision forces the architect to think about whether those impacts outweigh the benefits of the decision.   Another good use of this section is to document the trade-off analysis associated with the architecture decision. These trade-offs could be cost-based or trade-offs against other architecture characteristics (“- ilities ”). For example, consider the decision to use asynchronous (fire-and-forget) messaging to post a review on a website. The justification for this decision is to significantly increase the responsiveness of the post review request from 3,100 milliseconds to 25 milliseconds because users would not need to wait for the actual review to be posted (only for the message to be sent to a queue). While this is a good justification, someone else might argue that this is a bad idea due to the complexity of the error handling associated with an asynchronous request (“what happens if someone posts a review with some bad words?”). Unknown to the person challenging this decision, that issue was already discussed with the business stakeholders and other architects, and it was decided from a trade-off perspective that it was more important to have the increase in responsiveness and deal with the complex error handling rather than have the wait time to synchronously provide feedback to the user that the review was successfully posted. By leveraging ADRs, that trade-off analysis can be included in the Consequences section, providing a complete picture of the context (and trade-offs) of the architecture decision and thus avoiding these situations. 22

---

## Lámina 19

Técnicas de Arquitectura - Decisiones

Contexto:

El Contexto de un ADR especifica las fuerzas en juego. En otras palabras, “¿qué situación me está obligando a tomar esta decisión?” Esta sección le permite al arquitecto describir la situación o problema específico y explicar de manera concisa las posibles alternativas. Si se requiere que un arquitecto documente el análisis de cada alternativa en detalle, entonces se puede agregar una sección de Alternativas adicional al ADR en lugar de agregar ese análisis a la sección de Contexto.

También proporciona una forma de documentar la arquitectura. Al describir el contexto, el arquitecto también está describiendo la arquitectura. Esta es una forma efectiva de documentar un área específica de la arquitectura de manera clara y concisa.

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Compliance The compliance section of an ADR is not one of the standard sections in an ADR, but it’s one we highly recommend adding. The Compliance section forces the architect to think about how the architecture decision will be measured and governed from a compliance perspective. The architect must decide whether the compliance check for this decision must be manual or if it can be automated using a fitness function. If it can be automated using a fitness function, the architect can then specify in this section how that fitness function would be written and whether there are any other changes to the code base are needed to measure this architecture decision for compliance. 23

---

## Lámina 20

Técnicas de Arquitectura - Decisiones

Decisión:

La sección Decisión del ADR contiene la decisión de la arquitectura, junto con una justificación completa de la decisión. Michael Nygard presentó una excelente manera de expresar una decisión de arquitectura mediante el uso de una voz de mando afirmativa en lugar de una voz pasiva. Por ejemplo, la decisión de usar mensajería asíncrona entre servicios sería "usaremos mensajería asíncrona entre servicios". Esta es una forma mucho mejor de tomar una decisión en lugar de "Creo que la mensajería asincrónica entre servicios sería la mejor opción". Observe que aquí no está claro cuál es la decisión o incluso si se ha tomado una decisión; solo se expresa la opinión del arquitecto.

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Compliance The compliance section of an ADR is not one of the standard sections in an ADR, but it’s one we highly recommend adding. The Compliance section forces the architect to think about how the architecture decision will be measured and governed from a compliance perspective. The architect must decide whether the compliance check for this decision must be manual or if it can be automated using a fitness function. If it can be automated using a fitness function, the architect can then specify in this section how that fitness function would be written and whether there are any other changes to the code base are needed to measure this architecture decision for compliance. 24

---

## Lámina 21

Técnicas de Arquitectura - Decisiones

Decisión:

Quizás uno de los aspectos más poderosos de la sección de Decisión de ADR es que le permite a un arquitecto poner más énfasis en el por qué que en el cómo. Comprender por qué se tomó una decisión es mucho más importante que comprender cómo funciona algo. La mayoría de los arquitectos y desarrolladores pueden identificar cómo funcionan las cosas mirando los diagramas de contexto, pero no por qué se tomó una decisión. Saber por qué se tomó una decisión y la correspondiente justificación de la decisión ayuda a las personas a comprender mejor el contexto del problema y evita posibles errores mediante la refactorización a otra solución que podría generar problemas.

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Another section that is not part of a standard ADR but that we highly recommend adding is the Notes section. This section includes various metadata about the ADR, such as the following: Original author Approval date Approved by Superseded date Last modified date Modified by Last modification 25

---

## Lámina 22

Técnicas de Arquitectura - Decisiones

Consecuencias:

La sección de Consecuencias de un ADR documenta el impacto general de una decisión de arquitectura. Cada decisión de arquitectura que toma un arquitecto tiene algún tipo de impacto, tanto bueno como malo. Tener que especificar el impacto de una decisión de arquitectura obliga al arquitecto a pensar si esos impactos superan los beneficios de la decisión. Otro buen uso de esta sección es documentar el análisis de tradeoffs asociado con la decisión de arquitectura. Estas compensaciones podrían basarse en los costos o compensaciones con respecto a otras características de la arquitectura ("-ilidades").

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Storing ADRs Once an architect creates an ADR, it must be stored somewhere. Regardless of where ADRs are stored, each architecture decision should have its own file or wiki page. Some architects like to keep ADRs in the Git repository with the source code. Keeping ADRs in a Git repository allows the ADR to be versioned and tracked as well. However, for larger organizations we caution against this practice for several reasons. First, everyone who needs to see the architecture decision may not have access to the Git repository. Second, this is not a good place to store ADRs that have a context outside of the application Git repository (such as integration architecture decisions, enterprise architecture decisions, or those decisions common to every application). For these reasons we recommend storing ADRs either in a wiki (using a wiki template) or in a shared directory on a shared file server that can be accessed easily by a wiki or other document rendering software 26

---

## Lámina 23

Técnicas de Arquitectura - Decisiones

Cumplimiento:

La sección de Cumplimiento de un ADR no es una de las secciones estándar en un ADR, pero es una que recomendamos agregar. La sección de Cumplimiento obliga al arquitecto a pensar en cómo se medirá y regirá la decisión de la arquitectura desde una perspectiva de cumplimiento. El arquitecto debe decidir si la verificación del cumplimiento de esta decisión debe ser manual o si puede automatizarse mediante una fitness function. Si se puede automatizar usando una función, el arquitecto puede especificar en esta sección cómo se escribiría esa función y si se necesitan otros cambios en el código base para medir el cumplimiento de esta decisión de arquitectura.

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Storing ADRs Once an architect creates an ADR, it must be stored somewhere. Regardless of where ADRs are stored, each architecture decision should have its own file or wiki page. Some architects like to keep ADRs in the Git repository with the source code. Keeping ADRs in a Git repository allows the ADR to be versioned and tracked as well. However, for larger organizations we caution against this practice for several reasons. First, everyone who needs to see the architecture decision may not have access to the Git repository. Second, this is not a good place to store ADRs that have a context outside of the application Git repository (such as integration architecture decisions, enterprise architecture decisions, or those decisions common to every application). For these reasons we recommend storing ADRs either in a wiki (using a wiki template) or in a shared directory on a shared file server that can be accessed easily by a wiki or other document rendering software 27

---

## Lámina 24

Técnicas de Arquitectura - Decisiones

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

Por ejemplo, considere la siguiente decisión de arquitectura dentro de una arquitectura tradicional en capas de n niveles. Todos los objetos compartidos utilizados por los objetos de negocio de la capa de negocio residirán en la capa de servicios compartidos para aislar y contener la funcionalidad compartida.

> **Notas del orador:** Architecture Decision Records can be used an  an  effective means to document a software architecture. The Context section of an ADR provides an excellent opportunity to describe the specific area of the system that requires an architecture decision to be made. This section also provides an opportunity to describe the alternatives. Perhaps more important is that the Decision section describes the reasons why a particular decision is made, which is by far the best form of architecture documentation. The Consequences section adds the final piece to the architecture documentation by describing additional aspects of a particular decision, such as the trade-off analysis of choosing performance over scalability. 28

---

## Lámina 25

Técnicas de Arquitectura - Decisiones

Notas:

Otra sección que no forma parte de un ADR estándar pero que recomendamos agregar es la sección Notas. Esta sección incluye varios metadatos sobre la ADR:

Autor original

Fecha de aprobación

Aprobado por

Fecha reemplazada

Última fecha de modificación

Modificado por

Ultima modificación

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Fuente:  https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html 29

---

## Lámina 26

Técnicas de Arquitectura - Decisiones

Almacenamiento:

Una vez que un arquitecto crea un ADR, debe almacenarse en algún lugar. Independientemente de dónde se almacenen los ADR, cada decisión de arquitectura debe tener su propio archivo o página wiki. A algunos arquitectos les gusta mantener los ADR en el repositorio de Git con el código fuente. Mantener las ADR en un repositorio de Git también permite versionar y rastrear la ADR. Adicionalmente se recomienda almacenar las ADR en un wiki (usando una plantilla de wiki) o en un directorio compartido en un servidor de archivos al que se pueda acceder fácilmente mediante un wiki u otro software de gestión de documentos.

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Fuente:  https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html 30

---

## Lámina 27

Técnicas de Arquitectura - Decisiones

Almacenamiento:

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Fuente:  https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html 31

---

## Lámina 28

Técnicas de Arquitectura - Decisiones

ADR como Documentación:

Los Registros de Decisiones de Arquitectura se pueden utilizar como un medio eficaz para documentar una arquitectura de software. La sección Contexto de un ADR brinda una excelente oportunidad para describir el área específica del sistema que requiere que se tome una decisión de arquitectura. Esta sección también brinda la oportunidad de describir las alternativas. Quizás lo más importante es que la sección Decisión describe las razones por las que se toma una decisión en particular, que es, con mucho, la mejor forma de documentación de arquitectura. La sección Consecuencias agrega la pieza final a la documentación de la arquitectura al describir aspectos adicionales de una decisión en particular, como el análisis de tradeoffs de elegir rendimiento sobre escalabilidad.

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Fuente:  https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html 32

---

## Lámina 29

Técnicas de Arquitectura - Decisiones

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

Proceso de Adopción de ADR por AWS:

> **Notas del orador:** Fuente:  https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html 33

---

## Lámina 30

Técnicas de Arquitectura - Decisiones

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

Ejemplo – Caso de Estudio: Going, Going, Go

Description

An auction company wants to take its auctions online to a nationwide scale. Customers choose the auction to participate in, wait until the auction begins, then bid as if they are there in the room with the auctioneer.

Users

Scale up to hundreds of participants per auction, potentially up to thousands of participants, and as many simultaneous auctions as possible.

> **Notas del orador:** Fuente:  https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html 34

---

## Lámina 31

Técnicas de Arquitectura - Decisiones

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

Ejemplo – Caso de Estudio: Going, Going, Go

Requirements

Auctions must be as real-time as possible.

Bidders register with a credit card; the system automatically charges the card if the bidder wins.

Participants must be tracked via a reputation index.

Bidders can see a live video stream of the auction and all bids as they occur.

Both online and live bids must be received in the order in which they are placed.

> **Notas del orador:** Fuente:  https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html 35

---

## Lámina 32

Técnicas de Arquitectura - Decisiones

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

Ejemplo – Caso de Estudio: Going, Going, Go

Additional context

Auction company is expanding aggressively by merging with smaller competitors.

Budget is not constrained. This is a strategic direction.

Company just exited a lawsuit where it settled a suit alleging fraud.

> **Notas del orador:** Fuente:  https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html 36

---

## Lámina 33

Técnicas de Arquitectura - Decisiones

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

Ejemplo – Caso de Estudio: Going, Going, Go

El uso de microservicios basados en eventos, la división de las interfaces de usuario del postor y el subastador, el uso del Protocolo de transporte en tiempo real (RTP) para la captura de video, el uso de una sola capa API y el uso de publicación y -los mensajes de suscripción son solo algunas de las docenas de decisiones de arquitectura que se tomaron para este sistema de subastas. Toda decisión de arquitectura que se tome en un sistema, por obvia que sea, debe documentarse y justificarse.

> **Notas del orador:** Fuente:  https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html 37

---

## Lámina 34

Técnicas de Arquitectura - Decisiones

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

Ejemplo – Caso de Estudio: Going, Going, Go

Gone auction system, which is the use of publish-and-subscribe (pub/sub) messaging between the bid capture, bid streamer, and bid tracker services.

---

## Lámina 35

Técnicas de Arquitectura - Decisiones

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

Ejemplo – Caso de Estudio: Going, Going, Go

---

## Lámina 36

Técnicas de Arquitectura - Decisiones

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

Ejemplo – Caso de Estudio: Going, Going, Go

---

## Lámina 37

Técnicas de Arquitectura - Decisiones

Registros de Decisiones de Arquitectura (ADR)

Maestría en Ingeniería de Software – Arquitectura de Software

Ejemplo – Caso de Estudio: Going, Going, Go

---

## Lámina 38

Documenting architecture decisions by Michael Nygard

AWS – ADR Process

ADR Tools

My Agile Architecture Workflow Using ADRs

Lecturas

---

## Lámina 39

Mark Richards, Neal  Ford. Fundamentals of Software Architecture: An Engineering Approach. O'Reilly, 2020.

Bibliografía

---

## Lámina 40

_(sin texto: la lámina es una imagen)_
