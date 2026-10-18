# Técnicas de Análisis de Riesgos — deck oficial del Módulo 3

> **Tipo:** `material-oficial` (Recursos complementarios → «Presentaciones Adicionales», Brightspace, Unidad 4 de 5).
> **Fuente:** `TecnicasAnalisisRiesgos.pptx` (29 láminas), descargado el 2026-10-18 con sesión de Danny.
> **Extraído:** 2026-10-18, texto de las láminas tal cual. Las **notas del orador** se incluyen aparte
>  porque traen contenido (a menudo en inglés, del libro de referencia); las que solo tienen un número se omiten.
> **Límite de la extracción:** solo texto. Diagramas, figuras y tablas dibujadas como imagen NO están.
> **Este archivo no se edita.** Las notas y críticas van en `Aportes/`.

---

## Lámina 1

DIPLOMADO EN

ARQUITECTURA DE SOFTWARE

TÉCNICAS: ANÁLISIS DE RIESGOS

> **Notas del orador:** Every architecture has risk associated with it, whether it be risk involving availability, scalability, or data integrity. Analyzing architecture risk is one of the key activities of architecture. By continually analyzing risk, the architect can address deficiencies within the architecture and take corrective action to mitigate the risk. In this chapter we introduce some of the key techniques and practices for qualifying risk, creating risk assessments, and identifying risk through an activity called  risk storming .   4

---

## Lámina 2

ANÁLISIS DE RIESGOS

> **Notas del orador:** Risk Matrix The first issue that arises when assessing architecture risk is determining whether the risk should be classified as low, medium, or high. Too much subjectiveness usually enters into this classification, creating confusion about which parts of the architecture are really high risk versus medium risk. Fortunately, there is a risk matrix architects can leverage to help reduce the level of subjectiveness and qualify the risk associated with a particular area of the architecture. The architecture risk matrix (illustrated in  Figure 20-1 ) uses two dimensions to qualify risk: the overall impact of the risk and the likelihood of that risk occurring. Each dimensions has a low (1), medium (2), and high (3) rating. These numbers are multiplied together within each grid of the matrix, providing an objective numerical number representing that risk. Numbers 1 and 2 are considered low risk (green), numbers 3 and 4 are considered medium risk (yellow), and numbers 6 through 9 are considered high risk (red).   6

---

## Lámina 3

Técnicas de Arquitectura - Análisis de Riesgos

Cada arquitectura tiene un riesgo asociado, ya sea un riesgo relacionado con la disponibilidad, la escalabilidad o la integridad de los datos. Analizar el riesgo de la arquitectura es una de las actividades clave de la arquitectura. Al analizar continuamente el riesgo, el arquitecto puede abordar las deficiencias dentro de la arquitectura y tomar medidas correctivas para mitigar el riesgo.

Introducción

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Risk Matrix The first issue that arises when assessing architecture risk is determining whether the risk should be classified as low, medium, or high. Too much subjectiveness usually enters into this classification, creating confusion about which parts of the architecture are really high risk versus medium risk. Fortunately, there is a risk matrix architects can leverage to help reduce the level of subjectiveness and qualify the risk associated with a particular area of the architecture. The architecture risk matrix (illustrated in  Figure 20-1 ) uses two dimensions to qualify risk: the overall impact of the risk and the likelihood of that risk occurring. Each dimensions has a low (1), medium (2), and high (3) rating. These numbers are multiplied together within each grid of the matrix, providing an objective numerical number representing that risk. Numbers 1 and 2 are considered low risk (green), numbers 3 and 4 are considered medium risk (yellow), and numbers 6 through 9 are considered high risk (red).   7

---

## Lámina 4

MATRIZ DE RIESGOS

> **Notas del orador:** To see how the risk matrix can be used, suppose there is a concern about availability with regard to a primary central database used in the application. First, consider the impact dimension—what is the overall impact if the database goes down or becomes unavailable? Here, an architect might deem that high risk, making that risk either a 3 (medium), 6 (high), or 9 (high). However, after applying the second dimension (likelihood of risk occurring), the architect realizes that the database is on highly available servers in a clustered configuration, so the likelihood is low that the database would become unavailable. Therefore, the intersection between the high impact and low likelihood gives an overall risk rating of 3 (medium risk).   8

---

## Lámina 5

