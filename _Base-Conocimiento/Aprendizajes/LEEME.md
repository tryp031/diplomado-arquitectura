# Aprendizajes reutilizables

Lo que sale de un módulo cerrado y **sirve para los siguientes**. No es un resumen del módulo —
eso vive en `Modulo N/Consolidado/`. Aquí solo entra lo transversal.

Un aprendizaje entra si responde que sí a: *¿esto lo voy a volver a necesitar en otro módulo,
en el proyecto final o en el trabajo real?*

## Formato

Un archivo por aprendizaje: `<tema>.md`

```markdown
# Título del aprendizaje

**Origen:** Módulo N · <de qué trabajo salió> · fecha
**Tipo:** método · patrón · herramienta · error a evitar

## Qué aprendimos
## Cómo se aplica
## Cuándo NO aplica
## Evidencia
```

## Índice

*(vacío — se llena al cerrar el Módulo 1, el 29/09)*

### Candidatos ya identificados del Módulo 1

Estos salieron del reto de latencia y son claramente transversales. Se escriben al cerrar el módulo:

1. **Un atributo de calidad que no se mide es un deseo.** Cómo convertir «debe ser rápido» en
   «p99.9 < 1 ms, payload 32 B, closed-loop, en loopback». Aplica a cualquier requisito no funcional.
2. **La media miente; reporta percentiles.** Medido: media 13,45 µs contra máximo 2 202 µs — un
   factor de 163. Aplica a toda medición de rendimiento.
3. **Congelar la especificación de medición antes de implementar.** Si cada uno mide distinto, el
   estudio comparativo no vale nada. Aplica a cualquier benchmark entre alternativas.
4. **El sistema operativo es una restricción arquitectónica, no un detalle.** Verificado:
   `thread_policy_set` devuelve `KERN_NOT_SUPPORTED` en macOS/arm64; `CLOCK_MONOTONIC` avanza a
   saltos de 1 µs. La plataforma acota lo que la arquitectura puede prometer.
5. **Separar plano de control y plano de datos.** La interfaz que enciende y observa el sistema no
   puede estar en la ruta que se mide. Aplica a observabilidad en general.
6. **La opción que gana el benchmark suele ser la que no desplegarías.** Memoria compartida gana
   por 6 órdenes de magnitud y sería la peor decisión en producción. La primera ley, medida.
