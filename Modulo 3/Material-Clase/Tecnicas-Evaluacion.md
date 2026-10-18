# Técnicas de Evaluación — deck oficial del Módulo 3

> **Tipo:** `material-oficial` (Recursos complementarios → «Presentaciones Adicionales», Brightspace, Unidad 4 de 5).
> **Fuente:** `TecnicasEvaluacion.pptx` (72 láminas), descargado el 2026-10-18 con sesión de Danny.
> **Extraído:** 2026-10-18, texto de las láminas tal cual. Las **notas del orador** se incluyen aparte
>  porque traen contenido (a menudo en inglés, del libro de referencia); las que solo tienen un número se omiten.
> **Límite de la extracción:** solo texto. Diagramas, figuras y tablas dibujadas como imagen NO están.
> **Este archivo no se edita.** Las notas y críticas van en `Aportes/`.

---

## Lámina 1

DIPLOMADO EN

ARQUITECTURA DE SOFTWARE

TÉCNICAS: EVALUACIÓN

---

## Lámina 2

EVALUACIÓN DE ARQUITECTURA

---

## Lámina 3

Técnicas de Arquitectura - Evaluación

La evaluación de la arquitectura es el proceso de determinar el grado en que una arquitectura es apta para el propósito para el que está destinada. La arquitectura es un contribuyente tan importante para el éxito de un proyecto de ingeniería de sistemas y software que tiene sentido hacer una pausa y asegurarse de que la arquitectura que está diseñando podrá proporcionar todo lo que se espera de ella. Ese es el papel de la evaluación, que se basa en analizar las alternativas. Afortunadamente, existen métodos maduros para analizar arquitecturas que utilizan muchos de los conceptos y técnicas que ya ha aprendido.

Introducción

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 4

Técnicas de Arquitectura - Evaluación

Toda arquitectura conlleva riesgos. El resultado de una evaluación de arquitectura incluye una identificación de partes riesgosas de la arquitectura. Un riesgo es un evento que tiene tanto un impacto como una probabilidad. El costo estimado de un riesgo es la probabilidad de que ese evento ocurra multiplicada por el costo del impacto. Arreglar esos riesgos no es un resultado de la evaluación. Una vez que se han identificado los riesgos, solucionarlos es, como la evaluación misma, una cuestión de costo/beneficio.

Actividad de Reducción de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 5

Técnicas de Arquitectura - Evaluación

La probabilidad de un evento de riesgo está relacionada, entre otras cosas, con cuán precedentes o sin precedentes son el sistema en desarrollo y su arquitectura. Si usted y su organización tienen una larga y profunda experiencia en este dominio, entonces la probabilidad de producir una mala arquitectura es menor que si este proyecto es su primera vez.

Por lo tanto, las evaluaciones actúan como una póliza de seguro. La cantidad de seguro que necesita depende de qué tan expuesto esté al riesgo de una arquitectura inadecuada y su tolerancia al riesgo.

Actividad de Reducción de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 6

Técnicas de Arquitectura - Evaluación

Las evaluaciones se pueden realizar a lo largo del proceso de desarrollo en diferentes fases, con diferentes evaluadores y con diferencias en la forma en que se realiza la evaluación. Independientemente de sus detalles precisos, las evaluaciones se basan en los conceptos que ya hemos aprendido: los sistemas se construyen para satisfacer los objetivos de negocio, los objetivos de negocio se ejemplifican mediante escenarios de atributos de calidad y los objetivos de atributos de calidad se logran mediante la aplicación de tácticas y patrones.

Actividad de Reducción de Riesgos

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 7

Técnicas de Arquitectura - Evaluación

Independientemente de quién realice la evaluación y cuándo se realice, una evaluación se basa en drivers arquitectónicos, principalmente requisitos significativos para la arquitectura (ASR) expresados como escenarios de atributos de calidad. El número de ASR que entran en la evaluación es una función de los factores contextuales y el costo de la evaluación. A continuación, describimos los posibles factores contextuales para la evaluación de la arquitectura.

Una evaluación puede llevarse a cabo en cualquier punto del proceso de diseño donde exista una arquitectura candidata, o al menos una parte revisable coherente de una.

Actividades Clave de la Evaluación

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 8

Técnicas de Arquitectura - Evaluación

Toda evaluación debe incluir (al menos) estos pasos:

Los revisores se aseguran individualmente de que entienden el estado actual de la arquitectura. Esto se puede hacer a través de documentación compartida, a través de una presentación del arquitecto o mediante alguna combinación de estos.