Técnicas de Arquitectura - Análisis de Riesgos

El primer problema que surge al evaluar el riesgo de la arquitectura es determinar si el riesgo debe clasificarse como bajo, medio o alto. Por lo general, entra demasiada subjetividad en esta clasificación, lo que genera confusión sobre qué partes de la arquitectura son realmente de riesgo alto y cuáles son de riesgo medio. Afortunadamente, existe una matriz de riesgo que los arquitectos pueden aprovechar para ayudar a reducir el nivel de subjetividad y calificar el riesgo asociado con un área particular de la arquitectura.

Matriz de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Risk Assessments The risk matrix described in the previous section can be used to build what is called a  risk assessment . A risk assessment is a summarized report of the overall risk of an architecture with respect to some sort of contextual and meaningful assessment criteria. Risk assessments can vary greatly, but in general they contain the risk (qualified from the risk matrix) of some  assessment criteria  based on services or domain areas of an application.  10

---

## Lámina 6

Técnicas de Arquitectura - Análisis de Riesgos

La matriz de riesgo de la arquitectura utiliza dos dimensiones para calificar el riesgo: el impacto general del riesgo y la probabilidad de que ese riesgo ocurra. Cada dimensión tiene una calificación baja (1), media (2) y alta (3). Estos números se multiplican dentro de cada cuadrícula de la matriz, proporcionando un número objetivo que representa ese riesgo. Los números 1 y 2 se consideran de bajo riesgo (verde), los números 3 y 4 se consideran de riesgo medio (amarillo) y los números 6 a 9 se consideran de alto riesgo (rojo).

Matriz de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

> **Notas del orador:** Risk Assessments The risk matrix described in the previous section can be used to build what is called a  risk assessment . A risk assessment is a summarized report of the overall risk of an architecture with respect to some sort of contextual and meaningful assessment criteria. Risk assessments can vary greatly, but in general they contain the risk (qualified from the risk matrix) of some  assessment criteria  based on services or domain areas of an application.  11

---

## Lámina 7

Técnicas de Arquitectura - Análisis de Riesgos

Matriz de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

Para ver cómo se puede utilizar la matriz de riesgos, suponga que existe una preocupación acerca de la disponibilidad con respecto a una base de datos central primaria utilizada en la aplicación. Primero, considere la dimensión del impacto: ¿cuál es el impacto general si la base de datos deja de funcionar o deja de estar disponible? Aquí, un arquitecto podría considerar ese riesgo alto, haciendo que ese riesgo sea un 3 (medio), 6 (alto) o 9 (alto). Sin embargo, después de aplicar la segunda dimensión (probabilidad de que ocurra el riesgo), el arquitecto se da cuenta de que la base de datos se encuentra en servidores de alta disponibilidad en una configuración en clúster, por lo que la probabilidad de que la base de datos deje de estar disponible es baja. Por lo tanto, la intersección entre el alto impacto y la baja probabilidad da una calificación de riesgo general de 3 (riesgo medio).

> **Notas del orador:** The quantified risk from the risk matrix can be accumulated by the risk criteria and also by the service or domain area. For example, notice in Figure 20-2 that the accumulated risk for data integrity is the highest risk area at a total of 17, whereas the accumulated risk for Availability is only 10 (the least amount of risk). The relative risk of each domain area can also be determined by the example risk assessment. Here, customer registration carries the highest area of risk, whereas order fulfillment carries the lowest risk. These relative numbers can then be tracked to demonstrate either improvements or degradation of risk within a particular risk category or domain area.   Although the risk assessment example in Figure 20-2 contains all the risk analysis results, rarely is it presented as such. Filtering is essential for visually indicating a particular message within a given context. For example, suppose an architect is in a meeting for the purpose of presenting areas of the system that are high risk. Rather than presenting the risk assessment as illustrated in Figure 20-2, filtering can be used to only show the high risk areas (shown in Figure 20-3), improving the overall signal-to-noise ratio and presenting a clear picture of the state of the system (good or bad). 12

---

## Lámina 8

EVALUACIÓN DE RIESGOS

