# Reto 3: plan de implementación de la arquitectura resiliente

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir en AWS (y antes en LocalStack) un sistema con tres niveles de servicio. El nivel de cada minuto de reloj se decide con los errores del minuto anterior. Con el k6 oficial, el sistema tiene que recorrer N1, N2 y N3 y terminar en N1.

**Architecture:** API Gateway REST → Lambda `reto3-router`, que decide el nivel con el estado de DynamoDB y lo registra → invoca `reto3-nivel{1,2,3}`. La regla es una función pura (`reglas.py`). El estado va detrás de una interfaz (`estado.py`) para probar el router con un repositorio en memoria. La infraestructura está en `template.yaml` (SAM) y se despliega con `aws cloudformation package/deploy`, así que no hace falta SAM CLI. Se despliega igual en LocalStack y en AWS.

**Tech Stack:** Python 3.12 · boto3 · pytest · AWS Lambda / API Gateway REST / DynamoDB / CloudWatch (EMF) · SAM transform · LocalStack 3.8 · k6.

**Spec:** `docs/superpowers/specs/2026-10-18-reto3-resiliencia-design.md`. Lee el §3 (la regla) antes de empezar.

**Raíz del proyecto (todas las rutas relativas a ella):** `Modulo 3/Ejercicios/Reto3-Resiliencia/`. Ojo: el repo tiene espacios en el nombre, así que hay que poner las rutas entre comillas.

**Regla dura:** **nunca** desplegar con el perfil `default` ni con ningún perfil de `~/.aws` que no sea `diplomado`. En esta máquina son cuentas corporativas. Los scripts lo verifican y abortan.

---

## Mapa de archivos

| Archivo | Responsabilidad |
|---|---|
| `src/reglas.py` | Constantes N1/N2/N3, `Umbrales`, `objetivo()`, `siguiente_nivel()`, `nivel_para()`. Sin I/O |
| `src/niveles.py` | Mensajes y códigos por nivel, capacidades, `atender()`, handlers de las 3 Lambdas |
| `src/observabilidad.py` | Una línea JSON por evento, con bloque EMF opcional |
| `src/estado.py` | `RegistroMinuto`, `EstadoNoDisponible`, `RepositorioDynamo` |
| `src/router.py` | `Router` (orquestación) + `InvocadorLambda` + `handler` |
| `tests/conftest.py` | Agrega `src/` al path; fábricas `RepositorioMemoria`, `RelojFalso`, `k6_error()` |
| `tests/test_reglas.py` · `test_niveles.py` · `test_observabilidad.py` · `test_estado.py` · `test_router.py` · `test_k6_oficial.py` | Pruebas |
| `template.yaml` | SAM: API, 4 Lambdas, tabla, log groups, dashboard (solo AWS) |
| `localstack/docker-compose.yml` · `scripts/deploy.sh` · `scripts/correr-k6.sh` | Entornos y corrida |
| `README.md` · `requirements-dev.txt` · `pyproject.toml` | Uso |

---

### Task 1: Esqueleto y entorno de pruebas

**Files:**
- Create: `requirements-dev.txt`, `pyproject.toml`, `tests/conftest.py`

Nota: `src/` **no** es un paquete. Lambda importa `router`, `niveles`, etc. como módulos de primer nivel (`Handler: router.handler`), y los tests hacen lo mismo agregando `src/` al `sys.path`.

- [ ] **Step 1: Crear los archivos**

`requirements-dev.txt`:
```text
boto3>=1.34
pytest>=8
```

`pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
```

`tests/conftest.py`:
```python
"""Fábricas compartidas por las pruebas.

src/ no es un paquete: en Lambda cada módulo se importa en el primer nivel
(Handler: router.handler), y aquí se replica eso agregando src/ al path.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# 1_800_000_000 redondeado al minuto: el k6 arranca en el segundo 00.
T0 = 1_800_000_000 - (1_800_000_000 % 60)


class RelojFalso:
    def __init__(self, t: float = T0):
        self.t = t

    def __call__(self) -> float:
        return self.t


class RepositorioMemoria:
    """Mismo contrato que RepositorioDynamo, en memoria."""

    def __init__(self):
        self.minutos: dict[int, dict] = {}
        self.fallar = False

    def _revisar(self):
        if self.fallar:
            from estado import EstadoNoDisponible
            raise EstadoNoDisponible("falla inyectada")

    def leer_minutos(self, minutos):
        from estado import RegistroMinuto
        self._revisar()
        return {
            m: RegistroMinuto(nivel=d.get("nivel"), errores=d.get("errores", 0))
            for m, d in self.minutos.items() if m in minutos
        }

    def fijar_nivel(self, minuto, nivel):
        self._revisar()
        item = self.minutos.setdefault(minuto, {})
        if "nivel" in item:
            return item["nivel"], False
        item["nivel"] = nivel
        return nivel, True

    def registrar_resultado(self, minuto, es_error):
        self._revisar()
        item = self.minutos.setdefault(minuto, {})
        item["peticiones"] = item.get("peticiones", 0) + 1
        item["errores"] = item.get("errores", 0) + (1 if es_error else 0)


def k6_error(i: int) -> bool:
    """Réplica exacta del patrón de k6-script-profesor-reto3.js (i = currentIteration, base 0)."""
    minuto = i // 20 + 1
    if minuto == 1:
        return i % 20 < 5
    if minuto in (3, 5):
        return i % 20 < 15
    return False
```

- [ ] **Step 2: Crear el venv y comprobar que pytest arranca**

Run:
```bash
cd "Modulo 3/Ejercicios/Reto3-Resiliencia"
python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt
.venv/bin/pytest
```
Expected: `no tests ran` (exit code 5). Todavía no hay tests: lo que se comprueba es que el entorno arranca.

- [ ] **Step 3: Commit**

```bash
git add "Modulo 3/Ejercicios/Reto3-Resiliencia"
git commit -m "chore(m3): esqueleto del Reto 3 y fábricas de pruebas"
```

---

### Task 2: La regla de niveles (`reglas.py`)

**Files:**
- Create: `src/reglas.py`, `src/estado.py` (solo `RegistroMinuto` y `EstadoNoDisponible` por ahora)
- Test: `tests/test_reglas.py`

- [ ] **Step 1: Escribir los tests que fallan**

