# Equipo de trabajo — Group 2

> Fuente: Brightspace, «Miembros del grupo: Group 2». Actualizado: **2026-09-14**.

## Composición efectiva — 3 integrantes

En la reunión del **13/09** el equipo confirmó que **Bryan Andrés Brack Perilla no
participará** en el trabajo. El reparto y el plan se rehicieron para tres personas.

| Estudiante | Rol en el reto M1 | Variante | Estado |
|---|---|---|---|
| **Aparicio Marín, Freddy Erney** | Implementación | **A — HTTP/1.1 REST**, puerto 9100 | ⬜ pendiente |
| **Céspedes Leguizamón, Camilo Andrés** | Implementación | **C — Unix domain socket**, puerto 9102 | ⬜ pendiente |
| **Mazo Serna, Daniel** (Danny) | Arquitectura · harness · informe | **D — memoria compartida** + controles Bc y dominio + línea base E | ✅ medidas |
| ~~Brack Perilla, Bryan Andrés~~ | — | — | fuera del trabajo (13/09) |

### Consecuencias del cambio a 3

- **La variante C es la prescindible.** Ya estaba previsto en el registro de riesgos del
  `PLAN-EQUIPO.md`: con B, Bc, D y E medidas, el estudio se sostiene sin C.
- **La variante A no lo es.** Es el extremo superior del rango y lo que construiría
  cualquier equipo por defecto. Sin A no se puede afirmar «la opción simple ya cumple el
  umbral», que es la conclusión principal del informe.
- Daniel absorbe el trabajo transversal (harness, ADR, informe, video), que no se divide.

## ⚠️ Ambigüedad pendiente de confirmar

El diplomado asigna grupos en Brightspace, **pero el enunciado de la actividad M1 está
redactado en términos individuales**:

- *«Estimado estudiante, a continuación se presentan los pasos…»*
- *«**Cada estudiante** elegirá herramientas, lenguajes o metodologías para minimizar la latencia.»*
- *«Para aquellos **estudiantes** que no pueden asistir al encuentro sincrónico…»*

No hay en el material del Módulo 1 ninguna mención a entrega grupal. Las dos lecturas:

1. La entrega del reto es **una por grupo** (y el enunciado no se actualizó al pasar a
   modalidad grupal).
2. La entrega es **individual** y el grupo existe para foros, discusión o el proyecto final.

**Acción:** preguntar a la facilitadora (`lineadiplomadovirt1@javerianacali.edu.co`) o al
docente en el encuentro del **15/09**. El plan funciona en ambos escenarios: si la entrega
es individual, cada uno entrega el trabajo completo citando su variante como aporte propio.

## Referencias

- Plan de trabajo del reto: `Modulo 1/Ejercicios/Reto-Latencia-Minima/PLAN-EQUIPO.md`
- Contrato para implementar una variante: `.../harness/README.md`
- Decisión del dominio (13–14/09): `ADR/ADR-004-dominio-listas-de-hosts.md`