> **Notas del orador:** The quantified risk from the risk matrix can be accumulated by the risk criteria and also by the service or domain area. For example, notice in Figure 20-2 that the accumulated risk for data integrity is the highest risk area at a total of 17, whereas the accumulated risk for Availability is only 10 (the least amount of risk). The relative risk of each domain area can also be determined by the example risk assessment. Here, customer registration carries the highest area of risk, whereas order fulfillment carries the lowest risk. These relative numbers can then be tracked to demonstrate either improvements or degradation of risk within a particular risk category or domain area.   Although the risk assessment example in Figure 20-2 contains all the risk analysis results, rarely is it presented as such. Filtering is essential for visually indicating a particular message within a given context. For example, suppose an architect is in a meeting for the purpose of presenting areas of the system that are high risk. Rather than presenting the risk assessment as illustrated in Figure 20-2, filtering can be used to only show the high risk areas (shown in Figure 20-3), improving the overall signal-to-noise ratio and presenting a clear picture of the state of the system (good or bad). 13

---

## Lámina 9

Técnicas de Arquitectura - Análisis de Riesgos

Evaluaciones de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

La Matriz de Riesgos descrita previamente se puede utilizar para construir lo que se denomina la Evaluación de riesgos. Una evaluación de riesgos es un informe resumido del riesgo general de una arquitectura con respecto a algún tipo de criterio de evaluación contextual y significativo. Las evaluaciones de riesgos pueden variar mucho, pero en general contienen el riesgo (calificado de la matriz de riesgos) de algunos criterios de evaluación basados en servicios o áreas de dominio de una aplicación.

---

## Lámina 10

Técnicas de Arquitectura - Análisis de Riesgos

Evaluaciones de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

Convenciones: El gris claro (1-2) es de bajo riesgo, el gris medio (3-4) es de riesgo medio y el gris oscuro (6-9) es de alto riesgo. Por lo general, estos están codificados por colores como verde (bajo), amarillo (medio) y rojo (alto), pero el sombreado puede ser útil para la representación en blanco y negro y para el daltonismo.

---

## Lámina 11

Técnicas de Arquitectura - Análisis de Riesgos

Evaluaciones de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

El riesgo cuantificado de la matriz de riesgo puede ser acumulado por los criterios de riesgo y también por el área de servicio o dominio. Por ejemplo, en la figura anterior el riesgo acumulado para la integridad de los datos es el área de mayor riesgo con un total de 17, mientras que el riesgo acumulado para la disponibilidad es solo 10 (la menor cantidad de riesgo). El riesgo relativo de cada área de dominio también se puede determinar mediante la evaluación de riesgos del ejemplo. Aquí, el registro de clientes conlleva el área de riesgo más alta, mientras que el cumplimiento de pedidos conlleva el riesgo más bajo. Luego, estos números relativos pueden rastrearse para demostrar mejoras o degradación del riesgo dentro de una categoría de riesgo o área de dominio en particular.

---

## Lámina 12

Técnicas de Arquitectura - Análisis de Riesgos

Evaluaciones de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

Aunque el ejemplo anterior de evaluación de riesgos contiene todos los resultados del análisis de riesgos, rara vez se presenta como tal. El filtrado es esencial para indicar visualmente un mensaje particular dentro de un contexto dado. Por ejemplo, suponga que un arquitecto está en una reunión con el fin de presentar áreas del sistema que son de alto riesgo. En lugar de presentar la evaluación de riesgos completa, el filtrado se puede usar para mostrar solo las áreas de alto riesgo, mejorando la relación señal-ruido general y presentando una imagen clara del estado del sistema (bueno o malo).

> **Notas del orador:** No architect can single-handedly determine the overall risk of a system. The reason for this is two-fold. First, a single architect might miss or overlook a risk area, and very few architects have full knowledge of every part of the system. This is where  risk storming  can help. Risk storming is a collaborative exercise used to determine architectural risk within a specific dimension. Common dimensions (areas of risk) include unproven technology, performance, scalability, availability (including transitive dependencies), data loss, single points of failure, and security. While most risk storming efforts involve multiple architects, it is wise to include senior developers and tech leads as well. Not only will they provide an implementation perspective to the architectural risk, but involving developers helps them gain a better understanding of the architecture. The risk storming effort involves both an individual part and a collaborative part. In the individual part, all participants individually (without collaboration) assign risk to areas of the architecture using the risk matrix described in the previous section. This noncollaborative part of risk storming is essential so that participants don’t influence or direct attention away from particular areas of the architecture. In the collaborative part of risk storming, all participants work together to gain consensus on risk areas, discuss risk, and form solutions for mitigating the risk. An architecture diagram is used for both parts of the risk storming effort. For holistic risk assessments, usually a comprehensive architecture diagram is used, whereas risk storming within specific areas of the application would use a contextual architecture diagram. It is the responsibility of the architect conducting the risk storming effort to make sure these diagrams are up to date and available to all participants. 18