`tests/test_reglas.py`:
```python
import pytest

from estado import RegistroMinuto
from reglas import N1, N2, N3, Umbrales, nivel_para, objetivo, siguiente_nivel

U = Umbrales()


@pytest.mark.parametrize("errores,esperado", [(0, N1), (4, N1), (5, N2), (9, N2), (10, N3), (15, N3)])
def test_objetivo_por_umbrales(errores, esperado):
    assert objetivo(errores, U) == esperado


def test_degradacion_inmediata_salta_de_1_a_3():
    # Docente 18/09/2026: «se pasa de inmediato».
    assert siguiente_nivel(N1, 15, U) == N3


def test_recuperacion_baja_un_nivel_por_minuto():
    assert siguiente_nivel(N3, 0, U) == N2
    assert siguiente_nivel(N2, 0, U) == N1
    assert siguiente_nivel(N1, 0, U) == N1


def test_recuperacion_parcial_respeta_el_objetivo():
    # Desde N3 con 5 errores el objetivo es N2: coincide con bajar un nivel.
    assert siguiente_nivel(N3, 5, U) == N2


def test_sin_historia_es_n1():
    assert nivel_para(100, {}, U) == N1


def test_usa_el_minuto_anterior():
    regs = {99: RegistroMinuto(nivel=N1, errores=10)}
    assert nivel_para(100, regs, U) == N3


def test_minutos_sin_trafico_cuentan_como_cero_errores():
    # 97 en N3 con 12 errores → 98: N3 → 99 (sin tráfico): N2 → 100: N1
    regs = {97: RegistroMinuto(nivel=N3, errores=12)}
    assert nivel_para(98, regs, U) == N3
    assert nivel_para(99, regs, U) == N2
    assert nivel_para(100, regs, U) == N1


def test_historia_mas_vieja_que_la_memoria_se_ignora():
    regs = {90: RegistroMinuto(nivel=N3, errores=20)}
    assert nivel_para(100, regs, U) == N1


def test_registro_sin_nivel_se_salta():
    regs = {99: RegistroMinuto(nivel=None, errores=0), 98: RegistroMinuto(nivel=N3, errores=0)}
    assert nivel_para(100, regs, U) == N1  # 98:N3 → 99:N2 → 100:N1


def test_diagrama_de_la_sesion():
    # Discord-Aclaraciones-Docente.md §5: 0/5/10/5/0 errores → N1, N1, N2, N3, N2, N1
    errores = [0, 5, 10, 5, 0, 0]
    regs: dict[int, RegistroMinuto] = {}
    niveles = []
    for m, e in enumerate(errores):
        n = nivel_para(m, regs, U)
        regs[m] = RegistroMinuto(nivel=n, errores=e)
        niveles.append(n)
    assert niveles == [N1, N1, N2, N3, N2, N1]


def test_umbrales_invalidos():
    with pytest.raises(ValueError):
        Umbrales(degradado=10, minimo=5)
```

- [ ] **Step 2: Correr y ver que fallan**

Run: `.venv/bin/pytest tests/test_reglas.py`
Expected: falla con `ModuleNotFoundError: No module named 'estado'`.

- [ ] **Step 3: Implementar**

`src/estado.py` (versión inicial; la Task 5 agrega `RepositorioDynamo`):
```python
"""Estado compartido del sistema: un ítem por minuto de reloj en DynamoDB."""
from dataclasses import dataclass


class EstadoNoDisponible(Exception):
    """No se pudo leer ni escribir el estado. El router falla de forma segura hacia N3."""


@dataclass(frozen=True)
class RegistroMinuto:
    nivel: int | None
    errores: int
```

`src/reglas.py`:
```python
"""Regla de niveles del Reto 3. Funciones puras: sin I/O ni reloj.

Fuente: el docente (Discord, 17/09/2026) dice que los errores del minuto que ya pasó
deciden el nivel del minuto actual. La recuperación de un nivel por minuto es una
decisión nuestra (ver la spec, §3).
"""
from dataclasses import dataclass
from typing import Mapping

N1, N2, N3 = 1, 2, 3

# Con recuperación de un nivel por minuto, desde N3 se llega a N1 en 3 pasos.
# Más atrás de eso la historia ya no influye.
MEMORIA_MINUTOS = N3


@dataclass(frozen=True)
class Umbrales:
    degradado: int = 5
    minimo: int = 10

    def __post_init__(self):
        if not 0 < self.degradado < self.minimo:
            raise ValueError(f"umbrales inválidos: {self}")


def objetivo(errores: int, u: Umbrales) -> int:
    if errores >= u.minimo:
        return N3
    if errores >= u.degradado:
        return N2
    return N1


def siguiente_nivel(nivel_anterior: int, errores_minuto_anterior: int, u: Umbrales) -> int:
    """Degrada de inmediato y recupera como máximo un nivel por minuto."""
    return max(objetivo(errores_minuto_anterior, u), nivel_anterior - 1, N1)


def nivel_para(minuto: int, registros: Mapping[int, "RegistroMinuto"], u: Umbrales) -> int:
    """Nivel de `minuto` a partir del último minuto con nivel decidido.

    Los minutos sin registro no tuvieron tráfico y cuentan como 0 errores.
    """
    for atras in range(1, MEMORIA_MINUTOS + 1):
        registro = registros.get(minuto - atras)
        if registro is not None and registro.nivel is not None:
            nivel, errores = registro.nivel, registro.errores
            for _ in range(atras):
                nivel = siguiente_nivel(nivel, errores, u)
                errores = 0
            return nivel
    return N1
```

- [ ] **Step 4: Correr y ver que pasan**

Run: `.venv/bin/pytest tests/test_reglas.py`
Expected: `16 passed` (6 parametrizados + 10).

- [ ] **Step 5: Commit**

```bash
git add "Modulo 3/Ejercicios/Reto3-Resiliencia/src" "Modulo 3/Ejercicios/Reto3-Resiliencia/tests/test_reglas.py"
git commit -m "feat(m3): regla de niveles por minuto anterior con recuperación escalonada"
```

---

### Task 3: Observabilidad (`observabilidad.py`)

**Files:**
- Create: `src/observabilidad.py`
- Test: `tests/test_observabilidad.py`

- [ ] **Step 1: Test que falla**

`tests/test_observabilidad.py`:
```python
import json

from observabilidad import Observabilidad


def test_evento_sin_metricas_es_una_linea_json():
    lineas = []
    obs = Observabilidad("router", escribir=lineas.append, reloj=lambda: 1.5)
    obs.emitir("CAMBIO_NIVEL", de=1, a=3, motivo="degradacion")
    assert len(lineas) == 1
    d = json.loads(lineas[0])
    assert d == {"evento": "CAMBIO_NIVEL", "servicio": "router", "de": 1, "a": 3, "motivo": "degradacion"}


def test_metricas_generan_bloque_emf():
    lineas = []
    obs = Observabilidad("router", escribir=lineas.append, reloj=lambda: 2.0)
    obs.emitir("PETICION", metricas={"Errores": 1, "LatenciaRouter": 12.5}, nivel=2)
    d = json.loads(lineas[0])
    emf = d["_aws"]
    assert emf["Timestamp"] == 2000
    cw = emf["CloudWatchMetrics"][0]
    assert cw["Namespace"] == "Reto3"
    assert cw["Dimensions"] == [["servicio"]]
    assert {m["Name"] for m in cw["Metrics"]} == {"Errores", "LatenciaRouter"}
    assert d["Errores"] == 1 and d["LatenciaRouter"] == 12.5 and d["nivel"] == 2


def test_acentos_se_conservan():
    lineas = []
    Observabilidad("nivel1", escribir=lineas.append).emitir("X", mensaje="Operación")
    assert "Operación" in lineas[0]
```

- [ ] **Step 2: Correr y ver que falla**

Run: `.venv/bin/pytest tests/test_observabilidad.py`
Expected: `ModuleNotFoundError: No module named 'observabilidad'`.

- [ ] **Step 3: Implementar**