Los revisores determinan una serie de drivers para guiar la revisión. Es posible que estos drivers ya estén documentados, o pueden ser desarrollados por el equipo de revisión o por partes interesadas adicionales. Por lo general, los drivers más importantes que se deben revisar son los escenarios de atributos de calidad de alta prioridad (y no, por ejemplo, los casos de uso puramente funcionales).

Actividades Clave de la Evaluación

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 9

Técnicas de Arquitectura - Evaluación

3.  Para cada escenario, cada revisor debe determinar si se cumple o no. Los revisores plantean preguntas para determinar dos tipos de información. Primero, quieren determinar que el escenario está, de hecho, satisfecho. Esto podría hacerse haciendo que el arquitecto recorra la arquitectura y explique cómo se satisface el escenario. Si la arquitectura ya está documentada, los revisores pueden usar esa documentación para realizar esta evaluación. En segundo lugar, quieren determinar si alguno de los otros escenarios que se están considerando no se cumplirá debido a las decisiones tomadas en la parte de la arquitectura que se está revisando. Los revisores pueden plantear alternativas a cualquier aspecto arriesgado del diseño actual que pueda satisfacer mejor el escenario.

Actividades Clave de la Evaluación

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 10

Técnicas de Arquitectura - Evaluación

4.  Los revisores capturan los problemas potenciales expuestos durante el paso anterior. Esta lista de problemas potenciales forma la base para el seguimiento de la revisión. Si el problema potencial es un problema real, entonces debe solucionarse o los diseñadores y el director del proyecto deben tomar una decisión explícita de que están dispuestos a aceptar el riesgo.

Actividades Clave de la Evaluación

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 11

Técnicas de Arquitectura - Evaluación

¿Cuánto análisis se debe hacer? Las decisiones tomadas para lograr uno de los requisitos arquitectónicos fundamentales deben estar sujetas a más análisis que otras, porque darán forma a partes críticas de la arquitectura. Algunas consideraciones específicas incluyen estas:

La importancia de la decisión. Cuanto más importante sea la decisión, más cuidado se debe tener al tomarla y asegurarse de que sea correcta.

El número de alternativas potenciales. Cuantas más alternativas, más tiempo se podría dedicar a evaluarlas.

Suficientemente bueno en lugar de perfecto. Muchas veces, dos alternativas posibles no difieren dramáticamente en sus consecuencias.

Actividades Clave de la Evaluación

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 12

Técnicas de Arquitectura - Evaluación

Los evaluadores deben estar altamente capacitados en el dominio y los diversos atributos de calidad por los cuales se evaluará el sistema. Las excelentes habilidades organizativas y de facilitación también son imprescindibles para los evaluadores.

Evaluación por el Arquitecto

La evaluación se realiza, implícita o explícitamente, cada vez que el arquitecto toma una decisión de diseño clave para abordar un ASR o completa un hito de diseño. Esta evaluación implica decidir entre las alternativas en competencia.

¿Quién puede realizar la evaluación?

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 13

Técnicas de Arquitectura - Evaluación

Evaluación por revisión por pares

Los diseños arquitectónicos para abordar las ASR se pueden revisar por pares, al igual que el código se puede revisar por pares. Debe haber una cantidad fija de tiempo asignado para la revisión por pares, generalmente de varias horas a medio día. Si los diseñadores utilizan el proceso de diseño basado en atributos (ADD), se puede realizar una revisión por pares al final del paso 7 de cada iteración ADD.

¿Quién puede realizar la evaluación?

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 14

Técnicas de Arquitectura - Evaluación

Evaluación por parte de personas externas

Los evaluadores externos pueden echar un vistazo más objetivo a una arquitectura. “Afuera” es relativo; esto puede significar fuera del proyecto de desarrollo, fuera de la unidad de negocio donde reside el proyecto pero dentro de la misma empresa, o fuera de la empresa por completo. En la medida en que los evaluadores estén “afuera”, es menos probable que tengan miedo de plantear problemas delicados o problemas que no son evidentes debido a la cultura organizacional o porque “siempre lo hemos hecho de esa manera”.

¿Quién puede realizar la evaluación?

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 15

Técnicas de Arquitectura - Evaluación

Evaluación por parte de personas externas

A menudo, se elige a personas externas para participar en la evaluación porque poseen conocimientos o experiencia especializados, como conocimientos sobre un atributo de calidad que es importante para el sistema que se examina, habilidad con una tecnología en particular que se emplea o una larga experiencia en la evaluación exitosa de arquitecturas.

