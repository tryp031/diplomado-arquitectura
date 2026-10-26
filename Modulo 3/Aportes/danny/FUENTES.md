# Aportes de Danny: Módulo 3

> Ficha de origen. Se llena **al recibir** el aporte, no después.

## `m3-presentacion-reto3-danny.html`

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny), con IA |
| **Fecha** | 2026-10-18 |
| **Módulo** | 3. Diseño de arquitecturas de software |
| **Tema** | Borrador de la presentación del Reto 3 con las pautas de Danny: decisiones, restricciones, atributos de calidad priorizados, tácticas y arquitectura |
| **Tipo** | `investigacion`. Diseño propio, **no es material oficial** |
| **Fuentes** | `Material-Clase/Actividad-Reto3.md` · `k6-script-profesor-reto3.js` · `Material-Clase/Discord-Aclaraciones-Docente.md` · `Modulo 2/Material-Clase/Tacticas-Disponibilidad.md` · spec `docs/superpowers/specs/2026-10-18-reto3-resiliencia-design.md` |
| **Estado** | borrador · ⬜ sin consolidar |

**Límites:** la línea de tiempo (lámina 10) es **simulada**: sale de la reproducción del k6 en los tests, con 0,2 s de
latencia supuesta. **No hay corrida real todavía.**

**Actualización 2026-10-26 (v2).** La regla pasa a la permanencia de 2 min (ADR-001). La lámina 10 ahora es la corrida
**medida en LocalStack** (23/10, 1-2-3-2-1). Se suma una lámina con lo medido en AWS, tomada del informe de avance de
Camilo (PR #58; corridas de prueba con la regla anterior). Falta reemplazar la línea de tiempo por la corrida oficial en AWS. La lámina 12 es interna del equipo. El estilo visual reutiliza el
del deck del Reto 2 (`Modulo 2/Entregables/presentacion-reto2-v6.html`).

---

## `m3-guia-aws-camilo-danny.md`

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny), con IA |
| **Fecha** | 2026-10-18 |
| **Módulo** | 3 |
| **Tema** | Paso a paso para que Camilo cree un usuario IAM de despliegue con mínimo privilegio (`reto3-*`, us-east-2) |
| **Tipo** | `investigacion`. Procedimiento propio |
| **Fuentes** | Conocimiento general de IAM, CloudFormation y SAM **[Complementario]**. **No se probó en la cuenta** |
| **Estado** | vigente · pendiente de que Camilo lo ejecute |

**Límites:** la política no se validó contra una cuenta real. Si un despliegue falla por `AccessDenied`, el mensaje
de CloudFormation indica la acción que falta, y se agrega con el mismo prefijo.

---

## `m3-guion-video-reto3-danny.md`

| Campo | Valor |
|---|---|
| **Autor** | Daniel Mazo Serna (Danny), con IA |
| **Fecha** | 2026-10-26 |
| **Módulo** | 3 |
| **Tema** | Guion del video del Reto 3 (máximo 5 min): checklist previo, reparto por persona y minuto, y qué cambia si el docente ajusta la regla el 27/10 |
| **Tipo** | `investigacion`. Propuesta propia; el reparto se acuerda en el equipo |
| **Fuentes** | Enunciado del Reto 3 (video ≤ 5 min) · ADR-001 · corrida en LocalStack del 23/10 (la narración por minuto sale de ahí) · informe de avance de Camilo |
| **Estado** | borrador · depende de la corrida oficial en AWS |

**Límites:** la narración por minuto supone que AWS reproduce la secuencia de LocalStack (1-2-3-2-1). Si la corrida oficial
da otra cosa, se reescribe esa fila.
