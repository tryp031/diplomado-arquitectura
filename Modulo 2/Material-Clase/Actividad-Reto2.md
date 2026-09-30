# Actividad M2 — Reto 2: Sistema de alerta para flota vehicular

> **Tipo:** `material-oficial` (Brightspace → Módulo 2 → «Evidencia de aprendizaje: actividad M2»).
> **Fuente:** `Actividad-Reto2.pdf` (8 láminas, archivo original `Actividad - Reto 2 (1).pdf`), descargado 2026-09-30 con sesión de Danny.
> **Transcripción:** texto de las láminas tal cual; lo de las imágenes (láminas 7 y 8) está descrito abajo, marcado como `[imagen]`.
> **Este archivo no se edita.** Las observaciones propias van en `Aportes/`. El bloque «Lo que el enunciado NO dice» es anotación de Danny/IA, **no** del curso.

**Entrega en Brightspace:** carga de archivos (hasta 2 GB), audio o video. La fecha de cierre **no aparece** en la página capturada; el envío es individual.

---

## Contexto del reto

Estás a cargo del diseño e implementación de un sistema de alerta temprana para una flota vehicular. Cada vehículo envía constantemente su posición geográfica y su estado de operación a través de un endpoint. En situaciones críticas, como cuando el conductor presiona un botón de pánico o los sensores detectan una anomalía, se envía un evento de tipo `Emergency`.

Tu objetivo es garantizar que:

- Se reciban y procesen **1000 eventos** correctamente.
- Se envíe una alerta por correo electrónico a una cuenta Gmail específica **en el momento en que se reciba** un evento de tipo `Emergency`.
- Se cumplan las restricciones técnicas dadas (límite de peticiones, instancias máximas de procesadores, etc.).

### Objetivo

- Implementar una solución arquitectónica que permita recibir los eventos de los vehículos en tiempo real.
- Detectar eventos de emergencia en el flujo continuo de datos.
- Enviar una notificación por correo a la cuenta Gmail configurada **en menos de 30 segundos** desde la recepción del evento.

## Requerimientos funcionales

- **Recepción de eventos:** endpoint que pueda recibir **1000 solicitudes en 30 segundos**; el **100 %** de las solicitudes procesadas correctamente.
- **Detección de emergencias:** identificar eventos de tipo `Emergency` en el flujo continuo; registrar un log con la **fecha y hora exacta de la recepción**.
- **Notificación por correo:** enviar un correo a una cuenta Gmail configurada al detectar `Emergency`; registrar un log con la **fecha y hora del envío**.

## Requerimientos no funcionales

- **Tasa de peticiones:** si se usa API Gateway, tasa máxima **15 peticiones por segundo (rate)**. El valor de **burst puede quedar en su configuración predeterminada**.
- **Capacidad de procesamiento:** si se usan procesadores como Docker, Lambda, ALB, EC2, ECS, máximo **10 instancias activas simultáneamente**.
- **Logs:** registros claros con la hora exacta de (a) la recepción del evento `Emergency` y (b) el envío exitoso del correo.
- **Tiempo de entrega del correo:**
  - < 15 s → 2.5 puntos
  - entre 15 y 45 s → 1.5 puntos
  - > 45 s → 0.5 puntos
  - El tiempo se mide **entre el último envío realizado en k6 y la hora de envío del correo y recepción del mismo**.
- **Estándar del correo:** a una cuenta Gmail **personal** configurada por el estudiante; contenido claro, indicando que se recibió un evento `Emergency`.

## Entregables

1. **Código fuente:** toda la implementación para recibir eventos, detectar emergencias y enviar correos.
2. **Documentación técnica:**
   - **Decisiones de arquitectura:** justificar por qué se eligieron los componentes y servicios.
   - **Atributo de calidad más importante:** explicar cuál es y por qué fue priorizado.
   - **Diagrama de la arquitectura:** representación visual clara.
   - **Tácticas de arquitectura:** explicar las tácticas usadas para cumplir los objetivos.
3. **Logs de ejecución:** archivo o consola que muestre la recepción del `Emergency` y el envío exitoso del correo.
4. **Video de explicación** (para quienes **no** asisten al encuentro sincrónico): cómo se creó la arquitectura y todos los detalles del documento técnico e implementación. Quienes **sí** asisten deben **generar una presentación** detallando toda la implementación y mostrando **demo en vivo**.

## Escenario de pruebas

- Se **proporcionará** un script de k6 que envía 1000 peticiones en 30 segundos al endpoint configurado por el estudiante.
- El script simula vehículos que envían eventos `Position` y `Emergency`.
- El sistema debe detectar el `Emergency` y ejecutar la notificación.

## Restricciones

- No superar **15 peticiones por segundo** en el API Gateway.
- Los procesadores de peticiones (Lambda, Docker, ECS…) no pueden exceder **10 instancias simultáneas**.
- Usar una cuenta Gmail para la notificación.
- El envío de correos debe ser **consistente y medible**.