Además, ya sea justificado o no, los gerentes tienden a estar más inclinados a escuchar los problemas descubiertos por un equipo externo contratado a un costo considerable que por los miembros del equipo dentro de la organización.

¿Quién puede realizar la evaluación?

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 16

Técnicas de Arquitectura - Evaluación

Para las revisiones por pares o el análisis externo, se deben considerar una serie de factores contextuales al establecer una evaluación:

¿Qué artefactos están disponibles? Para realizar una evaluación arquitectónica, debe haber un artefacto que describa la arquitectura y esté fácilmente disponible. Algunas evaluaciones pueden tener lugar después de que el sistema esté operativo. En este caso, se pueden usar algunas herramientas de análisis y recuperación de la arquitectura para ayudar a descubrir la arquitectura, encontrar fallas en el diseño de la arquitectura y probar que el sistema construido se ajusta al sistema diseñado.

Factores contextuales

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 17

Técnicas de Arquitectura - Evaluación

¿Quién ve los resultados? Algunas evaluaciones se realizan con pleno conocimiento y participación de todas las partes interesadas. Otros se realizan de forma más privada.

¿Qué partes interesadas participarán? El proceso de evaluación debe incluir un método para obtener los objetivos y preocupaciones importantes de las partes interesadas con respecto al sistema. En esta etapa, es fundamental identificar a las personas que se necesitan y garantizar su participación en la evaluación.

Factores contextuales

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 18

Técnicas de Arquitectura - Evaluación

¿Cuáles son los objetivos de negocio? La evaluación debe responder si el sistema cumplirá con los objetivos de negocio. Si los objetivos de negocio no se capturan y priorizan explícitamente antes de la evaluación, una parte de la evaluación debe dedicarse a esta tarea.

Factores contextuales

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 19

Técnicas de Arquitectura - Evaluación

El Método de Análisis de Tradeoff de Arquitectura (ATAM) es el proceso que ha formalizado el Software Engineering Institute - SEI para realizar evaluaciones de arquitectura. El ATAM se ha utilizado durante más de dos décadas para evaluar arquitecturas de software de grandes sistemas en dominios que van desde la automoción hasta las finanzas y la defensa. El ATAM está diseñado para que los evaluadores no necesiten familiarizarse previamente con la arquitectura o sus objetivos de negocio, y el sistema no necesita estar construido todavía. Un ejercicio ATAM puede realizarse de forma presencial o remota.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 20

Técnicas de Arquitectura - Evaluación

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 21

Técnicas de Arquitectura - Evaluación

Participantes en la ATAM

La ATAM requiere la participación y cooperación mutua de tres grupos:

El equipo de evaluación. Este grupo es externo al proyecto cuya arquitectura se está evaluando. Por lo general, consta de tres a cinco personas. A cada miembro del equipo se le asigna una serie de roles específicos para desempeñar durante la evaluación; una sola persona puede adoptar varios roles en un ejercicio ATAM. El equipo de evaluación puede ser una unidad permanente en la que se realizan regularmente evaluaciones de arquitectura, o sus miembros pueden elegirse de un grupo de personas con conocimientos arquitectónicos para la ocasión.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 22

Técnicas de Arquitectura - Evaluación

Participantes en la ATAM

Tomadores de decisiones del proyecto. Estas personas están facultadas para hablar en nombre del proyecto de desarrollo o tienen la autoridad para exigir cambios en él. Por lo general, incluyen al gerente del proyecto y, si un cliente identificable está pagando la factura del desarrollo, también puede estar presente un representante de ese cliente. El arquitecto siempre está incluido: una regla cardinal de la evaluación de la arquitectura es que el arquitecto debe participar voluntariamente.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 23

Técnicas de Arquitectura - Evaluación

Participantes en la ATAM

Interesados en la arquitectura. Las partes interesadas tienen un interés personal en que la arquitectura funcione como se anuncia. Son las personas cuya capacidad para hacer su trabajo depende de la arquitectura que promueve la modificabilidad, la seguridad, la alta confiabilidad o similares. Las partes interesadas incluyen desarrolladores, probadores, integradores, mantenedores, ingenieros de rendimiento, usuarios y constructores de sistemas que interactúan con el que se está considerando. Su trabajo durante una evaluación es articular los objetivos de atributos de calidad específicos que la arquitectura debe cumplir para que el sistema se considere un éxito.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 24

Técnicas de Arquitectura - Evaluación

Roles del Team - ATAM

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

ROL

RESPONSABILIDADES

