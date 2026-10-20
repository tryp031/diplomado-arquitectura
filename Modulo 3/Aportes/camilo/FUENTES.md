# Aportes de Camilo — Módulo 3

> Ficha de origen. Se llena **al recibir** el aporte, no después.

## `diagrama-contenedores-reto3.html`

| Campo | Valor |
|---|---|
| **Autor** | Camilo Andrés Céspedes Leguizamón, con asistencia de IA |
| **Fecha de recepción** | 2026-10-19 |
| **Módulo** | 3 — Reto 3: Diseñando Arquitecturas Resilientes |
| **Tema** | Diagramas de la propuesta de Danny: vista general (zoom-out) y detalle de AWS, con el «qué hace» de cada pieza |
| **Tipo** | `investigacion` — representación visual de un diseño ajeno (el de Danny); **no es material oficial** |
| **Fuentes** | `docs/superpowers/specs/2026-10-18-reto3-resiliencia-design.md` · `Modulo 3/Ejercicios/Reto3-Resiliencia/` (`template.yaml`, `src/`, README) · `Modulo 3/Aportes/danny/FUENTES.md` |
| **Estado** | borrador · ⬜ sin consolidar |

**Qué contiene:** una página con dos figuras en SVG. La primera es la vista general: el panel de control
(k6 oficial y panel de estado) frente a AWS, con DynamoDB y CloudWatch dentro del plano de AWS. La segunda
es el detalle de AWS: API Gateway, Lambda router, las tres Lambdas de nivel, DynamoDB y CloudWatch, con el
«qué hace» bajo cada caja y una leyenda de estado.

**Límites:**
- Dibuja el diseño de Danny; no lo modifica ni lo valida. Si el diseño cambia (por ejemplo, tras el encuentro
  del 27/10), hay que actualizar los diagramas.
- El color indica el estado de validación: **verde** = validado con el k6 oficial en **LocalStack**;
  **ámbar** = pendiente de confirmar en AWS real (métricas EMF y dashboard); **gris** = actor externo.
  Todavía **no hay corrida en AWS real**.
- Las figuras no incluyen un calentador de Lambdas: se decidió no agregarlo y calentar a mano antes de la
  corrida.