## Rúbrica (lámina titulada «Rúbrica de Presentación», 2.5 puntos)

| Criterio | Ponderación |
|---|---|
| Justificación de decisiones de arquitectura | 0.5 |
| Atributo de calidad más importante | 0.5 |
| Diagrama de arquitectura | 0.5 |
| Tácticas de arquitectura | 1.0 |
| **Subtotal documentación técnica** | **2.5** |
| Tiempo de entrega del correo (< 15 s) | 2.5 |
| Tiempo de entrega del correo (15–45 s) | 1.5 |
| Tiempo de entrega del correo (> 45 s) | 0.5 |
| **Subtotal «demostración en vivo»** | **2.5** (máximo) |

Total máximo aparente: **5.0 puntos**.

## Rúbrica M2 en Brightspace (segunda rúbrica oficial, capturada 2026-09-30)

Ficha de la asignación «Evidencia de aprendizaje: actividad M2», envío **individual** (`grpid=0`), sin fecha
de entrega visible en la página. Rúbrica de 5 criterios con 5 niveles (Excelente 5 · Bueno 4 · Aceptable 3 ·
Deficiente 2 · Insuficiente 1). Los **descriptores de cada celda vienen vacíos** en la página.

| Criterio |
|---|
| Diseño de la arquitectura |
| Implementación técnica y funcionalidad |
| Documentación técnica |
| Pruebas y análisis de resultados |
| Presentación y explicación |

Puntuación general: **Nivel 4 ≥ 11 pts · Nivel 3 ≥ 8 · Nivel 2 ≥ 5 · Nivel 1 ≥ 0**. *No coincide con la rúbrica del PDF de arriba
(2.5 + 2.5). Además, 5 criterios × 5 puntos suman 25, pero los umbrales llegan solo a 11: la escala es ambigua.
Ver «Lo que el enunciado NO dice».*

## Configuraciones solicitadas `[imagen]`

- **API Gateway, stage `prod`:** Rate **15**, Burst **2000**, cache cluster inactivo, method-level caching inactivo, sin Web ACL.
- **Payload de ejemplo:**

```json
{
  "type": "Position",
  "vehicle_plate": "ABC-123",
  "coordinates": { "latitude": 12.345, "longitude": 67.890 },
  "status": "OK"
}
```

- **Correo de ejemplo:** asunto «🚨 Alerta de Emergencia 🚨»; cuerpo con título «Alerta de Emergencia», `Placa: VFH-600`, `Estado: OK`, `Evento: Emergency`.
- **Salida esperada de k6:** 1 escenario, **10 VUs máx.**, 1000 iteraciones compartidas, `maxDuration 30s`; `checks 100.00% 1000 out of 1000` (`is status 200`); `http_req_failed 0.00%`; `http_reqs 1000 → 35.69/s`; duración de petición avg ≈ 176 ms, p(95) ≈ 272 ms; corrida de ≈ 28 s.

---

## Lo que el enunciado NO dice (anotación; no es del curso)

1. **Tensión 15 rps vs 35 rps.** 1000 peticiones en 30 s son ≈ 33–36 req/s (lo confirma la propia salida de k6: 35.69/s), más del doble del *rate* de 15. Lo que hace viable el «100 % procesado» es el **burst de 2000** (de la imagen), no el rate. Pero el texto dice que el burst «puede quedar en su configuración predeterminada» y la imagen muestra 2000: **no son equivalentes a simple vista**. **Verificar cuál es el valor por defecto real en la cuenta AWS de cada uno antes de diseñar** y no asumir.
2. **Dónde se mide el tiempo del correo.** «Último envío en k6» → «recepción del correo»: la medida incluye la entrega de Gmail, que el estudiante no controla. Además, el objetivo del enunciado es **< 30 s**, pero la rúbrica puntúa con cortes en **15 s y 45 s**; no hay un corte en 30.
3. **Rúbrica inconsistente.** La lámina se titula «Reto 1» y llama «Demostración en vivo» al subtotal de tiempo de correo (los tres renglones de tiempo son excluyentes, no suman).
4. **El k6 «se proporcionará»**: no lo tenemos. Conseguirlo antes de medir.
5. **No se dice** la fecha de cierre ni el peso de la actividad en la nota. El envío aparece como **individual** (`grpid=0`).
   La ventana del módulo termina el 20/10, pero la hora de cierre no consta.
6. **El atributo «más importante» es entregable explícito (0.5 pts)**: es exactamente el hilo conductor que el profesor echó de menos en M1.
7. **Sesgo AWS:** todo el enunciado asume AWS (API Gateway, Lambda, ECS, ALB). El diplomado declara sesgo AWS-first; no dice si se admite otra nube.