Líder del Equipo

Configura la evaluación; coordina con el cliente, asegurándose de que se satisfagan las necesidades del cliente; establece el contrato de evaluación; forma el equipo de evaluación; ve que el informe final es producido y entregado.

Líder de Evaluación

Ejecuta la evaluación; facilita la elicitación de escenarios; administra el proceso de priorización de escenarios; facilita la evaluación de escenarios frente a la arquitectura.

Escritor de Escenarios

Escribe escenarios en una forma pública compartible durante la obtención de escenarios; captura la redacción acordada de cada escenario, deteniendo la discusión hasta que se captura la redacción exacta.

---

## Lámina 25

Técnicas de Arquitectura - Evaluación

Roles del Team - ATAM

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

ROL

RESPONSABILIDADES

e-Escritor

Captura los procedimientos en formato electrónico: escenarios sin procesar, tema(s) que motivan cada escenario (a menudo perdidos en la redacción del escenario mismo) y los resultados del análisis de cada escenario; también genera una lista de escenarios adoptados para su distribución a todos los participantes.

Cuestionador

Hace preguntas de sondeo basadas en atributos de calidad.

---

## Lámina 26

Técnicas de Arquitectura - Evaluación

Salidas de ATAM

Una presentación concisa de la arquitectura. Un requisito del ATAM es que la arquitectura se presente en una hora o menos, lo que conduce a una presentación arquitectónica que es concisa y, por lo general, comprensible.

Articulación de los objetivos de negocio. Con frecuencia, los objetivos de negocio presentados en el ejercicio ATAM son vistos por primera vez por algunos de los participantes reunidos y estos se capturan en los resultados. Esta descripción de los objetivos sobrevive a la evaluación y se convierte en parte del legado del proyecto.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 27

Técnicas de Arquitectura - Evaluación

Salidas de ATAM

Requisitos de atributos de calidad priorizados expresados como escenarios de atributos de calidad. Estos escenarios de atributos de calidad adoptan la forma descrita previamente. El ATAM utiliza escenarios de atributos de calidad priorizados como base para evaluar la arquitectura. Es posible que esos escenarios ya existan (quizás como resultado de un ejercicio anterior de captura de requisitos o una actividad ADD), pero si no es así, los participantes los generan como parte del ejercicio ATAM.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 28

Técnicas de Arquitectura - Evaluación

Salidas de ATAM

Un conjunto de riesgos y no riesgos. Un riesgo arquitectónico es una decisión que puede tener consecuencias indeseables a la luz de los requisitos de atributos de calidad establecidos. Del mismo modo, un no riesgo arquitectónico es una decisión que, tras el análisis, se considera segura. Los riesgos identificados forman la base para un plan de mitigación de riesgos arquitectónicos. Estos riesgos son el resultado principal de un ejercicio ATAM.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 29

Técnicas de Arquitectura - Evaluación

Salidas de ATAM

Un conjunto de temas de riesgo. Cuando se completa el análisis, el equipo de evaluación examina el conjunto completo de riesgos descubiertos para buscar temas generales que identifiquen debilidades sistémicas en la arquitectura o incluso en el proceso y el equipo de arquitectura. Si no se tratan, estos temas de riesgo amenazarán los objetivos de negocio del proyecto.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 30

Técnicas de Arquitectura - Evaluación

Salidas de ATAM

Mapeo de las decisiones arquitectónicas a los requisitos de calidad. Las decisiones arquitectónicas pueden interpretarse en términos de los drivers que apoyan o dificultan. Para cada escenario de atributo de calidad examinado durante un ejercicio ATAM, se determinan y capturan aquellas decisiones arquitectónicas que ayudan a lograrlo. Pueden servir como una declaración de los fundamentos de esas decisiones.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 31

Técnicas de Arquitectura - Evaluación

Salidas de ATAM

Un conjunto de puntos de sensibilidad identificados y puntos de tradeoff. Los puntos de sensibilidad son decisiones arquitectónicas que tienen un marcado efecto en la respuesta de un atributo de calidad. Los tradeoffs ocurren  cuando dos o más respuestas de atributos de calidad son sensibles a la misma decisión arquitectónica, pero una de ellas mejora mientras que la otra se degrada, de ahí la compensación.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 32

Técnicas de Arquitectura - Evaluación

Salidas de ATAM

Los resultados del ejercicio ATAM se pueden utilizar para elaborar un informe final que resume el método, resume los procedimientos, captura los escenarios y su análisis, y cataloga los hallazgos.