`src/observabilidad.py`:
```python
"""Logs estructurados en una línea JSON, con métricas en formato EMF.

CloudWatch Logs convierte el bloque _aws en métricas sin llamar a PutMetricData:
no agrega latencia ni permisos.
"""
import json
import time
from typing import Callable

NAMESPACE = "Reto3"
UNIDADES = {"LatenciaRouter": "Milliseconds"}


class Observabilidad:
    def __init__(self, servicio: str, escribir: Callable[[str], None] = print,
                 reloj: Callable[[], float] = time.time):
        self.servicio = servicio
        self._escribir = escribir
        self._reloj = reloj

    def emitir(self, evento: str, metricas: dict[str, float] | None = None, **campos) -> None:
        registro = {"evento": evento, "servicio": self.servicio, **campos}
        if metricas:
            registro["_aws"] = {
                "Timestamp": int(self._reloj() * 1000),
                "CloudWatchMetrics": [{
                    "Namespace": NAMESPACE,
                    "Dimensions": [["servicio"]],
                    "Metrics": [{"Name": n, "Unit": UNIDADES.get(n, "Count")} for n in metricas],
                }],
            }
            registro.update(metricas)
        self._escribir(json.dumps(registro, ensure_ascii=False))
```

- [ ] **Step 4: Correr y ver que pasa**

Run: `.venv/bin/pytest tests/test_observabilidad.py`
Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add "Modulo 3/Ejercicios/Reto3-Resiliencia/src/observabilidad.py" "Modulo 3/Ejercicios/Reto3-Resiliencia/tests/test_observabilidad.py"
git commit -m "feat(m3): logs JSON con métricas EMF"
```

---

### Task 4: Servicios por nivel (`niveles.py`)

**Files:**
- Create: `src/niveles.py`
- Test: `tests/test_niveles.py`

- [ ] **Step 1: Test que falla**

`tests/test_niveles.py`:
```python
import json

import pytest

import niveles
from reglas import N1, N2, N3


@pytest.mark.parametrize("nivel,falla,status,mensaje", [
    (N1, False, 200, "Nivel 1: OK"),
    (N1, True, 500, "Nivel 1: Operación Full con Error"),
    (N2, False, 200, "Nivel 2: OK"),
    (N2, True, 500, "Nivel 2: Operación Limitada"),
    (N3, False, 200, "Nivel 3: Operación al mínimo"),
    (N3, True, 503, "Nivel 3: Sistema bajo mantenimiento, intente más tarde"),
])
def test_mensajes_exactos(nivel, falla, status, mensaje):
    r = niveles.atender(nivel, {"error": falla}, escribir=lambda _: None)
    assert r["statusCode"] == status
    assert json.loads(r["body"]) == {"message": mensaje}
    assert mensaje in r["body"]  # sin escapes ó: k6 imprime el body tal cual


def test_solo_true_booleano_es_falla():
    r = niveles.atender(N1, {"error": "true"}, escribir=lambda _: None)
    assert r["statusCode"] == 200


def test_capacidades_se_registran():
    lineas = []
    niveles.atender(N2, {"error": False}, escribir=lineas.append)
    d = json.loads(lineas[0])
    assert d["capacidades"] == ["validar", "registrar"]
    assert d["diferidas"] == ["analisis_riesgo", "notificar"]


def test_handlers_por_nivel():
    assert json.loads(niveles.handler_nivel3({"error": False}, None)["body"])["message"] == "Nivel 3: Operación al mínimo"
```

- [ ] **Step 2: Correr y ver que falla**

Run: `.venv/bin/pytest tests/test_niveles.py`
Expected: `ModuleNotFoundError: No module named 'niveles'`.

- [ ] **Step 3: Implementar**

`src/niveles.py`:
```python
"""Los tres servicios, uno por nivel. Cada nivel se despliega como una Lambda distinta.

Mensajes de N1 y N2: capturas oficiales de «Resultados esperados».
Mensajes de N3: texto del enunciado.
El fallo lo pide el cliente con "error": true (así funciona el k6 oficial).
"""
import json
from typing import Callable

from observabilidad import Observabilidad
from reglas import N1, N2, N3

MENSAJES = {
    N1: {False: (200, "Nivel 1: OK"), True: (500, "Nivel 1: Operación Full con Error")},
    N2: {False: (200, "Nivel 2: OK"), True: (500, "Nivel 2: Operación Limitada")},
    N3: {False: (200, "Nivel 3: Operación al mínimo"),
         True: (503, "Nivel 3: Sistema bajo mantenimiento, intente más tarde")},
}

TODAS = ("validar", "registrar", "analisis_riesgo", "notificar")
CAPACIDADES = {N1: TODAS, N2: ("validar", "registrar"), N3: ()}


def respuesta(status: int, mensaje: str) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps({"message": mensaje}, ensure_ascii=False),
    }


def atender(nivel: int, cuerpo: dict, escribir: Callable[[str], None] = print) -> dict:
    falla = cuerpo.get("error") is True
    status, mensaje = MENSAJES[nivel][falla]
    capacidades = [] if falla else list(CAPACIDADES[nivel])
    Observabilidad(f"nivel{nivel}", escribir=escribir).emitir(
        "ATENCION", nivel=nivel, status=status, capacidades=capacidades,
        diferidas=[c for c in TODAS if c not in CAPACIDADES[nivel]],
    )
    return respuesta(status, mensaje)


# El router invoca cada Lambda con el cuerpo de la petición como evento.
def handler_nivel1(event, context):
    return atender(N1, event or {})


def handler_nivel2(event, context):
    return atender(N2, event or {})


def handler_nivel3(event, context):
    return atender(N3, event or {})
```

- [ ] **Step 4: Correr y ver que pasa**

Run: `.venv/bin/pytest tests/test_niveles.py`
Expected: `9 passed`.

- [ ] **Step 5: Commit**

```bash
git add "Modulo 3/Ejercicios/Reto3-Resiliencia/src/niveles.py" "Modulo 3/Ejercicios/Reto3-Resiliencia/tests/test_niveles.py"
git commit -m "feat(m3): servicios de nivel 1, 2 y 3 con los mensajes oficiales"
```

---

### Task 5: Repositorio DynamoDB (`estado.py`)

**Files:**
- Modify: `src/estado.py` (agregar `RepositorioDynamo` al final)
- Test: `tests/test_estado.py` (con `botocore.stub.Stubber`, sin dependencias nuevas)

- [ ] **Step 1: Test que falla**

`tests/test_estado.py`:
```python
import boto3
import pytest
from botocore.stub import Stubber

from estado import EstadoNoDisponible, RegistroMinuto, RepositorioDynamo

TABLA = "reto3-estado"


@pytest.fixture
def cliente():
    c = boto3.client("dynamodb", region_name="us-east-2",
                     aws_access_key_id="x", aws_secret_access_key="x")
    with Stubber(c) as s:
        yield c, s


def test_leer_minutos(cliente):
    c, s = cliente
    s.add_response("batch_get_item", {"Responses": {TABLA: [
        {"pk": {"S": "MIN#10"}, "nivel": {"N": "2"}, "errores": {"N": "7"}},
    ]}, "UnprocessedKeys": {}}, {"RequestItems": {TABLA: {
        "Keys": [{"pk": {"S": "MIN#10"}}, {"pk": {"S": "MIN#9"}}], "ConsistentRead": True}}})
    repo = RepositorioDynamo(TABLA, cliente=c)
    assert repo.leer_minutos([10, 9]) == {10: RegistroMinuto(nivel=2, errores=7)}


