# Diplomado en Arquitectura de Software y Cloud Computing

## Unidad 3 de 5 — Módulo 2

> **Tipo:** `material-oficial`. Texto de las páginas de Brightspace guardadas el 28/09/2026.
> **Extraído:** 2026-09-30. **Este archivo no se edita.**
> **Estado en Brightspace al guardar:** «1 de 5 requisitos completados» (solo *Contenidos obligatorios*).

## Estructura de la unidad (orden del menú lateral)

1. Contenidos obligatorios — ✅ completado
2. Evidencia de aprendizaje: autoevaluación M2 — cuestionario (`quiz_summary.d2l?qi=303577`)
3. Evidencia de aprendizaje: actividad M2 — entrega (`content/402764/fullscreen/3088707`)
4. Conclusiones
5. Recursos complementarios

> ⚠️ **Lo que NO quedó capturado** (las páginas 2 y 3 se guardaron como marco vacío: el contenido
> real vive en un `iframe` que exige sesión):
> - **Enunciado, rúbrica, formato y fecha de la actividad M2.**
> - Reglas de la autoevaluación M2 (nº de intentos, tiempo, nº de preguntas).
> - Las 4 presentaciones Genially y el video de YouTube de «Contenidos obligatorios» (embebidos
>   externos): `view.genially.com/683a05d4…`, `…683a0687…`, `…683a077a…`, `…683a085c…` y
>   `youtube.com/embed/MbUXkPdKaGw`.

---

## 1. Contenidos obligatorios

### Introducción

En este primer tema del módulo, te sumergirás en los requerimientos de calidad que acompañan a los
requerimientos funcionales, como la latencia, disponibilidad y seguridad. Aprenderás a identificar
los requerimientos arquitecturalmente significativos (ASRs), esenciales para diseñar sistemas
robustos y eficientes. Descubrirás cómo estos atributos de calidad influyen en el diseño y
funcionamiento de un sistema a través de ejemplos prácticos.

Este tema te proporcionará las bases necesarias para entender la importancia de los ASRs en la
arquitectura de software, preparándote para abordar los desafíos que estos presentan y optimizar el
rendimiento, la escalabilidad y la confiabilidad del sistema.

Presentación interactiva: **Requerimientos de calidad** — explora los requerimientos de calidad,
su importancia, clasificación y relación con las tácticas de diseño. *(Genially #1, no capturado)*

### Profundización

Se profundiza en las tácticas de arquitectura que aseguran la calidad: disponibilidad, desempeño y
seguridad, y cómo cada uno impacta el diseño y funcionamiento de un sistema, con ejemplos y
escenarios prácticos.

- **Disponibilidad (AVAILABILITY)** — presentación interactiva: definición, importancia y factores
  que la afectan; ejemplos y estrategias de continuidad operativa. *(Genially #2, no capturado)*
- **Desempeño (PERFORMANCE)** — presentación interactiva: incluye rendimiento y concurrencia;
  definición, factores y métricas de evaluación. *(Genially #3, no capturado)*
- **Seguridad (SECURITY)** — **video**: confidencialidad, integridad y disponibilidad; privacidad
  y regulaciones como GDPR que protegen la información de identificación personal (PII).
  *(YouTube, no capturado)*

### Cierre

- **Interoperabilidad (INTEROPERABILITY)** — presentación interactiva: cómo los sistemas
  interactúan eficazmente; integración e intercambio entre componentes heterogéneos; escenarios
  concretos (ejemplos del sector salud) y tácticas como **descubrimiento de servicios,
  orquestación y adaptación de interfaces**. *(Genially #4, no capturado)*

---

## 4. Conclusiones

En este módulo, hemos explorado cómo las tácticas de arquitectura aseguran la calidad de los
sistemas de software. Abordamos los Requerimientos Arquitecturalmente Significativos (ASRs) y su
impacto en la arquitectura del sistema, así como los atributos de disponibilidad, desempeño,
seguridad e interoperabilidad descritos así:

- **Disponibilidad:** asegura que el sistema esté siempre listo para realizar su tarea, incluso en
  situaciones de falla.
- **Desempeño:** optimiza el tiempo y la concurrencia para mejorar el rendimiento del sistema.
- **Seguridad:** protege los datos contra el acceso no autorizado y garantiza la privacidad.
- **Interoperabilidad:** facilita la integración y comunicación efectiva entre sistemas
  heterogéneos.

En resumen, estas tácticas construyen sistemas robustos y optimizados, moldeando experiencias y
fortaleciendo la confianza del cliente.

---

## 5. Recursos complementarios

### Presentaciones adicionales (capturadas en `Tacticas-*.md`)

- Tácticas Usabilidad · Tácticas Seguridad · Tácticas Disponibilidad · Tácticas Desplegabilidad ·
  Tácticas Desempeño

### Material adicional

- Eliot (2021). *Disaster Recovery (DR) Architecture on AWS*, Partes I–IV. AWS Architecture Blog.
  - I: https://aws.amazon.com/es/blogs/architecture/disaster-recovery-dr-architecture-on-aws-part-i-strategies-for-recovery-in-the-cloud/
  - II (Backup and Restore): https://aws.amazon.com/es/blogs/architecture/disaster-recovery-dr-architecture-on-aws-part-ii-backup-and-restore-with-rapid-recovery/
  - III (Pilot Light y Warm Standby): https://aws.amazon.com/es/blogs/architecture/disaster-recovery-dr-architecture-on-aws-part-iii-pilot-light-and-warm-standby/
  - IV (Multi-site Active/Active): https://aws.amazon.com/es/blogs/architecture/disaster-recovery-dr-architecture-on-aws-part-iv-multi-site-active-active/
- Enaqx (s.f.). *Awesome pentest* [GitHub]. https://github.com/enaqx/awesome-pentest#tools
- Fowler (2014). *Circuit Breaker*. https://martinfowler.com/bliki/CircuitBreaker.html
- Hodgson (2017). *Feature toggles (aka feature flags)*. https://martinfowler.com/articles/feature-toggles.html
- Netflix Technology Blog (2019). *Tips for high availability*. https://netflixtechblog.medium.com/tips-for-high-availability-be0472f2599c
- OWASP (s.f.). *OWASP Top 10:2021*. https://owasp.org/Top10/
- SANS Institute (s.f.). *CWE Top 25 Most Dangerous Software Weaknesses*. https://www.sans.org/top25-software-errors/
- SAFECode (2018). *Fundamental practices for secure software development* (2nd ed.). https://safecode.org/uncategorized/fundamental-practices-secure-software-development/
- Schmitt (2024). *SAST vs. DAST: When to use them*. https://circleci.com/blog/sast-vs-dast-when-to-use-them/
- Sharma (2023). *From big bang to canary…* Medium/ByteByteGo. https://medium.com/bytebytego-system-design-alliance/from-big-bang-to-canary-exploring-software-deployment-strategies-for-a-flawless-release-with-3610e89ea789

### Referencias bibliográficas

- Len Bass, Paul Clements, Rick Kazman. *Software Architecture in Practice*, 4th ed. SEI / Addison-Wesley, 2022.
- Mark Richards, Neal Ford. *Fundamentals of Software Architecture: An Engineering Approach*. O'Reilly, 2020.