---

## Lámina 13

Técnicas de Arquitectura - Análisis de Riesgos

Evaluaciones de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

Filtrar la evaluación de riesgos

> **Notas del orador:** No architect can single-handedly determine the overall risk of a system. The reason for this is two-fold. First, a single architect might miss or overlook a risk area, and very few architects have full knowledge of every part of the system. This is where  risk storming  can help. Risk storming is a collaborative exercise used to determine architectural risk within a specific dimension. Common dimensions (areas of risk) include unproven technology, performance, scalability, availability (including transitive dependencies), data loss, single points of failure, and security. While most risk storming efforts involve multiple architects, it is wise to include senior developers and tech leads as well. Not only will they provide an implementation perspective to the architectural risk, but involving developers helps them gain a better understanding of the architecture. The risk storming effort involves both an individual part and a collaborative part. In the individual part, all participants individually (without collaboration) assign risk to areas of the architecture using the risk matrix described in the previous section. This noncollaborative part of risk storming is essential so that participants don’t influence or direct attention away from particular areas of the architecture. In the collaborative part of risk storming, all participants work together to gain consensus on risk areas, discuss risk, and form solutions for mitigating the risk. An architecture diagram is used for both parts of the risk storming effort. For holistic risk assessments, usually a comprehensive architecture diagram is used, whereas risk storming within specific areas of the application would use a contextual architecture diagram. It is the responsibility of the architect conducting the risk storming effort to make sure these diagrams are up to date and available to all participants. 19

---

## Lámina 14

Técnicas de Arquitectura - Análisis de Riesgos

Evaluaciones de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

Mostrando la dirección del riesgo con signos más y menos

> **Notas del orador:** No architect can single-handedly determine the overall risk of a system. The reason for this is two-fold. First, a single architect might miss or overlook a risk area, and very few architects have full knowledge of every part of the system. This is where  risk storming  can help. Risk storming is a collaborative exercise used to determine architectural risk within a specific dimension. Common dimensions (areas of risk) include unproven technology, performance, scalability, availability (including transitive dependencies), data loss, single points of failure, and security. While most risk storming efforts involve multiple architects, it is wise to include senior developers and tech leads as well. Not only will they provide an implementation perspective to the architectural risk, but involving developers helps them gain a better understanding of the architecture. The risk storming effort involves both an individual part and a collaborative part. In the individual part, all participants individually (without collaboration) assign risk to areas of the architecture using the risk matrix described in the previous section. This noncollaborative part of risk storming is essential so that participants don’t influence or direct attention away from particular areas of the architecture. In the collaborative part of risk storming, all participants work together to gain consensus on risk areas, discuss risk, and form solutions for mitigating the risk. An architecture diagram is used for both parts of the risk storming effort. For holistic risk assessments, usually a comprehensive architecture diagram is used, whereas risk storming within specific areas of the application would use a contextual architecture diagram. It is the responsibility of the architect conducting the risk storming effort to make sure these diagrams are up to date and available to all participants. 20

---

## Lámina 15

Técnicas de Arquitectura - Análisis de Riesgos

Evaluaciones de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

Mostrando la dirección del riesgo con flechas y números

> **Notas del orador:** The image shows an example architecture we’ll use to illustrate the risk storming process. In this architecture, an Elastic Load Balancer fronts each EC2 instance containing the web servers (Nginx) and application services. The application services make calls to a MySQL database, a Redis cache, and a MongoDB database for logging. They also make calls to the Push Expansion Servers. The expansion servers, in turn, all interface with the MySQL database, Redis cache, and MongoDB logging facility. 21

---

## Lámina 16

LLUVIA DE RIESGOS

> **Notas del orador:** Risk storming is broken down into three primary activities:   Identification Consensus Mitigation   Identification is always an individual, noncollaborative activity, whereas consensus and mitigation are always collaborative and involve all participants working together in the same room (at least virtually). Each of these primary activities is discussed in detail in the following sections. 22

