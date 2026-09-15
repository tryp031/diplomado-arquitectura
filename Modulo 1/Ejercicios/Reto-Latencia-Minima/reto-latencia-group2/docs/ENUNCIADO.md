# Actividad M1 — Reto de Latencia Mínima

> Transcripción literal del enunciado. Fuente: `../../Material-Clase/Modulo1-ArquitecturaSoftware.md`,
> sección 4 "Evidencia de aprendizaje: actividad M1". **Fecha límite: 29/09/2026** (cierre del módulo;
> después de esa fecha no se califica — Art. 5 de los lineamientos).

## Reto

Diseña y construye un sistema en el que, ante un estímulo (por ejemplo, un mensaje cualquiera),
el sistema responda con otro mensaje (por ejemplo, "respuesta") en el menor tiempo posible.
El desafío es lograr una latencia (tiempo entre enviar y recibir respuesta) mínima,
**preferiblemente menor a un milisegundo**.

## Objetivo

Demostrar la capacidad de diseñar, implementar y optimizar una arquitectura de software enfocada
en reducir drásticamente la latencia de comunicación. La idea es que, una vez desplegado el
sistema, se lance un "estímulo" y se obtenga la respuesta casi de inmediato.

## Requisitos básicos

- El sistema debe **escuchar permanentemente** peticiones o estímulos.
- Al recibir el estímulo, el sistema debe **retornar una respuesta específica**.
- Debe **medirse el tiempo transcurrido** desde el envío del estímulo hasta la recepción de la respuesta.

## Restricciones

- No se otorgarán pistas ni guías sobre cómo implementar la solución.
- Cada estudiante elige herramientas, lenguajes o metodologías para minimizar la latencia.
- No se discutirán pasos ni configuraciones específicas en clase; **la investigación es parte del reto**.

## Entregables

1. **Código fuente** — archivo **ZIP** con la implementación completa del sistema que escucha
   peticiones y responde con la menor latencia posible.
2. **Documentación técnica** — **PDF** con:
   - Descripción detallada de la arquitectura del sistema.
   - Justificación de herramientas, lenguajes y metodologías elegidas para minimizar la latencia.
   - Explicación de cómo se mide la latencia y los resultados obtenidos.
3. **Logs de ejecución** — `.txt` / `.log` o capturas `.png` / `.jpg` con los registros del tiempo
   transcurrido entre envío del estímulo y recepción de la respuesta.
4. **Informe de resultados** — PDF (puede fusionarse con el anterior) con:
   - Análisis de los resultados: latencia medida y optimizaciones realizadas.
   - **Comparación explícita con el objetivo de 1 ms.**
5. **Video de explicación** — MP4 (máx. **5 minutos**) o enlace a YouTube.
   - Quien **no** asista al encuentro sincrónico: video explicando arquitectura, implementación y resultados.
   - Quien **sí** asista: **demostración en vivo** del sistema respondiendo a estímulos.

## Checklist de entrega

- [ ] Código fuente comprimido en ZIP
- [ ] Documentación técnica en PDF (arquitectura + justificación + método de medición)
- [ ] Logs de ejecución
- [ ] Informe de resultados con comparación contra 1 ms
- [ ] Video MP4 ≤ 5 min **o** demo en vivo el 15/09 o el 29/09
- [ ] Autoevaluación M1 enviada (1 solo intento permitido)
