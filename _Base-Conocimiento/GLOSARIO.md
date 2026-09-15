# Glosario

> Formato: **Término** — definición contextual · *dónde apareció* · nota de arquitecto si aplica.
> Solo se registran términos que aparezcan efectivamente en el material del diplomado.

## Módulo 0

- **Diplomado virtual asincrónico** — programa de Educación Continua no conducente a título, donde
  ≥70% del proceso formativo ocurre sin coincidencia temporal entre participantes y docentes.
  *Art. 1, lineamientos PUJ Cali V6.*
- **Objeto virtual de aprendizaje (OVA)** — unidad de contenido digital autocontenida (video,
  presentación, infografía, podcast) usada como vehículo del aprendizaje autónomo. *Art. 3.*
- **Brightspace** — LMS institucional de la PUJ Cali. *Art. 2.*
- **Encuentro sincrónico** — sesión programada de Q&A con el experto; carácter formativo y
  **no obligatorio**. *Art. 5.*

## Módulo 1

- **Arquitectura de software** — conjunto dinámico de elementos interrelacionados que definen cómo
  opera y se desarrolla un sistema; no una estructura estática. *M1, Contenidos obligatorios.*
  *[COMPL] Richards y Ford la descomponen en cuatro: estructura + características arquitectónicas +
  decisiones + principios de diseño.*
- **Atributo de calidad / característica arquitectónica** — propiedad no funcional que el sistema
  debe cumplir. Se clasifica en operacional, estructural o transversal. *M1, Cierre.*
  *Nota de arquitecto: si no se puede medir, no es un atributo de calidad.*
- **Características operacionales** — cómo se comporta el sistema en producción: disponibilidad,
  rendimiento, latencia, escalabilidad, elasticidad, recuperabilidad. *M1.*
- **Características estructurales** — cómo está construido: mantenibilidad, modularidad,
  extensibilidad, portabilidad, testabilidad, capacidad de despliegue. *M1.*
- **Características transversales** — las que no caben en las otras dos: seguridad, usabilidad,
  accesibilidad, privacidad, cumplimiento normativo. *M1.*
- **Restricción arquitectónica** — límite que guía diseño e implementación, en tres frentes:
  **negocio**, **tecnología** y **equipo/recursos**. *M1, Profundización.*
- **Decisión arquitectónica** — elección que define estructura y comportamiento del sistema;
  obligatoria, no negociable dentro del proyecto. *M1.*
- **Principio de diseño** — guía con margen de interpretación, a diferencia de la decisión.
  *[COMPL] Richards y Ford.*
- **ISO/IEC 25000 (SQuaRE)** — familia de normas de *Systems and software Quality Requirements
  and Evaluation*. *M1.*
- **ISO/IEC 25010** — modelo de calidad dentro de la familia 25000. La versión de **2011** que
  cita el diplomado define **8 características**: adecuación funcional, eficiencia de desempeño,
  compatibilidad, usabilidad, fiabilidad, seguridad, mantenibilidad y portabilidad.
  *[COMPL] La revisión de 2023 define 9 (añade Safety, renombra Usability→Interaction Capability
  y absorbe Portability en Flexibility) — verificar antes de citar.*
- **Primera ley de la arquitectura de software** — *todo en arquitectura de software es un
  trade-off*. *[COMPL] Richards y Ford; el material del M1 referencia "las leyes" pero el detalle
  está en el Genially no descargado.*
- **Segunda ley de la arquitectura de software** — *el "por qué" importa más que el "cómo"*.
  *[COMPL] Richards y Ford. Es la justificación conceptual de los ADR.*
