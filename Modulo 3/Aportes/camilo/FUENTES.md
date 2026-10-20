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
- Las figuras no incluyen un calentador de Lambdas (como el de EventBridge del Reto 2), porque no hace falta
  en este reto:
  - **La carga mantiene calientes las funciones.** El k6 manda una petición cada 3 s durante 7 minutos; ninguna
    Lambda queda inactiva el tiempo suficiente para enfriarse. El arranque en frío solo afecta a la primera
    petición y a la primera vez que se usa el Nivel 2 y el Nivel 3.
  - **Lo que se evalúa no es la latencia de una petición.** En el Reto 2 el calentador se justificaba por el
    corte de 15 s del correo. Aquí la prueba mide la secuencia de niveles; un arranque en frío no cambia los
    errores contados ni el nivel de ningún minuto.
  - **Un calentador interferiría con el estado.** Si pasara por el router, entraría al conteo de peticiones y
    podría fijar el nivel de un minuto. Evitarlo exige modificar `router.py` para ignorar esos eventos: más
    complejidad que beneficio.
  - **El riesgo real es acotado y se cubre a mano.** El router tiene timeouts cortos (1 s hacia DynamoDB y 3 s
    hacia las Lambdas de nivel, un solo intento); si la primera petición los supera, responde como Nivel 3
    sin contarse. Se evita calentando 2 minutos antes de la corrida con unas pocas peticiones sin error y una
    prueba directa de los Niveles 2 y 3.
  - **Es un análisis, no una medición.** Se confirma en la primera corrida en AWS real, revisando la duración
    de inicio en los logs y la primera línea del k6. Si falla, se reevalúa (subir los timeouts o agregar un
    calentador que no pase por el conteo).
