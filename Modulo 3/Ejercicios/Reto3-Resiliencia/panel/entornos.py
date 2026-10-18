"""Lo que el panel observa del servidor: el estado por minuto (DynamoDB) y los logs (CloudWatch).

Es de SOLO LECTURA en los dos entornos. La única escritura es «Reiniciar estado», que se permite
solo en LocalStack. El panel entra al sistema por la misma puerta que el k6: la URL del API Gateway.

Guarda de cuenta: en la máquina de Danny el perfil `default` de ~/.aws es corporativo. El
entorno AWS exige un perfil con nombre explícito y nunca usa la cadena de credenciales por defecto.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

TABLA = "reto3-estado"
GRUPO_ROUTER = "/aws/lambda/reto3-router"
GRUPOS = (GRUPO_ROUTER, "/aws/lambda/reto3-nivel1", "/aws/lambda/reto3-nivel2", "/aws/lambda/reto3-nivel3")
EVENTOS_CLAVE = ("CAMBIO_NIVEL", "FALLA_NIVEL", "FALLA_ROUTER", "ESTADO_NO_DISPONIBLE")
REGION = "us-east-2"
PERFILES_PROHIBIDOS = {"", "default"}
_CONFIG = Config(connect_timeout=2, read_timeout=5, retries={"total_max_attempts": 2})


class EntornoNoDisponible(Exception):
    pass


def iso_minuto(m: int) -> str:
    return datetime.fromtimestamp(m * 60, tz=timezone.utc).isoformat()


class Entorno:
    def __init__(self, nombre: str, sesion: boto3.Session, archivo_url: Path, endpoint: str | None = None,
                 permite_reinicio: bool = False):
        self.nombre, self.archivo_url, self.permite_reinicio = nombre, archivo_url, permite_reinicio
        self._db = sesion.client("dynamodb", endpoint_url=endpoint, config=_CONFIG)
        self._logs = sesion.client("logs", endpoint_url=endpoint, config=_CONFIG)

    @property
    def url(self) -> str | None:
        # Se relee siempre: un redespliegue en LocalStack cambia el id del API.
        try:
            return self.archivo_url.read_text(encoding="utf-8").strip() or None
        except OSError:
            return None

    def minutos(self, desde: int, hasta: int) -> list[dict[str, Any]]:
        """Ítems MIN#m de la tabla en [desde, hasta]. Los minutos sin tráfico no tienen ítem."""
        claves = [{"pk": {"S": f"MIN#{m}"}} for m in range(desde, hasta + 1)]
        items: list[dict] = []
        try:
            for i in range(0, len(claves), 100):  # límite de BatchGetItem
                r = self._db.batch_get_item(RequestItems={TABLA: {"Keys": claves[i:i + 100], "ConsistentRead": True}})
                items += r["Responses"].get(TABLA, [])
        except (ClientError, BotoCoreError) as e:
            raise EntornoNoDisponible(f"DynamoDB: {e}") from e
        out = []
        for it in items:
            m = int(it["pk"]["S"].split("#", 1)[1])
            out.append({"minuto": m, "iso": iso_minuto(m),
                        "nivel": int(it["nivel"]["N"]) if "nivel" in it else None,
                        "errores": int(it.get("errores", {"N": "0"})["N"]),
                        "peticiones": int(it.get("peticiones", {"N": "0"})["N"])})
        return sorted(out, key=lambda d: d["minuto"])

    def registros(self, desde_ms: int, hasta_ms: int | None = None, grupos=GRUPOS,
                  patron: str | None = None) -> list[dict[str, Any]]:
        """Eventos de CloudWatch Logs en la ventana, ordenados por tiempo."""
        out: list[dict[str, Any]] = []
        for grupo in grupos:
            kwargs: dict[str, Any] = {"logGroupName": grupo, "startTime": desde_ms}
            if hasta_ms:
                kwargs["endTime"] = hasta_ms
            if patron:
                kwargs["filterPattern"] = patron
            try:
                while True:
                    r = self._logs.filter_log_events(**kwargs)
                    out += [{"grupo": grupo, "ts": e["timestamp"], "mensaje": e["message"].rstrip("\n")}
                            for e in r.get("events", [])]
                    if not r.get("nextToken") or not r.get("events"):
                        break
                    kwargs["nextToken"] = r["nextToken"]
            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    continue  # el grupo aparece con la primera invocación de esa Lambda
                raise EntornoNoDisponible(f"CloudWatch Logs: {e}") from e
            except BotoCoreError as e:
                raise EntornoNoDisponible(f"CloudWatch Logs: {e}") from e
        return sorted(out, key=lambda d: d["ts"])

    def eventos_clave(self, desde_ms: int) -> list[dict[str, Any]]:
        """Cambios de nivel y fallas del router, ya decodificados."""
        import json
        out = []
        for r in self.registros(desde_ms, grupos=(GRUPO_ROUTER,)):
            inicio = r["mensaje"].find("{")
            if inicio < 0:
                continue
            try:
                d = json.loads(r["mensaje"][inicio:])
            except ValueError:
                continue
            if d.get("evento") in EVENTOS_CLAVE:
                out.append({"ts": r["ts"], **{k: v for k, v in d.items() if k != "_aws"}})
        return out

    def reiniciar(self) -> int:
        """Borra el estado por minuto. Solo en LocalStack: en AWS el panel es de solo lectura."""
        if not self.permite_reinicio:
            raise PermissionError("el reinicio del estado solo está permitido en LocalStack")
        borrados = 0
        try:
            for pagina in self._db.get_paginator("scan").paginate(TableName=TABLA, ProjectionExpression="pk"):
                for it in pagina["Items"]:
                    self._db.delete_item(TableName=TABLA, Key={"pk": it["pk"]})
                    borrados += 1
        except (ClientError, BotoCoreError) as e:
            raise EntornoNoDisponible(f"DynamoDB: {e}") from e
        return borrados


def localstack(raiz: Path, endpoint: str = "http://localhost:4566") -> Entorno:
    sesion = boto3.Session(aws_access_key_id="test", aws_secret_access_key="test", region_name=REGION)
    return Entorno("local", sesion, raiz / ".build" / "url-localstack.txt", endpoint=endpoint, permite_reinicio=True)


def aws(raiz: Path, perfil: str | None) -> Entorno:
    if (perfil or "") in PERFILES_PROHIBIDOS:
        raise EntornoNoDisponible("defina PANEL_AWS_PERFIL con un perfil de solo lectura del equipo (nunca «default»)")
    return Entorno("aws", boto3.Session(profile_name=perfil, region_name=REGION), raiz / ".build" / "url-aws.txt")


def minuto_actual() -> int:
    return int(time.time() // 60)