Una evaluación basada en ATAM también produce resultados intangibles que no deben ignorarse. Estos incluyen un sentido de comunidad por parte de las partes interesadas, canales de comunicación abiertos entre el arquitecto y las partes interesadas, y una mejor comprensión general entre todos los participantes de la arquitectura y sus fortalezas y debilidades. Si bien estos resultados son difíciles de medir, no son menos importantes que los demás.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 33

Técnicas de Arquitectura - Evaluación

Fases de ATAM

Las actividades en una evaluación basada en ATAM se distribuyen en cuatro fases:

En la Fase 0, “Asociación y preparación”, el liderazgo del equipo de evaluación y los tomadores de decisiones clave del proyecto resuelven los detalles del ejercicio. Los representantes del proyecto informan a los evaluadores sobre el proyecto para que el equipo de evaluación pueda complementarse con personas que posean la experiencia adecuada. Juntos, los dos grupos acuerdan la logística, el momento en que se realizará la evaluación y la tecnología utilizada para apoyar las reuniones. También acuerdan una lista preliminar de partes interesadas (por nombre, no solo función) y negocian cuándo se entregará el informe final ya quién.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 34

Técnicas de Arquitectura - Evaluación

Fases de ATAM

Durante las Fases 1 y 2, conocidas colectivamente como "Evaluación", todos se dedican al negocio del análisis. A estas alturas, el equipo de evaluación habrá estudiado la documentación de la arquitectura y tendrá una buena idea de qué se trata el sistema, los principales enfoques arquitectónicos adoptados y los atributos de calidad que son de suma importancia. Durante la fase 1, el equipo de evaluación se reúne con los responsables de la toma de decisiones del proyecto para comenzar la recopilación y el análisis de la información. En la fase 2, las partes interesadas de la arquitectura agregan sus aportes a los procedimientos y el análisis continúa.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 35

Técnicas de Arquitectura - Evaluación

Fases de ATAM

En la Fase 3, “Seguimiento”, el equipo de evaluación produce y entrega su informe final. Este informe, que puede ser un documento formal o simplemente un conjunto de diapositivas, primero se distribuye a las partes interesadas clave para garantizar que no contenga errores de comprensión. Una vez completada esta revisión, se entrega al cliente.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 36

Técnicas de Arquitectura - Evaluación

Fases de ATAM

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 37

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Las fases de análisis de ATAM (fases 1 y 2) constan de nueve pasos. Los pasos 1 a 6 se llevan a cabo en la fase 1 con el equipo de evaluación y los responsables de la toma de decisiones del proyecto, por lo general, el equipo de arquitectura, el director del proyecto y el cliente. En la fase 2, con todas las partes interesadas involucradas, se resumen los pasos 1 a 6 y se llevan a cabo los pasos 7 a 9.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 38

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 1: Presentar el ATAM.

El primer paso requiere que el líder de la evaluación presente el ATAM a los representantes del proyecto reunidos. Este tiempo se utiliza para explicar el proceso que todos seguirán, responder preguntas y establecer el contexto y las expectativas para el resto de las actividades. Utilizando una presentación estándar, el líder describe brevemente los pasos de ATAM y los resultados de la evaluación.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 39

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 2: Presentar los Objetivos de Negocio

Todos los involucrados en la evaluación, tanto los representantes del proyecto como los miembros del equipo de evaluación, deben comprender el contexto del sistema y los principales objetivos comerciales que motivan su desarrollo. En este paso, un tomador de decisiones del proyecto (idealmente, el gerente del proyecto o el representante del cliente) presenta una descripción general del sistema desde una perspectiva empresarial. Esta presentación debe describir los siguientes aspectos del proyecto:

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 40

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 2: Presentar los Objetivos de Negocio

Las funciones más importantes del sistema.

Cualquier restricción técnica, administrativa, económica o política relevante Los objetivos comerciales y el contexto en relación con el proyecto.

Los principales interesados

Los drivers arquitectónicos (enfatizando los requisitos significativos desde el punto de vista arquitectónico)

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 41

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 3: Presentar la Arquitectura

El arquitecto principal (o el equipo de arquitectura) hace una presentación que describe la arquitectura con un nivel de detalle apropiado. El "nivel apropiado" depende de varios factores: qué parte de la arquitectura se ha diseñado y documentado, cuánto tiempo está disponible y la naturaleza de los requisitos de comportamiento y calidad.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 42

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 3: Presentar la Arquitectura