def test_fijar_nivel_gana(cliente):
    c, s = cliente
    s.add_response("update_item", {})
    assert RepositorioDynamo(TABLA, cliente=c, reloj=lambda: 0).fijar_nivel(10, 3) == (3, True)


def test_fijar_nivel_pierde_la_carrera_y_lee_al_ganador(cliente):
    c, s = cliente
    s.add_client_error("update_item", service_error_code="ConditionalCheckFailedException")
    s.add_response("get_item", {"Item": {"pk": {"S": "MIN#10"}, "nivel": {"N": "2"}}})
    assert RepositorioDynamo(TABLA, cliente=c, reloj=lambda: 0).fijar_nivel(10, 3) == (2, False)


def test_error_de_servicio_es_estado_no_disponible(cliente):
    c, s = cliente
    s.add_client_error("update_item", service_error_code="ProvisionedThroughputExceededException")
    with pytest.raises(EstadoNoDisponible):
        RepositorioDynamo(TABLA, cliente=c, reloj=lambda: 0).registrar_resultado(10, True)


def test_claves_sin_procesar_es_estado_no_disponible(cliente):
    c, s = cliente
    s.add_response("batch_get_item", {"Responses": {TABLA: []},
                                      "UnprocessedKeys": {TABLA: {"Keys": [{"pk": {"S": "MIN#10"}}]}}})
    with pytest.raises(EstadoNoDisponible):
        RepositorioDynamo(TABLA, cliente=c).leer_minutos([10])
```

- [ ] **Step 2: Correr y ver que falla**

Run: `.venv/bin/pytest tests/test_estado.py`
Expected: `ImportError: cannot import name 'RepositorioDynamo'`.

- [ ] **Step 3: Implementar (agregar a `src/estado.py`)**

Agregar al inicio, junto a los imports existentes:
```python
import time
from typing import Callable, Iterable

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
```

Agregar al final:
```python
TTL_SEGUNDOS = 24 * 3600

# Sin reintentos ocultos: una caída de DynamoDB tiene que llegar rápido a la falla segura (lección del M2).
_CONFIG = Config(connect_timeout=1, read_timeout=1, retries={"total_max_attempts": 1})


def _clave(minuto: int) -> dict:
    return {"pk": {"S": f"MIN#{minuto}"}}


class RepositorioDynamo:
    def __init__(self, tabla: str, cliente=None, reloj: Callable[[], float] = time.time):
        self.tabla = tabla
        self._db = cliente or boto3.client("dynamodb", config=_CONFIG)
        self._reloj = reloj

    def _ttl(self) -> dict:
        return {"N": str(int(self._reloj()) + TTL_SEGUNDOS)}

    def leer_minutos(self, minutos: Iterable[int]) -> dict[int, RegistroMinuto]:
        claves = [_clave(m) for m in minutos]
        try:
            r = self._db.batch_get_item(RequestItems={self.tabla: {"Keys": claves, "ConsistentRead": True}})
        except (ClientError, BotoCoreError) as e:
            raise EstadoNoDisponible(str(e)) from e
        if r.get("UnprocessedKeys"):
            raise EstadoNoDisponible("batch_get_item dejó claves sin procesar")
        out = {}
        for item in r["Responses"].get(self.tabla, []):
            minuto = int(item["pk"]["S"].split("#", 1)[1])
            nivel = int(item["nivel"]["N"]) if "nivel" in item else None
            out[minuto] = RegistroMinuto(nivel=nivel, errores=int(item.get("errores", {"N": "0"})["N"]))
        return out

    def fijar_nivel(self, minuto: int, nivel: int) -> tuple[int, bool]:
        """Escribe el nivel del minuto solo si nadie lo hizo antes. Devuelve (nivel vigente, ¿lo escribí yo?)."""
        try:
            self._db.update_item(
                TableName=self.tabla, Key=_clave(minuto),
                UpdateExpression="SET nivel = :n, #ttl = if_not_exists(#ttl, :t)",
                ConditionExpression="attribute_not_exists(nivel)",
                ExpressionAttributeNames={"#ttl": "ttl"},
                ExpressionAttributeValues={":n": {"N": str(nivel)}, ":t": self._ttl()},
            )
            return nivel, True
        except ClientError as e:
            if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
                raise EstadoNoDisponible(str(e)) from e
        except BotoCoreError as e:
            raise EstadoNoDisponible(str(e)) from e
        try:
            item = self._db.get_item(TableName=self.tabla, Key=_clave(minuto), ConsistentRead=True)["Item"]
        except (ClientError, BotoCoreError, KeyError) as e:
            raise EstadoNoDisponible(str(e)) from e
        return int(item["nivel"]["N"]), False

    def registrar_resultado(self, minuto: int, es_error: bool) -> None:
        try:
            self._db.update_item(
                TableName=self.tabla, Key=_clave(minuto),
                UpdateExpression="ADD peticiones :uno, errores :e SET #ttl = if_not_exists(#ttl, :t)",
                ExpressionAttributeNames={"#ttl": "ttl"},
                ExpressionAttributeValues={":uno": {"N": "1"}, ":e": {"N": "1" if es_error else "0"},
                                           ":t": self._ttl()},
            )
        except (ClientError, BotoCoreError) as e:
            raise EstadoNoDisponible(str(e)) from e
```

- [ ] **Step 4: Correr y ver que pasa**

Run: `.venv/bin/pytest tests/test_estado.py tests/test_reglas.py`
Expected: `21 passed`.

- [ ] **Step 5: Commit**

```bash
git add "Modulo 3/Ejercicios/Reto3-Resiliencia/src/estado.py" "Modulo 3/Ejercicios/Reto3-Resiliencia/tests/test_estado.py"
git commit -m "feat(m3): repositorio DynamoDB con contador atómico y nivel por minuto condicional"
```

---

### Task 6: Router (`router.py`)

**Files:**
- Create: `src/router.py`
- Test: `tests/test_router.py`

- [ ] **Step 1: Test que falla**

`tests/test_router.py`:
```python
import json

from conftest import T0, RelojFalso, RepositorioMemoria
import niveles
from reglas import N1, N2, N3
from router import Router


def evento(error=False):
    return {"body": json.dumps({"message": "x", "timestamp": "t", "error": error})}


def armar(repo=None, invocar=None):
    repo = repo or RepositorioMemoria()
    reloj = RelojFalso()
    lineas = []
    invocar = invocar or (lambda nivel, cuerpo: niveles.atender(nivel, cuerpo, escribir=lambda _: None))
    r = Router(repo, invocar, reloj=reloj, escribir=lineas.append)
    return r, repo, reloj, lineas


def mensaje(resp):
    return json.loads(resp["body"])["message"]


def eventos(lineas, tipo):
    return [d for d in map(json.loads, lineas) if d["evento"] == tipo]


def test_arranca_en_n1():
    r, *_ = armar()
    assert mensaje(r.atender(evento(), "id")) == "Nivel 1: OK"


