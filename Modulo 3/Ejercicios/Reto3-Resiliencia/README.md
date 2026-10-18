# Reto 3: arquitectura resiliente (Group 2)

API Gateway → `reto3-router` → `reto3-nivel{1,2,3}`, con el estado en DynamoDB. **El nivel de cada minuto de reloj se
decide con los errores del minuto anterior**: ≥ 10 → N3 y ≥ 5 → N2. Se degrada de inmediato y se recupera un nivel
por minuto. Diseño completo: `docs/superpowers/specs/2026-10-18-reto3-resiliencia-design.md`.

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

## Qué cambia en el k6 oficial
Solo la URL. `correr-k6.sh` lo verifica con `diff` y guarda el diff en `.build/`.

## Corrida del k6 oficial en LocalStack (18/10/2026, 18:09–18:16 COT)

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
