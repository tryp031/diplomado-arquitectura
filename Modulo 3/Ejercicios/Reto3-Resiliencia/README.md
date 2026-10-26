# Reto 3: arquitectura resiliente (Group 2)

API Gateway → `reto3-router` → `reto3-nivel{1,2,3}`, con el estado en DynamoDB. **El nivel de cada minuto de reloj se
decide con los errores del minuto anterior**: ≥ 10 → N3 y ≥ 5 → N2. Se degrada de inmediato. Tras degradar, el nivel
se sostiene **2 minutos** y luego se recupera de a un nivel por minuto (`docs/ADR/ADR-001`, 22/10). Con el k6 oficial
la secuencia es **1-2-3-2-1**. Diseño completo: `docs/superpowers/specs/2026-10-18-reto3-resiliencia-design.md`.

## Pruebas (sin AWS)
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest            # incluye la reproducción de las 140 iteraciones del k6 oficial
```

## LocalStack
```bash
docker compose -f localstack/docker-compose.yml up -d
scripts/deploy.sh localstack
scripts/correr-k6.sh localstack
```
LocalStack **no valida** IAM, cold starts, latencias reales ni el dashboard.

Hallazgos al montarlo (18/10), ya resueltos en `deploy.sh` y `template.yaml`:
- `--endpoint-url` **no basta**. `cloudformation package` sube a S3 con su propio cliente, e intentó ir a AWS real (con
  llaves falsas, sin efecto). Se usa `AWS_ENDPOINT_URL`, que aplica a todos los servicios.
- El AWS CLI 2.2x manda un checksum que LocalStack 3.8 rechaza: `AWS_REQUEST_CHECKSUM_CALCULATION=when_required`.
- `package` **no resuelve el `CodeUri` de `Globals`**: empaquetaba la carpeta entera (27 MB, con `.venv`). El `CodeUri`
  va en cada función.
- Latencia medida en caliente: unos 40 ms por petición. El umbral del riesgo R1 es de unos **25 ms**: por debajo, la
  prueba termina en N2.

## AWS (cuenta del equipo, us-east-2)
```bash
AWS_PROFILE=diplomado CUENTA_ESPERADA=<id> scripts/deploy.sh aws
scripts/correr-k6.sh aws
```
El script aborta si el perfil no es `diplomado` o si la cuenta no coincide. **Nunca** despliegues con `default`.

## Panel de control
```bash
scripts/panel.sh                                      # http://localhost:8030, contra LocalStack
PANEL_AWS_PERFIL=<perfil-solo-lectura> scripts/panel.sh  # AWS con lectura del servidor
```
- **AWS sin perfil = modo «solo cliente».** Con la URL en `.build/url-aws.txt`, el panel corre el k6 y las peticiones
  manuales, y verifica la regla con los errores que ve el propio k6. Si el perfil no tiene permisos (AccessDenied),
  pasa lo mismo y el panel lo dice en un aviso, no como un error.
- **Guion del script**: los 7 minutos del k6 (5/0/15/0/15/0/0 errores), el nivel que predice la regla y el que
  respondió el sistema, minuto a minuto.
- **Gráfica por minuto de reloj**: el nivel del servidor, el de la regla y el del cliente, y debajo los errores con los
  umbrales. Tiene tooltip y una vista de tabla.
- **Nivel del minuto actual**, leído del servidor (DynamoDB): errores del minuto anterior y del actual, y la cuenta
  regresiva hasta la próxima evaluación.
- **▶ Correr k6 oficial**: la misma garantía que `correr-k6.sh`. Copia el script con la URL cambiada, verifica que
  sea la única línea distinta y guarda la salida cruda en `logs/k6-<entorno>-<sello>.log`.
- **Línea de tiempo por minuto**: el nivel que fijó el servidor frente al que vio el k6, con ✓/✗ de coherencia. Es lo
  que muestra que el panel no inventa nada.
- **Cambios de nivel**: los eventos `CAMBIO_NIVEL` y las fallas, leídos de CloudWatch Logs.
- **Prueba manual**: peticiones OK o con error por la misma puerta que el k6. Sirve para mostrar «Nivel 3: Sistema
  bajo mantenimiento», que el script oficial nunca produce.
- **Descargas**: un ZIP con el log del k6, los logs de CloudWatch (JSONL), los minutos (CSV), el resumen (JSON) y el
  diff del script.
- **Reiniciar estado**: solo en LocalStack. En AWS, el panel es de solo lectura.

El panel **observa, no mide**: la evidencia sigue siendo el log del k6 y los logs de CloudWatch. **Si se redespliega,
primero hay que descargar la evidencia**, porque en LocalStack el redespliegue puede recrear los grupos de logs.

## Qué cambia en el k6 oficial
Solo la URL. `correr-k6.sh` lo verifica con `diff` y guarda el diff en `.build/`.

## Corridas del 22/10/2026 (permanencia de 2 min, ADR-001)

| Entorno | Regla desplegada | Secuencia | Evidencia |
|---|---|---|---|
| LocalStack | permanencia 2 | **1-2-3-2-1**: 8/8 minutos con cliente = servidor = regla, 15 respuestas 503 «mantenimiento» | `logs/evidencia-local-20261023T010346Z/` |
| AWS (Camilo) | la anterior | 1-2-1-3-2-3-2-1, latencia media de 178 ms | `logs/k6-aws-20261023T010353Z.log` |

AWS **hay que redesplegarlo** con este código. El usuario `user-boto3-solo-lectura` del Reto 2 no tiene la política
`Reto3-PanelLectura` (AccessDenied en DynamoDB y Logs), así que el panel funciona en modo solo cliente hasta que se
agregue.

## Corrida del k6 oficial en LocalStack (18/10/2026, 18:09–18:16 COT)

> Histórica: es la regla anterior a ADR-001.

Log: `logs/k6-localstack-20261018T230825Z.log` (140/140 iteraciones, 7 min 10 s). El diff con el script oficial es
solo la línea `const url`.

| Nivel | Iteraciones | Respuestas vistas |
|---|---|---|
| N1 | 1–20 | 200 OK · 500 Full con Error |
| N2 | 21–39 | 200 OK |
| N1 | 40–59 | 200 OK · 500 Full con Error |
| N3 | 60–78 | 200 Operación al mínimo |
| N2 | 79–98 | 200 OK · 500 Operación Limitada |
| N3 | 99–118 | 200 Operación al mínimo |
| N2 | 119–137 | 200 OK |
| **N1** | **138–140** | 200 OK |

Secuencia **1-2-1-3-2-3-2-1**: igual a la de `test_k6_oficial`. Termina en N1, pero **solo con 3 iteraciones de
margen**, lo que confirma el riesgo R1.

Notas de la corrida:
- **El mensaje de mantenimiento de N3 no aparece.** Ninguna petición con error cae en un minuto que esté en N3. Ver la
  pregunta 4 de la spec, §13.
- **El log del k6 se reconstruyó** desde la captura de la terminal (`.build/corrida-localstack.out`). `correr-k6.sh`
  se editó mientras corría, y bash, que lee el script por partes, dejó el `.log` vacío. Las 140 líneas son las
  originales. **Regla para la próxima vez: no editar un script mientras se ejecuta.**
- **Los `CAMBIO_NIVEL` de esa corrida no se conservaron.** El redespliegue posterior recreó los grupos de logs de
  LocalStack. En la próxima corrida se extraen **antes** de redesplegar:
  `aws logs filter-log-events --log-group-name /aws/lambda/reto3-router --filter-pattern CAMBIO_NIVEL`.
- **El 400 de `curl` sin `Content-Type` es propio de LocalStack** (así transforma los cuerpos de formulario). Con
  `application/json`, que es lo que manda el k6, responde bien. El router además decodifica `isBase64Encoded`.

## Corrida desde el panel (18/10/2026, 18:33–18:40 COT): evidencia completa

`logs/evidencia-local-20261018T233216Z/` es la exportación del panel:
- **k6:** 140/140 iteraciones, secuencia **1-2-1-3-2-3-2-1**, termina en N1.
- **CloudWatch:** **7 `CAMBIO_NIVEL`** (1→2, 2→1, 1→3, 3→2, 2→3, 3→2, 2→1).
- **Coherencia cliente/servidor: 8 de 8 minutos.**
- **Diff:** solo la URL.

El minuto 23:32 UTC tiene 1 error de una petición manual previa a la corrida, sin efecto en el resultado.

**Prueba manual del Nivel 3 (18:41–18:42):** 10 errores en un minuto y, en el minuto siguiente,
`503 Nivel 3: Sistema bajo mantenimiento, intente más tarde` (con error) y `200 Nivel 3: Operación al mínimo` (sin error).
