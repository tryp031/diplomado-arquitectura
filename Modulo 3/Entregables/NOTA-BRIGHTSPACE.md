# Nota para el profesor — envío del Reto 3 en Brightspace

> Texto que acompaña `Entregable Reto 3.zip` en «Evidencia de aprendizaje: actividad M3».
> El envío es **individual**: cada integrante sube el mismo ZIP con esta nota.
> Se arma con `python3 "Modulo 3/Entregables/empaquetar_codigo.py"` (entregable 1) y el ZIP final
> contiene los 4 archivos `Entregable-*` de esta carpeta.

---

**Actividad M3 — Reto 3: Arquitectura resiliente con degradación en 3 niveles · Group 2**
Integrantes: Daniel Mazo Serna · Freddy Aparicio Marín · Camilo Céspedes Leguizamón

Profesor Diego, adjuntamos la evidencia del Reto 3 en `Entregable Reto 3.zip`, que contiene:

1. **`Entregable-1-Codigo-Fuente-Group2.zip`**: código fuente. Las 4 Lambdas (router y niveles 1, 2 y 3),
   la plantilla `template.yaml` que despliega API Gateway, Lambda, DynamoDB y CloudWatch en AWS, las
   pruebas automáticas, su script de k6 sin modificar y el panel de control usado en la demostración. El
   `README.md` explica la estructura y cómo ejecutarlo. El código de `src/` es exactamente el desplegado en
   AWS para las corridas (mismo `CodeSha256`).
2. **`Entregable-2-Documentacion-Tecnica-Group2.pdf`**: documentación técnica con el atributo de calidad
   priorizado (disponibilidad entendida como resiliencia), las tácticas, las decisiones de arquitectura, el
   modelo C4 y los resultados de la corrida oficial.
3. **`Entregable-3-Logs-Ejecucion-Group2.zip`**: logs del k6 y de CloudWatch de tres corridas en AWS
   (02/11 y 03/11). En las tres: 140/140 peticiones, solo los 35 errores que pide el script y la secuencia
   **1 → 2 → 3 → 2 → 1**, con cambios de nivel en las peticiones 21, 61, 126 y 136, terminando en
   «Nivel 1: OK». El `README.md` explica cómo leer cada archivo.
4. **`Entregable-4-Presentacion-Group2.pdf`**: la presentación expuesta con demostración en vivo en el
   encuentro del 03/11.

**Cómo ejecutar el proyecto** (requiere Python 3.12; para LocalStack, Docker Desktop, AWS CLI v2 y k6):

```
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest                                  # sin AWS: incluye las 140 iteraciones de su k6
docker compose -f localstack/docker-compose.yml up -d
scripts/deploy.sh localstack && scripts/correr-k6.sh localstack
```

- En AWS se despliega con `AWS_PROFILE=<perfil> CUENTA_ESPERADA=<id> scripts/deploy.sh aws`.
- `correr-k6.sh` usa su script cambiando **solo** la URL y lo comprueba con `diff`.
- Las credenciales no se incluyen. Si desea ver la versión en AWS en vivo, podemos hacer la demostración.

Los compromisos y riesgos que conocemos están en las secciones 2 y 12 del documento técnico.

Quedamos atentos. — Group 2
