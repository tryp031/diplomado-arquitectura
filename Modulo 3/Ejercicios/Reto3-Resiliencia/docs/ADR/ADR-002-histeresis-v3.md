# ADR-002 — v3: degradar por el «minuto» del k6 y recuperar con histéresis

- **Estado:** **Aceptada, 30/10/2026.** El equipo (Freddy, Camilo y Danny) eligió la v3 como versión oficial.
  **Reemplaza a ADR-001** (permanencia de 2 min), que queda como histórico y se puede desplegar con `Modo=reloj`.
- **Fecha:** 2026-10-27 (propuesta) · 2026-10-30 (aceptada) · **Autor:** Danny (con IA)

## Contexto

- El k6 oficial manda **5 / 0 / 15 / 0 / 15 / 0 / 0** errores por «minuto» (140 iteraciones, `floor(i/20)+1`).
- El diagrama de la sesión del docente supone **0 / 5 / 10 / 5 / 0** y da 1-1-2-3-2-1. Con el script, la regla
  pura «el minuto anterior decide» da **1-2-1-3-1-3-1**, sin importar cómo se guarden los errores ni la latencia
  (simulado con 0, 5 y 50 ms).
- **1-1-2-3-2-1 exacto es imposible con el script:** el sistema llega al minuto 4 y al minuto 6 en el mismo
  estado (N2, minuto anterior con 15 errores, el de antes con 0). El diagrama exige N3 en uno y N1 en el otro.
- La v1 (minuto de reloj + permanencia de 2 min) termina en N1 solo si el k6 se desborda al minuto 8 por la
  latencia (riesgo R1). Con latencia ≈ 0 termina en N2.

## Decisión

1. **Ventana = «minuto» del k6:** bloques de 20 peticiones numeradas en DynamoDB, no el reloj. La latencia deja
   de mover las ventanas.
2. **Degradar con la regla del docente:** al abrir un bloque, los errores del bloque anterior deciden
   (≥ 5 → N2, ≥ 10 → N3). Se puede saltar de nivel de inmediato.
3. **Recuperar con histéresis, de a un nivel:** de N3 a N2 tras **30** peticiones seguidas sin error («indicadores
   saludables» del enunciado); de N2 a N1 tras **40** («completamente estables»).
4. **Corrida nueva:** tras 15 s sin tráfico, el estado vuelve a N1.

## Implementación

- `src/histeresis.py`: la regla, como funciones puras (`entrar` numera la petición y decide su nivel; `registrar` cuenta
  el resultado).
- `src/router.py`: modo `histeresis`, **el valor por defecto** de `MODO` en el código y del parámetro `Modo` en
  `template.yaml`. Un `MODO` desconocido hace fallar al router al arrancar, a propósito (responde N3 y registra
  `FALLA_ROUTER`).
- `src/estado.py`: un solo ítem `pk = V3` en la misma tabla (`seq`, `nivel`, `errores_bloque`, `racha`, `ultimo`,
  `version`, `ttl`), con bloqueo optimista por `version` y hasta 5 reintentos. **No hay migración.** El router
  necesita `dynamodb:GetItem` y `dynamodb:UpdateItem`.
- Observabilidad: `CAMBIO_NIVEL` con `peticion`, `minuto_k6`, `racha_sin_error` y los umbrales; evento nuevo
  `CORRIDA_NUEVA`; cada `PETICION` lleva su número y su `minuto_k6`.

## Resultado con el k6 oficial

- **Por minuto del k6:** 1, 2, 2, 3, 3, 3, y en el 7 baja de 3 a 2 a 1.
- **Transiciones:** 1 → 2 → 3 → 2 → 1.
- **Cambios en las iteraciones:** 21, 61, 126 y 136.
- Termina en N1 y aparecen los dos mensajes de N3 del enunciado.
- Verificado en tests (`test_histeresis.py`, `test_router_histeresis.py`) y en LocalStack: el 27/10 (k6 manual,
  `logs/k6-local-v3-20261028T011300Z.log`) y el 30/10 (140 peticiones con el despliegue por defecto, sin pasar `Modo`).

## Consecuencias

- **+** Cumple el enunciado: los 3 niveles, recuperación gradual y recuperación completa al final.
- **+** Nunca salta de 3 a 1 y es determinista frente a la latencia.
- **−** Los umbrales 30/40 se calibraron con el script. Margen de **5 peticiones** en cada comparación crítica:
  35 < 40, 25 < 30 y 45 ≥ 40. Hay que declararlo, no presentarlo como algo que sale solo.
- **−** Con poco tráfico, una ventana por número de peticiones puede durar horas. En producción sería
  «20 peticiones o 60 s, lo que ocurra primero».
- **−** No reproduce el diagrama de la sesión. Ninguna regla puede reproducir a la vez el diagrama y el script.
- **−** N2 dura solo 10 peticiones al recuperarse (126 → 136): la racha no se reinicia al subir a N2. Si se
  reiniciara, la corrida no terminaría en N1 dentro de las 140 iteraciones. Es un compromiso de diseño, no un bug.
- **−** El reinicio a los 15 s sin tráfico es una regla nuestra: el enunciado no la pide. Existe para repetir el k6.
- **−** Estado en un solo ítem con versión optimista: suficiente para 1 VU; con alta concurrencia, ese ítem es un
  punto caliente.
