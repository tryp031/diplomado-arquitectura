"""Estado compartido del sistema: un ítem por minuto de reloj en DynamoDB."""
from dataclasses import dataclass
import time
from typing import Callable, Iterable

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError


class EstadoNoDisponible(Exception):
    """No se pudo leer ni escribir el estado. El router falla de forma segura hacia N3."""


@dataclass(frozen=True)
class RegistroMinuto:
    nivel: int | None
    errores: int


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