En esta presentación, el arquitecto cubre las limitaciones técnicas, como el sistema operativo, las plataformas prescritas para su uso y otros sistemas con los que este sistema debe interactuar. Lo más importante es que el arquitecto describe los enfoques arquitectónicos (o patrones o tácticas, si el arquitecto domina ese vocabulario) utilizados para cumplir con los requisitos.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 43

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 3: Presentar la Arquitectura

Los diagramas de contexto, las vistas de componentes y conectores, la descomposición de módulos o las vistas en capas y la vista de implementación son útiles en casi todas las evaluaciones, y el arquitecto debe estar preparado para mostrarlas. Se pueden presentar otras vistas si contienen información relevante para la arquitectura en cuestión, especialmente información relevante para satisfacer requisitos de atributos de calidad importantes.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 44

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 4: Identificar los enfoques arquitectónicos

El ATAM se centra en analizar una arquitectura mediante la comprensión de sus enfoques arquitectónicos. Los patrones y tácticas arquitectónicas son útiles (entre otras razones) por las formas conocidas en las que cada uno afecta los atributos de calidad particulares. Por ejemplo, un patrón en capas tiende a brindar portabilidad y mantenibilidad a un sistema, posiblemente a expensas del rendimiento. Un patrón de publicación-suscripción es escalable en la cantidad de productores y consumidores de datos, mientras que el patrón de redundancia activa promueve una alta disponibilidad.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 45

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 5: Generar un árbol de utilidad de atributos de calidad

Los objetivos de los atributos de calidad se articulan en detalle a través de un árbol de utilidad de atributos de calidad. Los árboles de utilidad sirven para concretar los requisitos al definir con precisión los requisitos de atributos de calidad relevantes que los arquitectos estaban trabajando para proporcionar.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 46

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 5: Generar un árbol de utilidad de atributos de calidad

Los objetivos de atributos de calidad importantes para la arquitectura bajo consideración fueron nombrados en el paso 2, cuando se presentaron los objetivos de negocio, pero no con un grado de especificidad que permitiera el análisis.

Recuerde que el árbol de utilidades es construido por el arquitecto y los tomadores de decisiones del proyecto. Juntos, determinan la importancia de cada escenario: el arquitecto califica la dificultad técnica o el riesgo del escenario (en una escala H, M, L) y los tomadores de decisiones del proyecto califican su importancia de negocio.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 47

Técnicas de Arquitectura - Evaluación

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 48

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 6: Analice los enfoques arquitectónicos

El equipo de evaluación examina los escenarios mejor calificados (identificados en el árbol de utilidades) uno a la vez; se le pide al arquitecto que explique cómo la arquitectura soporta cada uno. Los miembros del equipo de evaluación, especialmente los que preguntan, investigan los enfoques arquitectónicos que el arquitecto usó para llevar a cabo el escenario. En el camino, el equipo de evaluación documenta las decisiones arquitectónicas relevantes e identifica y cataloga sus riesgos, no riesgos y compensaciones.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 49

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 6: Analice los enfoques arquitectónicos

Para enfoques bien conocidos, el equipo de evaluación pregunta cómo el arquitecto superó las debilidades conocidas en el enfoque o cómo el arquitecto obtuvo la seguridad de que el enfoque era suficiente. El objetivo es que el equipo de evaluación esté convencido de que la instanciación del enfoque es adecuada para cumplir con los requisitos específicos del atributo para los que está destinado.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 50

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 6: Analice los enfoques arquitectónicos

El análisis durante el paso 6 no pretende ser exhaustivo. La clave es obtener suficiente información arquitectónica para establecer algún vínculo entre las decisiones arquitectónicas que se han tomado y los requisitos de atributos de calidad que deben satisfacerse.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 51

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

La figura muestra una plantilla para capturar el análisis de un enfoque arquitectónico para un escenario. Como se muestra en la figura, según los resultados de este paso, el equipo de evaluación puede identificar y registrar un conjunto de riesgos y no riesgos, puntos de sensibilidad y tradeoffs.

---

## Lámina 52

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Pausa e inicio de la Fase 2

El equipo de evaluación resume lo que ha aprendido e interactúa informalmente con el arquitecto durante una pausa de una semana más o menos. Se pueden analizar más escenarios durante este período, si se desea, o se pueden aclarar las respuestas a las preguntas planteadas en la fase 1.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 53

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Pausa e inicio de la Fase 2