---

## Lámina 17

Técnicas de Arquitectura - Análisis de Riesgos

Lluvia de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

Ningún arquitecto puede determinar por sí solo el riesgo general de un sistema. La razón de esto es doble. Primero, un solo arquitecto puede pasar por alto o pasar por alto un área de riesgo, y muy pocos arquitectos tienen pleno conocimiento de cada parte del sistema. Aquí es donde la lluvia de riesgos puede ayudar.

La tormenta de riesgos es un ejercicio de colaboración utilizado para determinar el riesgo arquitectónico dentro de una dimensión específica. Las dimensiones comunes (áreas de riesgo) incluyen tecnología no probada, rendimiento, escalabilidad, disponibilidad (incluidas las dependencias transitivas), pérdida de datos, puntos únicos de falla y seguridad.

> **Notas del orador:** The  identification  activity of risk storming involves each participant individually identifying areas of risk within the architecture. The following steps describe the identification part of the risk storming effort: The architect conducting the risk storming sends out an invitation to all participants one to two days prior to the collaborative part of the effort. The invitation contains the architecture diagram (or the location of where to find it), the risk storming dimension (area of risk being analyzed for that particular risk storming effort), the date when the collaborative part of risk storming will take place, and the location. Using the risk matrix described in the first section of this chapter, participants individually analyze the architecture and classify the risk as low (1-2), medium (3-4), or high (6-9). Participants prepare small Post-it notes with corresponding colors (green, yellow, and red) and write down the corresponding risk number (found on the risk matrix). 23

---

## Lámina 18

Técnicas de Arquitectura - Análisis de Riesgos

Lluvia de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

El esfuerzo de la lluvia de riesgos implica tanto una parte individual como una parte colaborativa. En la parte individual, todos los participantes individualmente (sin colaboración) asignan riesgo a las áreas de la arquitectura utilizando la matriz de riesgo descrita en la sección anterior. Esta parte no colaborativa de la tormenta de riesgos es esencial para que los participantes no influyan ni desvíen la atención de áreas particulares de la arquitectura.

En la parte colaborativa de la tormenta de riesgos, todos los participantes trabajan juntos para lograr un consenso sobre las áreas de riesgo, discutir el riesgo y formar soluciones para mitigar el riesgo.

> **Notas del orador:** The consensus activity in the risk storming effort is highly collaborative with the goal of gaining consensus among all participants regarding the risk within the architecture. This activity is most effective when a large, printed version of the architecture diagram is available and posted on the wall. In lieu of a large printed version, an electronic version can be displayed on a large screen.   Upon arrival at the risk storming session, participants begin placing their Post-it notes on the architecture diagram in the area where they individually found risk. If an electronic version is used, the architect conducting the risk storming session queries every participant and electronically places the risk on the diagram in the area of the architecture where the risk was identified 24

---

## Lámina 19

Técnicas de Arquitectura - Análisis de Riesgos

Lluvia de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

Se utiliza un diagrama de arquitectura para ambas partes del esfuerzo de la lluvia de riesgos. Para las evaluaciones de riesgos holísticas, generalmente se usa un diagrama de arquitectura integral, mientras que la lluvia de riesgos dentro de áreas específicas de la aplicación usaría un diagrama de arquitectura contextual. Es responsabilidad del arquitecto que realiza el esfuerzo de análisis de riesgos asegurarse de que estos diagramas estén actualizados y disponibles para todos los participantes.

> **Notas del orador:** The  identification  activity of risk storming involves each participant individually identifying areas of risk within the architecture. The following steps describe the identification part of the risk storming effort: The architect conducting the risk storming sends out an invitation to all participants one to two days prior to the collaborative part of the effort. The invitation contains the architecture diagram (or the location of where to find it), the risk storming dimension (area of risk being analyzed for that particular risk storming effort), the date when the collaborative part of risk storming will take place, and the location. Using the risk matrix described in the first section of this chapter, participants individually analyze the architecture and classify the risk as low (1-2), medium (3-4), or high (6-9). Participants prepare small Post-it notes with corresponding colors (green, yellow, and red) and write down the corresponding risk number (found on the risk matrix). 25

---

## Lámina 20

Técnicas de Arquitectura - Análisis de Riesgos

Lluvia de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

