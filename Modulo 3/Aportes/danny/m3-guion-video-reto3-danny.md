# Guion del video — Reto 3 (máximo 5 minutos)

> **Autor:** Danny (Group 2), con asistencia de IA · **Fecha:** 2026-10-26 · **Tipo:** `investigacion` (borrador)
> **Estado:** borrador. Depende de la corrida oficial en AWS (después del redespliegue con `PERMANENCIA_MINUTOS=2`).
> **Quién habla:** es una propuesta; se acuerda en el equipo.

## Regla del video

El k6 dura unos **7 min 24 s** y el video, **5 como máximo**. No cabe en vivo. Se graba la corrida completa y se
**edita**: se muestra el arranque, se acelera la parte central (×4) y se vuelve a velocidad normal en los cambios de
nivel y al final. Se dice en voz alta que el video está acelerado, para no dar la impresión de ocultar algo.

## Antes de grabar (checklist)

1. `AWS_PROFILE=reto3-panel-lectura scripts/verificar-aws.sh` → «listo». Si falla, **no se graba**.
2. Calentar las 4 Lambdas (una prueba por nivel en la consola y 3 o 4 peticiones sin error). Esperar a que empiece un
   minuto nuevo, para que el calentamiento no cuente errores en el minuto de la corrida.
3. `PANEL_AWS_PERFIL=reto3-panel-lectura scripts/panel.sh` → http://localhost:8030 en el switch **AWS**.
4. Grabar la pantalla con el panel y una terminal visibles. La consola de CloudWatch, en otra pestaña.

## Guion

| Tiempo | Quién | En pantalla | Qué se dice |
|---|---|---|---|
| 0:00–0:30 | Danny | Deck, lámina 2 | «Priorizamos la **disponibilidad**: responder siempre, aunque sea con menos. A costa de capacidades en los niveles 2 y 3, de unos 40 ms por el router y de reaccionar al minuto siguiente y no al instante.» |
| 0:30–1:15 | Danny | Deck, láminas 8 y 4 | Arquitectura: API Gateway → router → tres Lambdas, estado en DynamoDB y CloudWatch. La regla: los errores del minuto anterior deciden el nivel (lo dijo el docente); se degrada de golpe, **se sostiene 2 minutos** y se recupera de a un nivel (decisión nuestra, ADR-001). |
| 1:15–1:35 | Camilo | Terminal | `diff` del script: la única línea distinta es la URL. Arranca el k6 desde el panel. |
| 1:35–3:45 | Camilo / Freddy | Panel (×4 entre cambios) | Narrar cada cambio de nivel a velocidad normal: min 1 → N2 (5 errores); min 3 → N3 (por los 15 errores del min 2); min 4 sigue en N3 y aparece «Sistema bajo mantenimiento»; min 6 → N2; min 7 → N1. Señalar la coherencia servidor = cliente. |
| 3:45–4:15 | Freddy | CloudWatch Logs Insights | Los eventos `CAMBIO_NIVEL` con el minuto, el nivel de origen y de destino, el motivo y los errores. «Cada cambio queda registrado, como pide el enunciado.» |
| 4:15–4:45 | Camilo | Resumen del k6 + panel | 140/140 iteraciones, 35 fallidas = las que pide el script, ninguna inesperada. Secuencia **1-2-3-2-1**, termina en Nivel 1. Descargar el ZIP de evidencia. |
| 4:45–5:00 | Danny | Deck, lámina de cierre | Compromisos declarados: la permanencia se aparta del diagrama de la sesión en una ventana y es reversible con un parámetro; el contador de un ítem por minuto no escala a 10×. |

## Qué NO va en el video

- La explicación de LocalStack ni del panel en modo local: es contexto del ZIP, no de la demo.
- Las corridas de prueba del 21 y 22/10 (regla anterior). Si alguien pregunta, están en `logs/` y en el ADR-001.

## Si el docente cambia algo el 27/10

- **Rechaza la permanencia:** `PERMANENCIA_MINUTOS=1` en el router, volver a correr `verificar-aws.sh` con
  `PERMANENCIA_ESPERADA=1`, y el guion cambia la secuencia a 1-2-1-3-2-3-2-1 y explica la recuperación escalonada.
- **Pide que el ruteo ocurra en API Gateway:** no se resuelve en el video. Se discute en el equipo antes de grabar.
