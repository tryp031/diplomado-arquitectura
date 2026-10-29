# Módulo 3 — Diseño de arquitecturas de software

**Ventana:** 21/10/2026 → 03/11/2026 (según `_Base-Conocimiento/CRONOGRAMA.md`; la página de la actividad no muestra fecha)
**Encuentros sincrónicos:** martes 27/10 y martes 03/11 (el segundo coincide con el cierre)
**Dedicación estimada (oficial):** 20 horas

## Objetivo (oficial)

Dominar técnicas para el **diseño, representación y evaluación** de arquitecturas: diagramación (UML, C4,
ArchiMate), **ADD**, estilos arquitectónicos (monolito, microservicios, eventos) y **análisis de riesgos**
(matriz, evaluación, lluvia de riesgos). Los decks complementarios suman ASR/QAW, evaluación (ATAM) y
registro de decisiones (ADR).

## Estado

| Sección | Estado |
|---|---|
| Contenidos obligatorios | ✅ 4 Genially transcritos 18/10 (`Material-Clase/Genially-Contenidos-Obligatorios.md`) |
| Autoevaluación M3 | ✅ presentada · 7 preguntas · cuadernillo de repaso en `Aportes/danny/m3-autoevaluacion-oficial-danny.html` (29/10) |
| **Actividad M3** | ✅ enunciado capturado 18/10 (`Material-Clase/Actividad-Reto3.md`) · **Reto 3: arquitectura resiliente con degradación en 3 niveles, solo AWS** · ✅ k6 del profesor en `Material-Clase/k6-script-profesor-reto3.js` |
| Conclusiones · Recursos complementarios | ✅ capturados como texto; 6 decks extraídos |

## Material oficial

- `Material-Clase/Modulo3-Brightspace.md`: páginas del módulo, conclusiones y lecturas.
- `Material-Clase/Actividad-Reto3.md`: enunciado del Reto 3 y transcripción de las 2 imágenes de resultados
  esperados (`Material-Clase/img/`). **Leer el bloque «Lo que el enunciado NO dice»**: las imágenes contradicen
  los umbrales del texto.
- `Material-Clase/k6-script-profesor-reto3.js`: **script de k6 oficial** del Reto 3, sin modificar (archivo del
  13/10, aportado por Danny el 18/10). 140 peticiones, 1 VU, 35 con `error: true`. Análisis en `Actividad-Reto3.md`.
- `Material-Clase/Discord-Aclaraciones-Docente.md`: **respuestas del docente en Discord #modulo-3** (18/10).
  Definen la regla que el enunciado deja abierta: **los errores del minuto anterior deciden el nivel del minuto
  actual**. Incluyen el diagrama de la sesión (0/5/10/5/0 errores → N1, N1, N2, N3, N2, N1). Está por encima de las
  imágenes de «Resultados esperados».
- Diseño del Reto 3 (borrador): `docs/superpowers/specs/2026-10-18-reto3-resiliencia-design.md`.
- `Material-Clase/Genially-Contenidos-Obligatorios.md`: Diagramación, ADD, Estilos de arquitectura y Análisis de riesgos.
- `Material-Clase/Tecnicas-{Diagramacion,DisenoADD,ASR-QAW,AnalisisRiesgos,Evaluacion,Decisiones}.md`: texto de
  los 6 decks, con las notas del orador.
- Los `.pptx` originales están en la misma carpeta **solo en local** (no se versionan, ~40 MB).

> **Falta conseguir:** la fecha de cierre real, la rúbrica
> completa (solo la demo muestra 2,5 pts) y si el envío es individual.