Los asistentes a la reunión de la fase 2 incluyen una lista ampliada de participantes, con partes interesadas adicionales que se unen a la discusión. Para usar una analogía de la programación: la Fase 1 es similar a cuando pruebas tu propio programa, usando tus propios criterios. La fase 2 es cuando entrega su programa a un grupo independiente de control de calidad, que probablemente someterá su programa a una variedad más amplia de pruebas y entornos.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 54

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Pausa e inicio de la Fase 2

En la fase 2, se repite el paso 1 para que las partes interesadas comprendan el método y los roles que deben desempeñar. Luego, el líder de la evaluación resume los resultados de los pasos 2 a 6 y comparte la lista actual de riesgos, no riesgos, puntos sensibles y compensaciones. Después de poner al día a las partes interesadas con los resultados de la evaluación hasta el momento, se pueden llevar a cabo los tres pasos restantes.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 55

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 7: lluvia de ideas y priorización de escenarios

El equipo de evaluación les pide a las partes interesadas que hagan una lluvia de ideas sobre escenarios de atributos de calidad que sean operativamente significativos con respecto a los roles individuales de las partes interesadas. Es probable que un mantenedor proponga un escenario de modificabilidad, mientras que un usuario probablemente presente un escenario que exprese la facilidad de operación, y una persona de control de calidad propondrá un escenario sobre probar el sistema o poder replicar el estado del sistema antes de un fallo.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 56

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 7: lluvia de ideas y priorización de escenarios

Si bien la generación del árbol de utilidades (paso 5) se usa principalmente para comprender cómo el arquitecto percibió y manejó los controladores arquitectónicos de atributos de calidad, el propósito de la lluvia de ideas de escenarios es tomar el pulso de la comunidad de partes interesadas más grande: comprender qué significa el éxito del sistema para ellos. La lluvia de ideas de escenarios funciona bien en grupos más grandes, creando una atmósfera en la que las ideas y los pensamientos de una persona estimulan las ideas de los demás.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 57

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 7: lluvia de ideas y priorización de escenarios

Una vez que se han recopilado los escenarios, se deben priorizar, por las mismas razones por las que se necesita priorizar los escenarios en el árbol de utilidades: el equipo de evaluación necesita saber dónde dedicar su limitado tiempo de análisis. En primer lugar, se pide a las partes interesadas que fusionen escenarios que consideren que representan el mismo comportamiento o preocupación por la calidad.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 58

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 7: lluvia de ideas y priorización de escenarios

A continuación, votan por los escenarios que consideran más importantes. A cada parte interesada se le asigna un número de votos equivalente al 30 por ciento del número de escenarios, 1 redondeado hacia arriba. Así, si se recogieran 40 escenarios, cada actor tendría 12 votos. Estos votos se pueden asignar de cualquier manera que la parte interesada considere adecuada: los 12 votos para 1 escenario, 1 voto para cada uno de los 12 escenarios distintos o cualquier punto intermedio.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 59

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 8: Analice los enfoques arquitectónicos

Después de recopilar y priorizar los escenarios en el paso 7, el equipo de evaluación guía al arquitecto en el proceso de análisis de los escenarios mejor calificados. El arquitecto explica cómo las decisiones arquitectónicas contribuyen a la realización de cada escenario. Idealmente, esta actividad estará dominada por la explicación del arquitecto de los escenarios en términos de enfoques arquitectónicos discutidos previamente. En este paso, el equipo de evaluación realiza las mismas actividades que en el paso 6, utilizando los escenarios recién generados mejor calificados. Por lo general, este paso podría cubrir los 5 a 10 escenarios principales, según lo permita el tiempo.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 60

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 9: Presentar los resultados

En el paso 9, el equipo de evaluación se reúne y agrupa los riesgos en temas de riesgo, en función de alguna preocupación subyacente común o deficiencia sistémica. Por ejemplo, un grupo de riesgos sobre documentación inadecuada o desactualizada podría agruparse en un tema de riesgo que indique que la documentación no se tiene suficientemente en cuenta. Un grupo de riesgos sobre la incapacidad del sistema para funcionar frente a varias fallas de hardware y/o software podría generar un tema de riesgo sobre la atención insuficiente a la capacidad de respaldo o la provisión de alta disponibilidad.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 61

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 9: Presentar los resultados

Para cada tema de riesgo, el equipo de evaluación identifica cuáles de los objetivos enumerados en el paso 2 se ven afectados. Identificar los temas de riesgo y luego relacionarlos con drivers específicos cierra el círculo de la evaluación al relacionar los resultados finales con la presentación inicial, proporcionando así un cierre satisfactorio para el ejercicio. Igualmente, importante, eleva los riesgos que fueron descubiertos a la atención de la gerencia. Lo que de otro modo podría haberle parecido a un gerente como un problema técnico esotérico, ahora se identifica sin ambigüedades como una amenaza a algo que al gerente le preocupa.

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 62