def test_el_minuto_en_curso_no_cambia_de_nivel():
    r, repo, reloj, _ = armar()
    for _ in range(12):
        resp = r.atender(evento(error=True), "id")
    assert mensaje(resp) == "Nivel 1: Operación Full con Error"
    assert repo.minutos[T0 // 60]["errores"] == 12


def test_errores_del_minuto_anterior_degradan_y_se_registra_el_cambio():
    r, repo, reloj, lineas = armar()
    for _ in range(10):
        r.atender(evento(error=True), "id")
    reloj.t += 60
    assert mensaje(r.atender(evento(), "id")) == "Nivel 3: Operación al mínimo"
    cambio = eventos(lineas, "CAMBIO_NIVEL")
    assert len(cambio) == 1
    assert cambio[0]["de"] == N1 and cambio[0]["a"] == N3
    assert cambio[0]["motivo"] == "degradacion" and cambio[0]["errores_minuto_anterior"] == 10


def test_recuperacion_escalonada():
    r, repo, reloj, lineas = armar()
    for _ in range(10):
        r.atender(evento(error=True), "id")
    niveles_vistos = []
    for _ in range(3):
        reloj.t += 60
        niveles_vistos.append(mensaje(r.atender(evento(), "id")))
    assert niveles_vistos == ["Nivel 3: Operación al mínimo", "Nivel 2: OK", "Nivel 1: OK"]
    assert [c["motivo"] for c in eventos(lineas, "CAMBIO_NIVEL")] == ["degradacion", "recuperacion", "recuperacion"]


def test_falla_de_estado_responde_n3_mantenimiento():
    repo = RepositorioMemoria()
    repo.fallar = True
    r, _, _, lineas = armar(repo=repo)
    resp = r.atender(evento(), "id")
    assert resp["statusCode"] == 503
    assert mensaje(resp) == "Nivel 3: Sistema bajo mantenimiento, intente más tarde"
    assert eventos(lineas, "ESTADO_NO_DISPONIBLE")


def test_falla_del_servicio_de_nivel_cuenta_como_error():
    def invocar_roto(nivel, cuerpo):
        raise TimeoutError("lambda lenta")
    r, repo, _, lineas = armar(invocar=invocar_roto)
    resp = r.atender(evento(), "id")
    assert resp["statusCode"] == 503
    assert repo.minutos[T0 // 60]["errores"] == 1
    assert eventos(lineas, "FALLA_NIVEL")


def test_cuerpo_invalido_es_400_y_no_cuenta():
    r, repo, _, _ = armar()
    resp = r.atender({"body": "{no-json"}, "id")
    assert resp["statusCode"] == 400
    assert repo.minutos.get(T0 // 60, {}).get("peticiones", 0) == 0


def test_carrera_dos_routers_mismo_minuto_usan_el_mismo_nivel():
    repo = RepositorioMemoria()
    a, _, reloj_a, _ = armar(repo=repo)
    b, _, reloj_b, _ = armar(repo=repo)
    for _ in range(5):
        a.atender(evento(error=True), "id")
    reloj_a.t += 60
    reloj_b.t += 60
    assert mensaje(b.atender(evento(), "id")) == mensaje(a.atender(evento(), "id")) == "Nivel 2: OK"


def test_cada_peticion_emite_metricas():
    r, _, _, lineas = armar()
    r.atender(evento(error=True), "id")
    p = eventos(lineas, "PETICION")[0]
    assert p["NivelActual"] == N1 and p["Errores"] == 1 and p["Peticiones"] == 1
    assert "_aws" in p
```

- [ ] **Step 2: Correr y ver que falla**

Run: `.venv/bin/pytest tests/test_router.py`
Expected: `ModuleNotFoundError: No module named 'router'`.

- [ ] **Step 3: Implementar**

`src/router.py`:
```python
"""Router: el monitor del sistema. Decide el nivel del minuto, invoca el servicio de ese
nivel, cuenta el resultado y registra cada cambio de nivel.

API Gateway (proxy) → handler → Router.atender → InvocadorLambda → reto3-nivel{n}
"""
import json
import os
import time
from datetime import datetime, timezone
from typing import Callable

from estado import EstadoNoDisponible
from niveles import MENSAJES, respuesta
from observabilidad import Observabilidad
from reglas import MEMORIA_MINUTOS, N3, Umbrales, nivel_para

Invocar = Callable[[int, dict], dict]


def _iso(minuto: int) -> str:
    return datetime.fromtimestamp(minuto * 60, tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


class Router:
    def __init__(self, repo, invocar: Invocar, umbrales: Umbrales = Umbrales(),
                 reloj: Callable[[], float] = time.time, escribir: Callable[[str], None] = print):
        self.repo = repo
        self.invocar = invocar
        self.u = umbrales
        self.reloj = reloj
        self.obs = Observabilidad("router", escribir=escribir, reloj=reloj)

    def atender(self, evento: dict, request_id: str) -> dict:
        inicio = self.reloj()
        minuto = int(inicio // 60)
        try:
            cuerpo = json.loads(evento.get("body") or "{}")
            if not isinstance(cuerpo, dict):
                raise ValueError("el cuerpo no es un objeto JSON")
        except ValueError:
            return respuesta(400, "Solicitud inválida: se esperaba un objeto JSON")

        try:
            nivel = self._nivel_del_minuto(minuto, request_id)
        except EstadoNoDisponible as e:
            # Falla segura: sin estado no sabemos la salud, así que se opera al mínimo.
            self.obs.emitir("ESTADO_NO_DISPONIBLE", minuto=_iso(minuto), detalle=str(e), request_id=request_id)
            return respuesta(*MENSAJES[N3][True])

        try:
            resultado = self.invocar(nivel, cuerpo)
        except Exception as e:  # cualquier falla del servicio de nivel es un error de salud
            self.obs.emitir("FALLA_NIVEL", nivel=nivel, detalle=repr(e), request_id=request_id)
            resultado = respuesta(*MENSAJES[N3][True])

        es_error = resultado["statusCode"] >= 500
        try:
            self.repo.registrar_resultado(minuto, es_error)
        except EstadoNoDisponible as e:
            self.obs.emitir("ESTADO_NO_DISPONIBLE", minuto=_iso(minuto), detalle=str(e), request_id=request_id)

        self.obs.emitir(
            "PETICION", minuto=_iso(minuto), nivel=nivel, status=resultado["statusCode"], request_id=request_id,
            metricas={"NivelActual": nivel, "Errores": int(es_error), "Peticiones": 1,
                      "LatenciaRouter": round((self.reloj() - inicio) * 1000, 1)},
        )
        return resultado

    def _nivel_del_minuto(self, minuto: int, request_id: str) -> int:
        # Se leen el minuto actual y los anteriores que pueden influir (MEMORIA_MINUTOS + 1 para el nivel previo).
        registros = self.repo.leer_minutos([minuto - k for k in range(MEMORIA_MINUTOS + 2)])
        actual = registros.get(minuto)
        if actual is not None and actual.nivel is not None:
            return actual.nivel

        nuevo = nivel_para(minuto, registros, self.u)
        vigente, lo_decidi = self.repo.fijar_nivel(minuto, nuevo)
        if lo_decidi:
            anterior = registros.get(minuto - 1)
            previo = anterior.nivel if anterior and anterior.nivel is not None else nivel_para(minuto - 1, registros, self.u)
            if previo != vigente:
                self.obs.emitir(
                    "CAMBIO_NIVEL", minuto=_iso(minuto), de=previo, a=vigente,
                    motivo="degradacion" if vigente > previo else "recuperacion",
                    errores_minuto_anterior=anterior.errores if anterior else 0,
                    umbrales={"degradado": self.u.degradado, "minimo": self.u.minimo},
                    request_id=request_id, metricas={"Transiciones": 1},
                )
        return vigente


class InvocadorLambda:
    """Invoca la Lambda del nivel de forma síncrona. Sin reintentos: el router cuenta la falla."""

    def __init__(self, funciones: dict[int, str], cliente=None):
        import boto3
        from botocore.config import Config
        self.funciones = funciones
        self._lambda = cliente or boto3.client(
            "lambda", config=Config(connect_timeout=2, read_timeout=3, retries={"total_max_attempts": 1}))

    def __call__(self, nivel: int, cuerpo: dict) -> dict:
        r = self._lambda.invoke(FunctionName=self.funciones[nivel], Payload=json.dumps(cuerpo).encode())
        datos = json.loads(r["Payload"].read() or b"{}")
        if "FunctionError" in r:
            raise RuntimeError(f"reto3-nivel{nivel}: {datos}")
        return datos


_router: Router | None = None


def _desde_entorno() -> Router:
    from estado import RepositorioDynamo
    funciones = {n: os.environ[f"NIVEL{n}_FN"] for n in (1, 2, 3)}
    umbrales = Umbrales(degradado=int(os.environ.get("UMBRAL_DEGRADADO", 5)),
                        minimo=int(os.environ.get("UMBRAL_MINIMO", 10)))
    return Router(RepositorioDynamo(os.environ["TABLA"]), InvocadorLambda(funciones), umbrales)


def handler(event, context):
    global _router
    if _router is None:
        _router = _desde_entorno()
    return _router.atender(event, getattr(context, "aws_request_id", "local"))
```

- [ ] **Step 4: Correr y ver que pasa**

Run: `.venv/bin/pytest tests/test_router.py`
Expected: `9 passed`.

- [ ] **Step 5: Commit**

```bash
git add "Modulo 3/Ejercicios/Reto3-Resiliencia/src/router.py" "Modulo 3/Ejercicios/Reto3-Resiliencia/tests/test_router.py"
git commit -m "feat(m3): router con estado compartido, falla segura y registro de cambios de nivel"
```

---

### Task 7: Reproducción del k6 oficial (el test que decide si pasamos)

**Files:**
- Test: `tests/test_k6_oficial.py`

- [ ] **Step 1: Escribir el test**

`tests/test_k6_oficial.py`:
```python
"""Reproduce las 140 iteraciones del k6 oficial contra el Router con reloj falso.

Cada iteración dura 3 s (sleep) + la latencia de la petición. El k6 arranca en el segundo 00.
"""
import json

import pytest

from conftest import RelojFalso, RepositorioMemoria, k6_error
import niveles
from router import Router


def correr_k6(paso: float):
    repo, reloj = RepositorioMemoria(), RelojFalso()
    r = Router(repo, lambda n, c: niveles.atender(n, c, escribir=lambda _: None), reloj=reloj, escribir=lambda _: None)
    mensajes = []
    for i in range(140):
        resp = r.atender({"body": json.dumps({"error": k6_error(i)})}, f"it{i + 1}")
        mensajes.append(json.loads(resp["body"])["message"])
        reloj.t += paso
    nivel = [int(m.split(":")[0].split()[1]) for m in mensajes]
    secuencia = [nivel[0]] + [b for a, b in zip(nivel, nivel[1:]) if a != b]
    return secuencia, mensajes


@pytest.mark.parametrize("paso", [3.05, 3.1, 3.2, 3.3, 3.5, 4.0])
def test_recorre_los_3_niveles_y_termina_en_n1(paso):
    secuencia, mensajes = correr_k6(paso)
    assert {1, 2, 3} <= set(secuencia)
    assert mensajes[-1] == "Nivel 1: OK"
    # Nunca se recupera saltando niveles.
    assert all(not (a == 3 and b == 1) for a, b in zip(secuencia, secuencia[1:]))


def test_secuencia_con_latencia_tipica_de_aws():
    secuencia, _ = correr_k6(3.2)
    assert secuencia == [1, 2, 1, 3, 2, 3, 2, 1]


def test_riesgo_r1_latencia_cero_termina_en_n2():
    """Documenta el riesgo R1 de la spec: 140 × 3,00 s = 420 s, justo el borde del minuto 7."""
    _, mensajes = correr_k6(3.0)
    assert mensajes[-1] == "Nivel 2: OK"
```

- [ ] **Step 2: Correr**

Run: `.venv/bin/pytest tests/test_k6_oficial.py -v`
Expected: `8 passed`. Si `test_secuencia_con_latencia_tipica_de_aws` falla, **no ajustar el test**: comparar contra la simulación de la spec, §3, y revisar `reglas.py`.

- [ ] **Step 3: Correr toda la suite**

Run: `.venv/bin/pytest`
Expected: `50 passed`.

- [ ] **Step 4: Commit**

```bash
git add "Modulo 3/Ejercicios/Reto3-Resiliencia/tests/test_k6_oficial.py"
git commit -m "test(m3): reproducción del k6 oficial con varias latencias y el riesgo R1"
```

---

### Task 8: Infraestructura como código (`template.yaml`)

**Files:**
- Create: `template.yaml`

- [ ] **Step 1: Escribir la plantilla**

`template.yaml`:
```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: AWS::Serverless-2016-10-31
Description: Reto 3 — arquitectura resiliente con degradación en 3 niveles (Group 2)

Parameters:
  Entorno:
    Type: String
    AllowedValues: [aws, localstack]
    Default: aws
  UmbralDegradado:
    Type: Number
    Default: 5
  UmbralMinimo:
    Type: Number
    Default: 10

Conditions:
  EsAws: !Equals [!Ref Entorno, aws]

Globals:
  Function:
    Runtime: python3.12
    Architectures: [arm64]
    CodeUri: src/
    MemorySize: 256
    Timeout: 10

Resources:
  Api:
    Type: AWS::Serverless::Api
    Properties:
      Name: reto3-api
      StageName: prod
      MethodSettings:
        - ResourcePath: "/*"
          HttpMethod: "*"
          ThrottlingBurstLimit: 50
          ThrottlingRateLimit: 25

  TablaEstado:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: reto3-estado
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions: [{AttributeName: pk, AttributeType: S}]
      KeySchema: [{AttributeName: pk, KeyType: HASH}]
      TimeToLiveSpecification: {AttributeName: ttl, Enabled: true}

  Nivel1:
    Type: AWS::Serverless::Function
    Properties: {FunctionName: reto3-nivel1, Handler: niveles.handler_nivel1}
  Nivel2:
    Type: AWS::Serverless::Function
    Properties: {FunctionName: reto3-nivel2, Handler: niveles.handler_nivel2}
  Nivel3:
    Type: AWS::Serverless::Function
    Properties: {FunctionName: reto3-nivel3, Handler: niveles.handler_nivel3}

  Router:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: reto3-router
      Handler: router.handler
      Environment:
        Variables:
          TABLA: !Ref TablaEstado
          NIVEL1_FN: !Ref Nivel1
          NIVEL2_FN: !Ref Nivel2
          NIVEL3_FN: !Ref Nivel3
          UMBRAL_DEGRADADO: !Ref UmbralDegradado
          UMBRAL_MINIMO: !Ref UmbralMinimo
      Policies:
        - DynamoDBCrudPolicy: {TableName: !Ref TablaEstado}
        - LambdaInvokePolicy: {FunctionName: !Ref Nivel1}
        - LambdaInvokePolicy: {FunctionName: !Ref Nivel2}
        - LambdaInvokePolicy: {FunctionName: !Ref Nivel3}
      Events:
        Servicio:
          Type: Api
          Properties: {RestApiId: !Ref Api, Path: /service-api, Method: post}

  LogsRouter:
    Type: AWS::Logs::LogGroup
    Properties: {LogGroupName: /aws/lambda/reto3-router, RetentionInDays: 14}
  LogsNivel1:
    Type: AWS::Logs::LogGroup
    Properties: {LogGroupName: /aws/lambda/reto3-nivel1, RetentionInDays: 14}
  LogsNivel2:
    Type: AWS::Logs::LogGroup
    Properties: {LogGroupName: /aws/lambda/reto3-nivel2, RetentionInDays: 14}
  LogsNivel3:
    Type: AWS::Logs::LogGroup
    Properties: {LogGroupName: /aws/lambda/reto3-nivel3, RetentionInDays: 14}

  Dashboard:
    Type: AWS::CloudWatch::Dashboard
    Condition: EsAws
    Properties:
      DashboardName: reto3-resiliencia
      DashboardBody: !Sub |
        {"widgets":[
          {"type":"metric","x":0,"y":0,"width":12,"height":6,"properties":{"title":"Nivel actual (1 Full · 2 Degradado · 3 Mínimo)","region":"${AWS::Region}","stat":"Maximum","period":60,"metrics":[["Reto3","NivelActual","servicio","router"]],"yAxis":{"left":{"min":0,"max":3}}}},
          {"type":"metric","x":12,"y":0,"width":12,"height":6,"properties":{"title":"Errores y peticiones por minuto","region":"${AWS::Region}","stat":"Sum","period":60,"metrics":[["Reto3","Errores","servicio","router"],["Reto3","Peticiones","servicio","router"]]}},
          {"type":"metric","x":0,"y":6,"width":12,"height":6,"properties":{"title":"Transiciones de nivel","region":"${AWS::Region}","stat":"Sum","period":60,"metrics":[["Reto3","Transiciones","servicio","router"]]}},
          {"type":"log","x":12,"y":6,"width":12,"height":6,"properties":{"title":"CAMBIO_NIVEL","region":"${AWS::Region}","query":"SOURCE '/aws/lambda/reto3-router' | filter evento = 'CAMBIO_NIVEL' | fields @timestamp, minuto, de, a, motivo, errores_minuto_anterior | sort @timestamp desc"}}
        ]}

Outputs:
  ApiUrl:
    Value: !Sub "https://${Api}.execute-api.${AWS::Region}.amazonaws.com/prod/service-api"
  ApiId:
    Value: !Ref Api
```

- [ ] **Step 2: Validar la sintaxis contra LocalStack** (después de la Task 9; aquí solo se commitea)

- [ ] **Step 3: Commit**

```bash
git add "Modulo 3/Ejercicios/Reto3-Resiliencia/template.yaml"
git commit -m "feat(m3): plantilla SAM con API, 4 Lambdas, tabla, logs y dashboard"
```

---

### Task 9: LocalStack, despliegue con guarda de cuenta y corrida de k6

**Files:**
- Create: `localstack/docker-compose.yml`, `scripts/deploy.sh`, `scripts/correr-k6.sh`
- Modify: `.gitignore` de la raíz del repo (agregar `Modulo 3/Ejercicios/Reto3-Resiliencia/.build/`)

- [ ] **Step 1: Escribir los archivos**

`localstack/docker-compose.yml`:
```yaml
# LocalStack 3.8 community: es la última imagen que ya está descargada y que no pide auth token.
services:
  localstack:
    image: localstack/localstack:3.8
    container_name: reto3-localstack
    ports: ["127.0.0.1:4566:4566"]
    environment:
      - SERVICES=cloudformation,s3,lambda,apigateway,dynamodb,logs,iam,sts,cloudwatch
      - LAMBDA_RUNTIME_ENVIRONMENT_TIMEOUT=60
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

`scripts/deploy.sh`:
```bash
#!/usr/bin/env bash
# Despliega la misma plantilla en LocalStack o en AWS.
#   scripts/deploy.sh localstack
#   AWS_PROFILE=diplomado CUENTA_ESPERADA=<id de 12 dígitos de Camilo> scripts/deploy.sh aws
# Guarda: en esta máquina el perfil `default` es corporativo. Para AWS se exige el
# perfil `diplomado` Y que la cuenta coincida con CUENTA_ESPERADA; si no, aborta.
set -euo pipefail
cd "$(dirname "$0")/.."
ENTORNO="${1:?uso: deploy.sh localstack|aws}"
STACK=reto3
mkdir -p .build

if [[ "$ENTORNO" == localstack ]]; then
  unset AWS_PROFILE
  export AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=us-east-2
  # localhost.localstack.cloud resuelve a 127.0.0.1 y admite el estilo virtual-host de S3 que usa `package`.
  AWS=(aws --endpoint-url http://localhost.localstack.cloud:4566)
  BUCKET=reto3-artefactos-local
  "${AWS[@]}" s3 mb "s3://$BUCKET" >/dev/null 2>&1 || true
elif [[ "$ENTORNO" == aws ]]; then
  [[ "${AWS_PROFILE:-}" == diplomado ]] || { echo "ABORTO: usa AWS_PROFILE=diplomado" >&2; exit 1; }
  CUENTA=$(aws sts get-caller-identity --query Account --output text)
  [[ "$CUENTA" == "${CUENTA_ESPERADA:?define CUENTA_ESPERADA}" ]] || { echo "ABORTO: cuenta $CUENTA != $CUENTA_ESPERADA" >&2; exit 1; }
  export AWS_DEFAULT_REGION=us-east-2
  AWS=(aws)
  BUCKET="reto3-artefactos-$CUENTA"
  aws s3api head-bucket --bucket "$BUCKET" 2>/dev/null || aws s3 mb "s3://$BUCKET"
else
  echo "entorno desconocido: $ENTORNO" >&2; exit 1
fi

"${AWS[@]}" cloudformation package --template-file template.yaml --s3-bucket "$BUCKET" \
  --output-template-file .build/packaged.yaml >/dev/null
"${AWS[@]}" cloudformation deploy --template-file .build/packaged.yaml --stack-name "$STACK" \
  --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND --parameter-overrides "Entorno=$ENTORNO" --no-fail-on-empty-changeset

API_ID=$("${AWS[@]}" cloudformation describe-stacks --stack-name "$STACK" \
  --query "Stacks[0].Outputs[?OutputKey=='ApiId'].OutputValue" --output text)
if [[ "$ENTORNO" == localstack ]]; then
  URL="http://localhost:4566/restapis/$API_ID/prod/_user_request_/service-api"
else
  URL="https://$API_ID.execute-api.us-east-2.amazonaws.com/prod/service-api"
fi
echo "$URL" | tee ".build/url-$ENTORNO.txt"
```

`scripts/correr-k6.sh`:
```bash
#!/usr/bin/env bash
# Corre el k6 OFICIAL sin modificarlo: solo se reemplaza la URL del profesor por la nuestra.
#   scripts/correr-k6.sh localstack|aws
set -euo pipefail
cd "$(dirname "$0")/.."
ENTORNO="${1:?uso: correr-k6.sh localstack|aws}"
URL=$(cat ".build/url-$ENTORNO.txt")
OFICIAL="../../Material-Clase/k6-script-profesor-reto3.js"
URL_PROFE='https://6u2da0eye1.execute-api.us-east-2.amazonaws.com/prod/service-api'
COPIA=".build/k6-reto3-$ENTORNO.js"
sed "s#$URL_PROFE#$URL#" "$OFICIAL" > "$COPIA"
# Evidencia de que el único cambio es la URL:
diff "$OFICIAL" "$COPIA" | tee ".build/k6-diff-$ENTORNO.txt" || true
[[ $(diff "$OFICIAL" "$COPIA" | grep -c '^[<>]') -eq 2 ]] || { echo "ABORTO: el script cambió en algo más que la URL" >&2; exit 1; }
mkdir -p logs
LOG="logs/k6-$ENTORNO-$(date -u +%Y%m%dT%H%M%SZ).log"
k6 run "$COPIA" 2>&1 | tee "$LOG"
echo "log: $LOG"
```

Agregar a `.gitignore` de la raíz:
```text
# --- Reto 3: artefactos de despliegue ---
Modulo 3/Ejercicios/Reto3-Resiliencia/.build/
```

- [ ] **Step 2: Levantar LocalStack y desplegar**

Run:
```bash
cd "Modulo 3/Ejercicios/Reto3-Resiliencia"
chmod +x scripts/*.sh
docker compose -f localstack/docker-compose.yml up -d
until curl -s localhost:4566/_localstack/health | grep -q '"lambda": "available"'; do sleep 2; done
scripts/deploy.sh localstack
```
Expected: la última línea es `http://localhost:4566/restapis/<id>/prod/_user_request_/service-api`.

Si falla: (0) dentro de las Lambdas, boto3 tiene que apuntar a LocalStack. LocalStack 3.x inyecta `AWS_ENDPOINT_URL` en los contenedores de Lambda **[Supuesto]**: si el router no llega a DynamoDB, revisar `docker logs reto3-localstack`; (a) `Transform` no soportado → revisar los logs con `docker logs reto3-localstack`; (b) arm64 no soportado → cambiar `Architectures` a `[x86_64]` **solo con un parámetro**, no a mano. Anotar en el README cualquier diferencia que se encuentre (riesgo R2 de la spec).

- [ ] **Step 3: Prueba de humo**

Run:
```bash
URL=$(cat .build/url-localstack.txt)
curl -s -X POST "$URL" -H 'Content-Type: application/json' -d '{"error":false}'; echo
curl -s -X POST "$URL" -H 'Content-Type: application/json' -d '{"error":true}'; echo
```
Expected: `{"message": "Nivel 1: OK"}` y `{"message": "Nivel 1: Operación Full con Error"}`.

- [ ] **Step 4: Corrida completa del k6 oficial en LocalStack (~8 min)**

Run: `scripts/correr-k6.sh localstack`
Si k6 v2 rechaza el `sleep()` del contexto *init* del script oficial, **no editar el script**: documentarlo y correr con una versión de k6 que lo acepte (`brew install k6@<versión>` o la imagen `grafana/k6:0.54.0`). Expected: el diff muestra solo la línea `const url = …`; en el log aparecen mensajes de los niveles 1, 2 y 3; la iteración 140 dice `Nivel 1: OK`. Revisar también `CAMBIO_NIVEL` con:
```bash
AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test aws --endpoint-url http://localhost:4566 --region us-east-2 \
  logs filter-log-events --log-group-name /aws/lambda/reto3-router --filter-pattern CAMBIO_NIVEL --query 'events[].message' --output text
```

- [ ] **Step 5: Commit (incluye el log de la corrida en LocalStack como evidencia)**

```bash
git add .gitignore "Modulo 3/Ejercicios/Reto3-Resiliencia/localstack" "Modulo 3/Ejercicios/Reto3-Resiliencia/scripts" "Modulo 3/Ejercicios/Reto3-Resiliencia/logs"
git commit -m "feat(m3): LocalStack, despliegue con guarda de cuenta y corrida del k6 oficial"
```

---

### Task 10: README del proyecto

**Files:**
- Create: `README.md`

- [ ] **Step 1: Escribir**

`README.md`:
````markdown
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

## AWS (cuenta del equipo, us-east-2)
```bash
AWS_PROFILE=diplomado CUENTA_ESPERADA=<id> scripts/deploy.sh aws
scripts/correr-k6.sh aws
```
El script aborta si el perfil no es `diplomado` o si la cuenta no coincide. **Nunca** despliegues con `default`.

## Qué cambia en el k6 oficial
Solo la URL. `correr-k6.sh` lo verifica con `diff` y guarda el diff en `.build/`.
````

- [ ] **Step 2: Commit**

```bash
git add "Modulo 3/Ejercicios/Reto3-Resiliencia/README.md"
git commit -m "docs(m3): README del Reto 3"
```

---

### Task 11: AWS real (depende de Camilo)

Precondición: que Camilo haya completado `Modulo 3/Aportes/danny/m3-guia-aws-camilo-danny.md` y que exista el perfil `diplomado` en `~/.aws`.

- [ ] **Step 1:** `AWS_PROFILE=diplomado CUENTA_ESPERADA=<id> scripts/deploy.sh aws`. Expected: la URL `https://…execute-api.us-east-2…`.
- [ ] **Step 2:** Prueba de humo con `curl` (igual que en la Task 9, Step 3, pero con `.build/url-aws.txt`).
- [ ] **Step 3:** `scripts/correr-k6.sh aws` y, en paralelo, abrir el dashboard `reto3-resiliencia` para grabar el video.
- [ ] **Step 4:** Medir R1: `aws logs filter-log-events --log-group-name /aws/lambda/reto3-router --filter-pattern PETICION` y calcular la media de `LatenciaRouter`. Si la iteración 140 no dio `Nivel 1: OK`, registrarlo; **no** tocar la regla.
- [ ] **Step 5:** Commit del log oficial en `logs/` y actualización de la sección de riesgos de la spec con la latencia medida.

---

## Fuera de este plan

- Borrador de la presentación: `Modulo 3/Aportes/danny/m3-presentacion-reto3-danny.html`. Se hace en paralelo y no depende del código.
- Guía de acceso para Camilo: `Modulo 3/Aportes/danny/m3-guia-aws-camilo-danny.md`.
- Documento técnico PDF y video: cuando haya corrida en AWS.
