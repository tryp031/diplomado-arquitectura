# Módulo 1 — Fundamentos de la Arquitectura de Software

> Fuente: `Material-Clase/Modulo1-ArquitecturaSoftware.md` (Brightspace, Unidad 2 de 5).
> Extraído: 2026-09-08. Todo lo de esta página es **contenido del diplomado**.

**Duración estimada:** 15 horas · **Ventana:** 07/09/2026 → 29/09/2026
**Encuentros sincrónicos:** martes 15/09 y martes 29/09, 6:00 pm

## Estructura de la unidad (5 secciones + 1 de recursos)

| # | Sección | Tipo | Estado |
|---|---|---|---|
| 1 | Contenidos obligatorios | Recursos (2 infografías + 1 video + 1 infografía) | ✅ visitado |
| 2 | Evidencia de aprendizaje: autoevaluación M1 | Cuestionario calificado | ⬜ **pendiente** |
| 3 | Evidencia de aprendizaje: actividad M1 | Entrega — Reto de Latencia Mínima | ⬜ **pendiente** |
| 4 | Conclusiones | Cierre | ✅ visitado |
| 5 | Recursos complementarios | Bibliografía | ✅ visitado |

## Temario declarado por el módulo

### A. El papel estratégico de la arquitectura de software
- La arquitectura no es una estructura estática, sino un **conjunto dinámico de elementos
  interrelacionados** que definen cómo opera y se desarrolla un sistema.
- Alineación de soluciones tecnológicas con **objetivos de negocio**.
- **Responsabilidades del arquitecto.**
- **Las tres dimensiones clave** que definen su importancia:
  1. Estructuración de la complejidad.
  2. Análisis temprano de atributos de calidad.
  3. Toma de decisiones técnicas informadas.

### B. Leyes y alcance de la arquitectura de software
- Leyes fundamentales que rigen la arquitectura.
- Alcance en la creación y evolución de aplicaciones.
- Principios que guían las decisiones arquitectónicas.

### C. Restricciones y decisiones
- Decisiones clave: definen estructura y comportamiento del sistema.
- **Restricciones como límites** que guían diseño e implementación, en tres frentes:
  **negocio**, **tecnología** y **equipo/recursos**.
- Impacto de las decisiones en performance, seguridad y mantenibilidad — desde la creación
  y a lo largo de la evolución del sistema.

### D. Atributos de calidad y características arquitectónicas
- Definición y clasificación en tres categorías:
  - **Operacionales** (p. ej. disponibilidad, rendimiento, escalabilidad).
  - **Estructurales** (p. ej. mantenibilidad, modularidad).
  - **Transversales** (p. ej. seguridad, usabilidad).
- Estándar **ISO/IEC 25010** (familia ISO/IEC 25000 — SQuaRE) para evaluar calidad.
- Cómo garantizar calidad en rendimiento, seguridad y mantenibilidad.

## Recursos obligatorios (enlaces embebidos)

| Recurso | Tema | URL |
|---|---|---|
| Infografía 1 (Genially) | Fundamentos de la arquitectura de software | https://view.genially.com/663ad43275eb060014ff0ca3 |
| Infografía 2 (Genially) | Leyes y alcance de la arquitectura de software | https://view.genially.com/663af4768b3ea40013334b37 |
| Video (YouTube) | La importancia de la Arquitectura de Software | https://www.youtube.com/watch?v=Ne396XnJ8RI |
| Infografía 3 (Genially) | Restricciones y decisiones de la arquitectura (M1P4) | https://view.genially.com/683a0ab406169c8e03907ff1 |
| Presentación (Genially) | Atributos de calidad (M1P5) | https://view.genially.com/683a0ae806169c8e0390c363 |

> ⚠️ Los 4 Genially y el video **no quedaron descargados** — son contenido embebido externo.
> El detalle fino (listas de leyes, taxonomía exacta de atributos) vive ahí, no en el HTML.

## Referencias bibliográficas del módulo

- **Richards y Ford (2020).** *Fundamentals of Software Architecture: An Engineering Approach.* O'Reilly.
- **Bass, Clements y Kazman (2022).** *Software Architecture in Practice*, 4.ª ed. SEI / Addison-Wesley.

Estos dos libros son **la fuente real del temario**: las "tres dimensiones", las "leyes de la
arquitectura" y la clasificación operacional/estructural/transversal vienen de Richards y Ford;
los atributos de calidad y su análisis temprano, de Bass, Clements y Kazman.

## Recursos complementarios (14 enlaces)

**Resiliencia y disponibilidad**
- AWS Blog — *Disaster Recovery (DR) Architecture on AWS*, partes I–IV (Eliot, 2021):
  I estrategias · II backup & restore · III pilot light y warm standby · IV multi-site active/active.
- Netflix Tech Blog (2019) — *Tips for high availability*.
- Fowler (2014) — *Circuit Breaker*.

**Entrega y despliegue**
- Hodgson (2017) — *Feature toggles (feature flags)*.
- Sharma (2023) — *From big bang to canary: deployment strategies*.

**Seguridad**
- OWASP Top 10:2021 · SANS/CWE Top 25 · SAFECode (2018) *Fundamental practices for secure
  software development* · Schmitt (2024) *SAST vs. DAST* · `awesome-pentest` (GitHub).

**Calidad**
- ISO/IEC 25010:2011 — https://iso25000.com/index.php/normas-iso-25000/iso-25010

> Observación: los complementarios son casi todos de **resiliencia, DR, despliegue y seguridad**,
> con fuerte peso AWS. Es coherente con el perfil del docente y probablemente anticipa los módulos 2–4.
