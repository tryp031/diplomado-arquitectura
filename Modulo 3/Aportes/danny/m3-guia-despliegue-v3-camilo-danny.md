# Guía para Camilo: desplegar la v3 (histéresis) en AWS

> **Para:** Camilo. **De:** Danny. **Fecha:** 2026-10-30. **Región:** `us-east-2`.
> **Tiempo estimado:** 15 minutos más la corrida del k6 (8 min).
> **Antes de empezar:** el PR de la v3 tiene que estar mergeado en `main`. Haz `git pull` en `main`.

## Qué cambia y qué no

| | v1 desplegada hoy (ADR-001) | v3 oficial (ADR-002) |
|---|---|---|
| «Minuto» que se evalúa | Minuto de reloj | Bloque de 20 peticiones (el «minuto» del k6) |
| Degradar | Errores del minuto anterior: ≥ 5 → N2, ≥ 10 → N3 | **La misma regla**, aplicada al bloque anterior |
| Recuperar | Permanencia de 2 min y luego de a un nivel por minuto | **30** peticiones seguidas sin error para pasar de N3 a N2 y **40** para pasar de N2 a N1 |
| Corrida nueva | Implícita (minutos nuevos) | 15 s sin tráfico devuelven el sistema a N1 |
| Resultado con el k6 | 1-2-3-2-1 (depende de la latencia) | 1 → 2 → 3 → 2 → 1, con cambios en las iteraciones 21, 61, 126 y 136 (no depende de la latencia) |

**No cambia:** el API Gateway (la URL es la misma), la tabla `reto3-estado` (no hay migración), los handlers ni el
runtime. **Sí cambia:** el código de las 4 Lambdas y 3 variables de entorno del router.

## Paso 1: Generar el .zip

Desde `Modulo 3/Ejercicios/Reto3-Resiliencia/`:

```bash
python3 scripts/empaquetar.py        # en Windows: python scripts\empaquetar.py
```

Crea `.build/reto3-src.zip` e imprime su `CodeSha256`. **Usa este .zip y no uno armado a mano.** Es determinista: el
mismo código da el mismo SHA en cualquier máquina, y así `verificar-aws.sh` puede comprobar que lo desplegado es
exactamente la v3.

## Paso 2: Subir el .zip a las 4 Lambdas

Para cada una de `reto3-router`, `reto3-nivel1`, `reto3-nivel2` y `reto3-nivel3`:
Lambda → la función → pestaña **Code** → **Upload from** → **.zip file** → elige `.build/reto3-src.zip` → **Save**.

Las 4 llevan **el mismo .zip**. Los handlers no cambian: `router.handler` y `niveles.handler_nivel1/2/3`.

## Paso 3: Variables de entorno del router

`reto3-router` → **Configuration** → **Environment variables** → **Edit**. Agrega:

| Variable | Valor |
|---|---|
| `MODO` | `histeresis` (sin tilde) |
| `RACHA_N2` | `30` |
| `RACHA_N1` | `40` |

Deja las que ya están (`TABLA`, `NIVEL1_FN`, `NIVEL2_FN`, `NIVEL3_FN`, `UMBRAL_DEGRADADO=5`, `UMBRAL_MINIMO=10`).
`PERMANENCIA_MINUTOS` puede quedarse: la v3 no la usa.

**Ojo con `MODO`:** si escribes otro valor (por ejemplo `histéresis` con tilde), el router falla al arrancar y responde
siempre «Nivel 3: Sistema bajo mantenimiento». Es a propósito, para que el error se note.

## Paso 4: Permisos del rol del router

La v3 lee el estado con **`dynamodb:GetItem`** y lo escribe con **`dynamodb:UpdateItem`** sobre `reto3-estado`. La v1
usaba `BatchGetItem` y `UpdateItem`. Revisa en IAM → el rol de `reto3-router` → que tenga `GetItem`.

**Síntoma si falta:** todas las respuestas son 503 «mantenimiento» y en los logs del router aparece
`ESTADO_NO_DISPONIBLE` con `AccessDenied`.

## Paso 5: Verificar antes de la corrida oficial

Lo corro yo, o tú, con la llave de solo lectura (`.env.aws`):

```bash
scripts/verificar-aws.sh
```

Tiene que decir **«RESULTADO: listo»**. Comprueba `MODO=histeresis`, las rachas, los umbrales y que las 4 Lambdas
tengan el `CodeSha256` del .zip de `main`.

**Prueba rápida (opcional):** manda una petición sin error:

```bash
curl -s -X POST -H 'Content-Type: application/json' -d '{"error": false}' <URL del API>
```

Tiene que responder `{"message": "Nivel 1: OK"}`. En CloudWatch (`/aws/lambda/reto3-router`), el evento `PETICION`
de la v3 trae `"peticion"` y `"minuto_k6"`. Si trae `"minuto"` con una fecha, sigue corriendo la v1.

**Después de la prueba, espera al menos 20 s antes del k6.** Así la petición de prueba no cuenta en la corrida: con 15 s
sin tráfico, el estado vuelve a N1.

## Paso 6: Corrida oficial

```bash
scripts/correr-k6.sh aws
```

**Resultado esperado:**
- 140/140 iteraciones.
- N1 en las iteraciones 1–20, N2 en 21–60, N3 en 61–125, N2 en 126–135 y N1 en 136–140.
- La última respuesta es «Nivel 1: OK».
- En CloudWatch, **4 `CAMBIO_NIVEL`**: 21 (1→2, degradación), 61 (2→3, degradación), 126 (3→2, recuperación,
  `racha_sin_error` 30) y 136 (2→1, recuperación, `racha_sin_error` 40).

Guarda el log de `logs/` y exporta los `CAMBIO_NIVEL`:

```bash
aws logs filter-log-events --log-group-name /aws/lambda/reto3-router --filter-pattern CAMBIO_NIVEL
```

Si se repite la corrida, no hay que limpiar la tabla. El k6 espera al segundo 00 antes de arrancar, y si pasaron más
de 15 s sin tráfico empieza en N1.

**El panel no sirve para validar la v3 todavía.** Su columna «regla» y la coherencia ✓/✗ calculan la v1 y van a
marcar ✗ aunque todo esté bien. La evidencia es el log del k6 más CloudWatch.

## Rollback

El mismo .zip trae las dos versiones. Para volver a la v1 sin subir nada, cambia `MODO=reloj` en el router: la v1
usa `PERMANENCIA_MINUTOS=2`, así que esa variable tiene que estar. Para volver al código anterior, sube el .zip
previo.

## Riesgo que hay que declarar en el informe

Los umbrales 30/40 se calibraron con el script del docente. El margen es de **5 peticiones** en cada comparación
crítica (35 < 40, 25 < 30 y 45 ≥ 40). Si el docente cambia los errores del k6, el resultado puede cambiar. Ver ADR-002.