En el ejemplo se muestra una arquitectura con un Elastic Load Balancer en frente de cada instancia EC2 que contiene los servidores web (Nginx) y los servicios de aplicaciones. Los servicios de la aplicación realizan llamadas a una base de datos MySQL, un caché Redis y una base de datos MongoDB para los Logs. También realizan llamadas a los servidores de expansión de inserción. Los servidores de expansión, a su vez, interactúan con la base de datos MySQL, el caché de Redis y la instalación de registro de MongoDB.

> **Notas del orador:** The  identification  activity of risk storming involves each participant individually identifying areas of risk within the architecture. The following steps describe the identification part of the risk storming effort: The architect conducting the risk storming sends out an invitation to all participants one to two days prior to the collaborative part of the effort. The invitation contains the architecture diagram (or the location of where to find it), the risk storming dimension (area of risk being analyzed for that particular risk storming effort), the date when the collaborative part of risk storming will take place, and the location. Using the risk matrix described in the first section of this chapter, participants individually analyze the architecture and classify the risk as low (1-2), medium (3-4), or high (6-9). Participants prepare small Post-it notes with corresponding colors (green, yellow, and red) and write down the corresponding risk number (found on the risk matrix). 26

---

## Lámina 21

Técnicas de Arquitectura - Análisis de Riesgos

Lluvia de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

La Lluvia de riesgos se divide en tres actividades principales:

Identificación

Consenso

Mitigación

La identificación es siempre una actividad individual, no colaborativa, mientras que el consenso y la mitigación siempre son colaborativos e involucran a todos los participantes trabajando juntos en la misma sala (al menos virtualmente).

> **Notas del orador:** Mitigation Once all participants agree on the qualification of the risk areas of the architecture, the final and most important activity occurs— risk mitigation . Mitigating risk within an architecture usually involves changes or enhancements to certain areas of the architecture that otherwise might have been deemed perfect the way they were. This activity, which is also usually collaborative, seeks ways to reduce or eliminate the risk identified in the first activity. There may be cases where the original architecture needs to be completely changed based on the identification of risk, whereas others might be a straightforward architecture refactoring, such as adding a queue for back pressure to reduce a throughput bottleneck issue. Regardless of the changes required in the architecture, this activity usually incurs additional cost. For that reason, key stakeholders typically decide whether the cost outweighs the risk. For example, suppose that through a risk storming session the central database was identified as being medium risk (4) with regard to overall system availability. In this case, the participants agreed that clustering the database, combined with breaking the single database into separate physical databases, would mitigate that risk. However, while risk would be significantly reduced, this solution would cost $20,000. The architect would then conduct a meeting with the key business stakeholder to discuss this trade-off. During this negotiation, the business owner decides that the price tag is too high and that the cost does not outweigh the risk. Rather than giving up, the architect then suggests a different approach—what about skipping the clustering and splitting the database into two parts? The cost in this case is reduced to $8,000 while still mitigating most of the risk. In this case, the stakeholder agrees to the solution. The previous scenario shows the impact risk storming can have not only on the overall architecture, but also with regard to negotiations between architects and business stakeholders. Risk storming, combined with the risk assessments described at the start of this chapter, provide an excellent vehicle for identifying and tracking risk, improving the architecture, and handling negotiations between key stakeholders. 27

---

## Lámina 22

Técnicas de Arquitectura - Análisis de Riesgos

Lluvia de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

Identificación: La identificación  implica que cada participante identifique individualmente áreas de riesgo dentro de la arquitectura. Los siguientes pasos describen la actividad:

El arquitecto que realiza la lluvia de riesgos envía una invitación a todos los participantes uno o dos días antes de la parte colaborativa del esfuerzo. La invitación contiene el diagrama de la arquitectura, las dimensione, la fecha en que se llevará a cabo la parte colaborativa y la ubicación.

Usando la matriz de riesgo, los participantes analizan individualmente la arquitectura y clasifican el riesgo como bajo (1-2), medio (3-4) o alto (6-9).

Los participantes preparan pequeñas notas Post-it con los colores correspondientes (verde, amarillo y rojo) y escriben el número de riesgo correspondiente (que se encuentra en la matriz de riesgo).