Técnicas de Arquitectura - Evaluación

Pasos de las Fases de Evaluación ATAM

Paso 9: Presentar los resultados

La información recopilada de la evaluación se resume y se presenta a las partes interesadas. Se presentan las siguientes salidas:

Los enfoques arquitectónicos documentados

El conjunto de escenarios y su priorización a partir de la lluvia de ideas

El árbol de la utilidad

Los riesgos y no riesgos descubiertos

Los puntos de sensibilidad y las compensaciones encontradas

Temas de riesgo y los objetivos de negocio amenazados por cada uno

ATAM - Método de Análisis de Tradeoff de Arquitectura

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 63

Técnicas de Arquitectura - Evaluación

El método de evaluación de arquitectura ligera (LAE) está diseñado para usarse en un contexto interno del proyecto donde la revisión la llevan a cabo pares de manera regular. Utiliza los mismos conceptos que el ATAM y está destinado a realizarse con regularidad. Se puede convocar una sesión LAE para centrarse en lo que ha cambiado desde la revisión anterior (en la arquitectura o en los drivers de la arquitectura) o para examinar una parte de la arquitectura no examinada anteriormente. Debido a este alcance limitado, muchos de los pasos del ATAM se pueden omitir o acortar.

Evaluación de Arquitectura Ligera

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 64

Técnicas de Arquitectura - Evaluación

La duración de un ejercicio LAE depende de la cantidad de escenarios de atributos de calidad generados y examinados, que a su vez se basa en el alcance de la revisión. El número de escenarios examinados depende de la importancia del sistema que se está revisando. Por lo tanto, un ejercicio LAE puede ser tan corto como un par de horas o tan largo como un día completo. Se lleva a cabo en su totalidad por miembros internos de la organización.

Evaluación de Arquitectura Ligera

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 65

Técnicas de Arquitectura - Evaluación

Debido a que los participantes son todos internos a la organización y menos en número que para el ATAM, dar a todos su opinión y lograr un entendimiento compartido lleva mucho menos tiempo. Además, un ejercicio LAE, por ser un proceso ligero, se puede hacer con regularidad; a su vez, muchos de los pasos del método pueden omitirse o solo mencionarse brevemente. Los pasos potenciales en un ejercicio LAE, junto con nuestras experiencias sobre cómo se desarrollan en la práctica, se muestran en la siguiente tabla. El ejercicio LAE suele ser convocado y dirigido por el arquitecto del proyecto.

Evaluación de Arquitectura Ligera

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 66

Técnicas de Arquitectura - Evaluación

Evaluación de Arquitectura Ligera

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 67

Técnicas de Arquitectura - Evaluación

Evaluación de Arquitectura Ligera

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 68

Técnicas de Arquitectura - Evaluación

Evaluación de Arquitectura Ligera

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 69

Técnicas de Arquitectura - Evaluación

No hay un informe final, pero (como en el ATAM) un documentador es responsable de capturar los resultados, que luego pueden compartirse y servir como base para la remediación de riesgos. Un LAE completo puede procesarse en menos de un día, tal vez una tarde. Los resultados dependerán de qué tan bien comprenda el equipo reunido los objetivos del método, las técnicas del método y el sistema mismo. El equipo de evaluación, al ser interno, suele ser menos objetivo que un equipo de evaluación externo, y esto puede comprometer el valor de sus resultados: se tiende a escuchar menos ideas nuevas y menos opiniones discrepantes. Sin embargo, esta versión de evaluación es económica, es fácil de convocar e implica una ceremonia relativamente sencilla, por lo que puede implementarse rápidamente cada vez que un proyecto requiera una verificación de cordura de garantía de calidad de la arquitectura.

Evaluación de Arquitectura Ligera

Maestría en Ingeniería de Software – Arquitectura de Software

---

## Lámina 70

Software Engineering Institute - Architecture Tradeoff Analysis Method Collection

Lecturas

---

## Lámina 71

Humberto Cervantes, Rick Kazman. Designing Software Architectures: A Practical Approach. SEI / Addison-Wesley, 2016.

Bibliografía

Len Bass, Paul Clements, Rick Kazman. Software Architecture in Practice. 4th Edition. SEI / Addison-Wesley, 2022​

---

## Lámina 72

_(sin texto: la lámina es una imagen)_
