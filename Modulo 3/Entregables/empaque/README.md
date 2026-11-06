# Reto 3 — Arquitectura resiliente con degradación en 3 niveles · Código fuente

**Diplomado en Arquitectura de Software y Cloud Computing — PUJ Cali · Módulo 3 · Group 2**

Integrantes: Freddy Erney Aparicio Marín · Camilo Andrés Céspedes Leguizamón · Daniel Mazo Serna

## Arquitectura

```
k6 ──► API Gateway ──► Lambda reto3-router ──┬──► Lambda reto3-nivel1  (Full)
                              │              ├──► Lambda reto3-nivel2  (Degradado)
                              ▼              └──► Lambda reto3-nivel3  (Mínimo)
                     DynamoDB reto3-estado
                     (nivel vigente, contador y racha)
```

Todo se despliega con una sola plantilla (`template.yaml`, AWS SAM / CloudFormation) en `us-east-2`.
Los logs estructurados (`PETICION`, `CAMBIO_NIVEL`, `CORRIDA_NUEVA`, `FALLA_*`) van a CloudWatch Logs.

## Qué contiene este paquete

| Carpeta / archivo | Para qué sirve |
|---|---|
| `src/` | Código de las 4 Lambdas: `router.py` decide el nivel, `niveles.py` responde cada nivel, `histeresis.py` es la regla (funciones puras), `estado.py` guarda el estado en DynamoDB y `observabilidad.py` escribe los logs |
| `template.yaml` | Infraestructura como código: API Gateway, las 4 Lambdas, la tabla DynamoDB, los permisos IAM, los grupos de logs y el dashboard |
| `tests/` | Pruebas automáticas (pytest), incluida la reproducción de las 140 iteraciones del k6 oficial |
| `k6/` | El script oficial del profesor, sin modificar |
| `scripts/` | Despliegue (`deploy.sh`), corrida del k6 (`correr-k6.sh`), verificación del despliegue (`verificar-aws.sh`), empaquetado de las Lambdas (`empaquetar.py`) y panel (`panel.sh`) |
| `panel/` | Panel de control usado en la demostración: corre el k6 y muestra el nivel, los cambios de nivel y la coherencia entre cliente, servidor y regla |
| `localstack/` | AWS simulado en Docker para probar sin la cuenta |
| `docs/ADR/` | Registro de la decisión de la regla oficial (v3) |

## La regla (versión oficial: v3, histéresis)

- **Degradar:** al empezar cada «minuto» del k6, los errores del minuto anterior deciden el nivel:
  **≥ 5 → Nivel 2** y **≥ 10 → Nivel 3**, de inmediato. El «minuto» es un bloque de 20 peticiones
  numeradas, no el reloj: así la latencia de la red no corre las ventanas.
- **Recuperar:** de a un nivel. De N3 a N2 tras **30** peticiones seguidas sin error y de N2 a N1 tras **40**.
- **Corrida nueva:** después de 15 s sin tráfico el sistema vuelve a N1, para poder repetir la prueba.

Con el k6 oficial la secuencia es **1 → 2 → 3 → 2 → 1** (cambios en las peticiones 21, 61, 126 y 136).
La justificación completa (atributo priorizado, tácticas y compromisos) está en el documento técnico.
La regla anterior (v1: minuto de reloj y permanencia de 2 minutos, `ADR-001`) sigue disponible con el
parámetro `Modo=reloj`, solo para comparar.

## Cómo ejecutarlo

Requisitos: Python 3.12, Docker Desktop (para LocalStack), AWS CLI v2 y k6.

**1. Pruebas (no necesitan AWS):**
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest
```

**2. En local con LocalStack (no necesita credenciales):**
```bash
docker compose -f localstack/docker-compose.yml up -d
scripts/deploy.sh localstack
scripts/correr-k6.sh localstack
```
LocalStack no valida IAM, arranques en frío ni latencias reales.

**3. En AWS:**
```bash
AWS_PROFILE=<perfil> CUENTA_ESPERADA=<id de 12 dígitos> scripts/deploy.sh aws
scripts/correr-k6.sh aws
```
El script se detiene si el perfil es `default` o si la cuenta no coincide con `CUENTA_ESPERADA`.

`correr-k6.sh` copia el script oficial reemplazando **solo** la URL, comprueba con `diff` que esa sea la
única diferencia y guarda la salida del k6 en `logs/`.

**Despliegue por consola (alternativa):** `python3 scripts/empaquetar.py` crea `.build/reto3-src.zip`, que se
sube a las cuatro Lambdas. En `reto3-router` se configuran `MODO=histeresis`, `RACHA_N2=30` y `RACHA_N1=40`.
El .zip es determinista: el mismo `src/` produce el mismo `CodeSha256` en cualquier sistema operativo.
El código de `src/` de este paquete es el desplegado en AWS para la corrida oficial
(`CodeSha256 = Gq+DEPQOikPl9sW2XowRlIdEN8XHeXB+ek+uRyXHlqA=`).

**Verificar un despliegue en AWS antes de correr el k6** (con credenciales de solo lectura):
```bash
cp .env.aws.example .env.aws    # y completar la llave de un usuario IAM de solo lectura
scripts/verificar-aws.sh        # modo, umbrales, rachas y CodeSha256 de las 4 Lambdas
```

## Panel de control

```bash
scripts/panel.sh     # http://localhost:8030
```
Contra LocalStack funciona sin configuración. Contra AWS lee el servidor solo si existe `.env.aws`;
sin él queda en modo «solo cliente» (corre el k6 y verifica la regla con lo que ve el propio k6).
El panel **observa, no mide**: la evidencia es el log del k6 y los logs de CloudWatch, que el panel
permite descargar en un ZIP.

## Lo que este paquete **no** incluye

- **Secretos:** no hay credenciales. `.env.aws` se crea a partir de `.env.aws.example` y no se versiona.
- **Logs de las corridas y documentación técnica:** se entregan aparte.