> **Notas del orador:** Mitigation Once all participants agree on the qualification of the risk areas of the architecture, the final and most important activity occurs— risk mitigation . Mitigating risk within an architecture usually involves changes or enhancements to certain areas of the architecture that otherwise might have been deemed perfect the way they were. This activity, which is also usually collaborative, seeks ways to reduce or eliminate the risk identified in the first activity. There may be cases where the original architecture needs to be completely changed based on the identification of risk, whereas others might be a straightforward architecture refactoring, such as adding a queue for back pressure to reduce a throughput bottleneck issue. Regardless of the changes required in the architecture, this activity usually incurs additional cost. For that reason, key stakeholders typically decide whether the cost outweighs the risk. For example, suppose that through a risk storming session the central database was identified as being medium risk (4) with regard to overall system availability. In this case, the participants agreed that clustering the database, combined with breaking the single database into separate physical databases, would mitigate that risk. However, while risk would be significantly reduced, this solution would cost $20,000. The architect would then conduct a meeting with the key business stakeholder to discuss this trade-off. During this negotiation, the business owner decides that the price tag is too high and that the cost does not outweigh the risk. Rather than giving up, the architect then suggests a different approach—what about skipping the clustering and splitting the database into two parts? The cost in this case is reduced to $8,000 while still mitigating most of the risk. In this case, the stakeholder agrees to the solution. The previous scenario shows the impact risk storming can have not only on the overall architecture, but also with regard to negotiations between architects and business stakeholders. Risk storming, combined with the risk assessments described at the start of this chapter, provide an excellent vehicle for identifying and tracking risk, improving the architecture, and handling negotiations between key stakeholders. 28

---

## Lámina 23

Técnicas de Arquitectura - Análisis de Riesgos

Lluvia de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

Consenso: Esta actividad es altamente colaborativa con el objetivo de obtener consenso entre todos los participantes con respecto al riesgo dentro de la arquitectura. Esta actividad es más eficaz cuando se dispone de una versión impresa grande del diagrama de arquitectura y se cuelga en la pared. En lugar de una versión impresa grande, se puede mostrar una versión electrónica en una pantalla grande.

Al llegar a la sesión de análisis de riesgos, los participantes comienzan a colocar sus notas Post-it en el diagrama de la arquitectura en el área donde individualmente encontraron el riesgo. Si se utiliza una versión electrónica, el arquitecto que realiza la sesión de evaluación de riesgos consulta a cada participante y coloca electrónicamente el riesgo en el diagrama en el área de la arquitectura donde se identificó el riesgo.

---

## Lámina 24

Técnicas de Arquitectura - Análisis de Riesgos

Lluvia de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

Una vez que todas las notas Post-it estén en su lugar, puede comenzar la parte colaborativa de la lluvia de riesgos. El objetivo de esta actividad de análisis de riesgos es analizar las áreas de riesgo en equipo y lograr un consenso en cuanto a la calificación del riesgo. Observe que se identificaron varias áreas de riesgo en la arquitectura.

---

## Lámina 25

Técnicas de Arquitectura - Análisis de Riesgos

Lluvia de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 26

Técnicas de Arquitectura - Análisis de Riesgos

Lluvia de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

Mitigación: Una vez que todos los participantes acuerdan la calificación de las áreas de riesgo de la arquitectura, se produce la actividad final y más importante: la mitigación de riesgos.

Mitigar el riesgo dentro de una arquitectura generalmente implica cambios o mejoras en ciertas áreas de la arquitectura que, de otro modo, podrían haberse considerado perfectas tal como eran. Esta actividad, que también suele ser colaborativa, busca formas de reducir o eliminar el riesgo identificado en la primera actividad.

---

## Lámina 27

Técnicas de Arquitectura - Análisis de Riesgos

Lluvia de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

Mitigación:

Puede haber casos en los que la arquitectura original deba cambiarse por completo en función de la identificación del riesgo, mientras que otros pueden ser una refactorización de la arquitectura sencilla, como agregar una cola para la contrapresión para reducir un problema de cuello de botella en el rendimiento.

Independientemente de los cambios requeridos en la arquitectura, esta actividad suele tener un costo adicional. Por esa razón, las partes interesadas clave suelen decidir si el costo supera el riesgo.

---

## Lámina 28

Bibliografía

Mark Richards, Neal  Ford. Fundamentals of Software Architecture: An Engineering Approach. O'Reilly, 2020.

---

## Lámina 29

_(sin texto: la lámina es una imagen)_
