---
name: consolidar-conocimiento
description: Use cuando haya que fusionar aportes de varios integrantes del equipo (apuntes, investigaciones, material oficial) en una nota consolidada única por módulo, conservando fuentes y registrando contradicciones. Invócala con /consolidar-conocimiento o cuando el usuario pida "consolidar", "unificar los aportes", "fusionar lo de Camilo con lo mío" o "notas consolidadas del módulo N".
---

# Consolidar conocimiento

Fusiona los aportes de varias personas en **una sola nota consolidada por módulo**, sin perder de
dónde vino cada cosa y sin borrar los desacuerdos.

## Qué NO es esto

No es resumir. Resumir comprime una fuente; consolidar **reconcilia varias fuentes que no
necesariamente coinciden**. Si al terminar no hay ninguna contradicción registrada y las fuentes
eran independientes, no consolidaste: copiaste la más larga.

## Entradas

Lee, en este orden de autoridad:

1. `Modulo N/Material-Clase/` — **fuente primaria**. Manda sobre todo lo demás.
2. `Modulo N/Aportes/*/` — aportes individuales. Lee también cada `FUENTES.md`.
3. `Modulo N/Notas/` — notas de encuentros sincrónicos.
4. `Modulo N/Ejercicios/` — evidencia medida, si existe. **Un dato medido gana a una estimación.**
5. `_Base-Conocimiento/` — lo ya consolidado de módulos anteriores, para no repetirlo.

## Procedimiento

1. **Inventario.** Lista cada fuente con autor, fecha, tipo y si fue generada con IA. Un documento
   generado con IA es `investigacion`, nunca `material-oficial`, aunque parezca oficial.
2. **Extracción.** De cada fuente, los conceptos con su afirmación literal. No parafrasees todavía.
3. **Alineación.** Agrupa los conceptos que hablan de lo mismo aunque usen nombres distintos.
4. **Detección de contradicciones.** Para cada grupo, ¿dicen todos lo mismo? Cuando no:
   - **Registra ambas versiones**, con quién dice cada una.
   - Resuelve por autoridad: material oficial > dato medido propio > fuente externa citada >
     afirmación sin fuente.
   - Si no se puede resolver, queda como **pregunta abierta**. No inventes el desempate.
5. **Clasificación.** Marca cada afirmación:
   - `[Curso]` lo dice el material del diplomado
   - `[Complementario]` conocimiento externo aportado
   - `[Recomendación]` criterio del equipo o del arquitecto
   - `[Hipótesis]` plausible pero sin verificar
6. **Deduplicación.** Si dos aportes dicen lo mismo, una sola entrada citando a los dos autores.
7. **Redacción** con `_Plantillas/PLANTILLA-consolidado.md`.
8. **Cosecha.** Identifica qué sube a `_Base-Conocimiento/Aprendizajes/` por ser transversal.
9. **Generar el HTML** (paso obligatorio, ver abajo).

## Salida — siempre dos archivos

| Archivo | Qué es |
|---|---|
| `Modulo N/Consolidado/mN-consolidado.md` | **La fuente de verdad.** Se edita aquí y solo aquí |
| `Modulo N/Consolidado/mN-consolidado.html` | La vista de lectura para el equipo. **Se genera, nunca se escribe a mano** |

El `.md` lleva todas las secciones de la plantilla. Obligatorias aunque queden cortas:
**contradicciones**, **preguntas abiertas** y **qué sube a Aprendizajes**.

### Generar el HTML

```bash
.claude/skills/consolidar-conocimiento/consolidar_html.py "Modulo N/Consolidado/mN-consolidado.md"
```

Sin dependencias: solo Python 3. Produce un documento con índice lateral, tablas legibles, tema
claro/oscuro automático, ancho de móvil y estilos de impresión — el mismo aspecto en todos los
módulos. Cualquiera del equipo puede regenerarlo sin IA.

**Por qué se genera y no se escribe:** si el `.md` y el `.html` se escribieran por separado,
divergirían. Una sola fuente de verdad, una sola verdad.

**Regenerar SIEMPRE que se toque el `.md`.** Un HTML desactualizado es peor que no tenerlo: el
equipo leería una versión que ya nadie mantiene.

### Subconjunto de Markdown soportado

Encabezados · tablas · listas (un nivel de anidación) · citas · bloques de código · separadores ·
`**negrita**` · `*cursiva*` · `` `código` `` · enlaces · y los marcadores `[Curso]`,
`[Complementario]`, `[Recomendación]` e `[Hipótesis]`, que se renderizan como etiqueta de color.

Fuera de esa lista el marcado sale como texto plano. Si un consolidado necesita algo más, se amplía
`consolidar_html.py` — no se parchea el HTML.

## Reglas duras

- **No inventar.** Si el material no dice algo, la respuesta es «no está en el material». Nunca una
  versión plausible.
- **No borrar desacuerdos.** Una contradicción entre el aporte de dos compañeros es información
  sobre el tema, no un error de formato.
- **Conservar la atribución.** Quien aportó un concepto queda nombrado en el consolidado.
- **El dato medido manda sobre la estimación**, venga de donde venga la estimación.
- **No editar los archivos de `Aportes/`.** El consolidado es un archivo nuevo.
- **No editar nunca el `.html` a mano.** Es un artefacto generado. Se corrige el `.md` y se regenera.
- Al terminar, actualizar `_Base-Conocimiento/INDICE.md` y el `README.md` del módulo.
