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
latencia supuesta. **No hay corrida real todavía.** La lámina 12 es interna del equipo. El estilo visual reutiliza el
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
