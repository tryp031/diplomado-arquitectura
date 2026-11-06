# Reto 3 — Logs y métricas de ejecución · Group 2

Tres corridas del **k6 oficial** contra la solución desplegada en **AWS (us-east-2)**, con el mismo código
(`CodeSha256 Gq+DEPQOikPl9sW2XowRlIdEN8XHeXB+ek+uRyXHlqA=` en las 4 Lambdas). En las tres, el único
cambio al script del profesor es la URL (línea 57); cada carpeta trae el `diff` que lo demuestra.
Los logs están **tal como los produjo k6 o CloudWatch**, sin editar.

## Resultado

| Corrida | Peticiones | Errores (pedidos por el script) | Secuencia de niveles | Cambios de nivel en las peticiones | Latencia media / p95 |
|---|---|---|---|---|---|
| 1 · 02/11, 12:32 COT (la del documento técnico) | 140 / 140 | 35 (25 %) | **1 → 2 → 3 → 2 → 1** | 21, 61, 126, 136 | 167 ms / 182 ms |
| 2 · 03/11, 18:11 COT (demo, desde el panel) | 140 / 140 | 35 (25 %) | **1 → 2 → 3 → 2 → 1** | 21, 61, 126, 136 | 175 ms / 194 ms |
| 3 · 03/11, ≈ 19:20 COT (k6 a mano en la terminal) | 140 / 140 | 35 (25 %) | **1 → 2 → 3 → 2 → 1** | 21, 61, 126, 136 | 210 ms / 358 ms |

Las 35 respuestas con error son las que pide el propio script (`error: true` en los minutos 1, 3 y 5:
5, 15 y 15). No hubo ninguna falla inesperada. Las tres corridas terminan en «Nivel 1: OK».

## Cómo leer cada carpeta

### `1-corrida-informe-aws-20261102/` — la corrida que analiza el documento técnico (sección 11)
- `…-k6.log`: salida completa del k6. Cada línea dice minuto, iteración, si llevaba error, código HTTP y
  mensaje del nivel que respondió.
- `…-servidor.jsonl`: los logs de CloudWatch de las 4 Lambdas en la ventana de la corrida. Cada `PETICION`
  trae su número y su «minuto del k6»; los 4 eventos `CAMBIO_NIVEL` traen nivel de origen, destino,
  motivo y errores del bloque anterior o racha sin error.
- `…-k6-diff.txt`: el script usado frente al oficial: solo cambia la URL.

La coherencia cliente = servidor = regla de esta corrida (7 de 7 «minutos» del k6) se puede reproducir con
la prueba `test_coherencia_con_una_corrida_real_en_aws` del paquete de código, que lee estos dos archivos.

### `2-corrida-demo-panel-aws-20261103/` — exportada por el panel de control
Los mismos tres archivos, más:
- `…-minutos.csv`: por cada «minuto» del k6 (bloques de 20 peticiones), los errores y el nivel según el
  cliente (k6), el servidor (CloudWatch) y la regla. **Coinciden en los 7.** En el minuto 7 el nivel baja
  3 → 2 → 1 dentro del mismo bloque: las rachas sin error se cumplen en las peticiones 126 y 136.
- `…-resumen.json`: veredicto de la corrida (recorrió los 3 niveles, terminó en N1, sin saltos, secuencia
  1-2-3-2-1) y los parámetros de la regla (bloques de 20, umbrales 5/10, rachas 30/40).

### `3-corrida-manual-aws-20261103/` — el script oficial corrido a mano
- `k6-manual-aws-20261103-1928COT.log`: la salida de `k6 run k6-reto3-aws.js`. k6 no imprime la fecha;
  la hora del nombre es la del archivo guardado al terminar (19:28 COT).
- `k6-reto3-aws.js` y `k6-diff.txt`: el script usado y su diferencia con el oficial (solo la URL).

Sirve para mostrar que el resultado no depende de nuestro panel ni de nuestros scripts.
