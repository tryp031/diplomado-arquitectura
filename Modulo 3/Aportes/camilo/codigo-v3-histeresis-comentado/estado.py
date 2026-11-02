"""Estado compartido del sistema en DynamoDB: un ítem por minuto de reloj (modo `reloj`) o un único ítem `V3` (modo `histeresis`)."""
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
    degradado_en: int | None = None  # minuto en que se entró degradando al nivel vigente


# Los ítems vencen a las 24 horas: el atributo `ttl` lo borra DynamoDB por su cuenta.
TTL_SEGUNDOS = 24 * 3600

# Sin reintentos ocultos: una caída de DynamoDB tiene que llegar rápido a la falla segura.
_CONFIG = Config(connect_timeout=1, read_timeout=1, retries={"total_max_attempts": 1})


# Clave del modo `histeresis`: toda la corrida vive en un solo ítem.
_CLAVE_V3 = {"pk": {"S": "V3"}}


# Clave del modo `reloj`: un ítem por minuto, `MIN#<minuto>`.
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
        # Lectura consistente de varios minutos en una sola llamada.
        claves = [_clave(m) for m in minutos]
        try:
            r = self._db.batch_get_item(RequestItems={self.tabla: {"Keys": claves, "ConsistentRead": True}})
        except (ClientError, BotoCoreError) as e:
            raise EstadoNoDisponible(str(e)) from e
        # Si DynamoDB no devolvió todo, no se decide con datos incompletos.
        if r.get("UnprocessedKeys"):
            raise EstadoNoDisponible("batch_get_item dejó claves sin procesar")
        out = {}
        try:
            for item in r["Responses"].get(self.tabla, []):
                minuto = int(item["pk"]["S"].split("#", 1)[1])
                nivel = int(item["nivel"]["N"]) if "nivel" in item else None
                degradado_en = int(item["degradado_en"]["N"]) if "degradado_en" in item else None
                out[minuto] = RegistroMinuto(nivel=nivel, errores=int(item.get("errores", {"N": "0"})["N"]),
                                             degradado_en=degradado_en)
        except (KeyError, ValueError, IndexError) as e:
            raise EstadoNoDisponible(f"ítem malformado: {e!r}") from e
        return out

    def fijar_nivel(self, minuto: int, nivel: int, degradado_en: int | None = None) -> tuple[int, bool]:
        """Escribe el nivel del minuto solo si nadie lo hizo antes. Devuelve (nivel vigente, ¿lo escribí yo?).

        `degradado_en` va en la misma escritura condicional: el nivel y su permanencia no se separan.
        """
        expresion, valores = "SET nivel = :n, #ttl = if_not_exists(#ttl, :t)", {":n": {"N": str(nivel)}, ":t": self._ttl()}
        if degradado_en is not None:
            expresion += ", degradado_en = :d"
            valores[":d"] = {"N": str(degradado_en)}
        try:
            self._db.update_item(
                TableName=self.tabla, Key=_clave(minuto),
                UpdateExpression=expresion,
                ConditionExpression="attribute_not_exists(nivel)",
                ExpressionAttributeNames={"#ttl": "ttl"},
                ExpressionAttributeValues=valores,
            )
            return nivel, True
        except ClientError as e:
            if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
                raise EstadoNoDisponible(str(e)) from e
        except BotoCoreError as e:
            raise EstadoNoDisponible(str(e)) from e
        try:
            item = self._db.get_item(TableName=self.tabla, Key=_clave(minuto), ConsistentRead=True)["Item"]
            return int(item["nivel"]["N"]), False
        except (ClientError, BotoCoreError, KeyError, ValueError) as e:
            raise EstadoNoDisponible(str(e)) from e

    def registrar_resultado(self, minuto: int, es_error: bool) -> None:
        # ADD suma sin leer antes: los contadores no se pisan entre peticiones simultáneas.
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

    # --- modo histeresis: un solo ítem con el estado de la corrida y una versión ---

    def leer_histeresis(self):
        """Estado v3 y su versión (0 si todavía no existe)."""
        from histeresis import EstadoHisteresis
        try:
            item = self._db.get_item(TableName=self.tabla, Key=_CLAVE_V3, ConsistentRead=True).get("Item")
        except (ClientError, BotoCoreError) as e:
            raise EstadoNoDisponible(str(e)) from e
        if not item:
            return EstadoHisteresis(), 0
        try:
            return EstadoHisteresis(
                seq=int(item["seq"]["N"]), nivel=int(item["nivel"]["N"]),
                errores_bloque=int(item["errores_bloque"]["N"]), racha=int(item["racha"]["N"]),
                ultimo=float(item["ultimo"]["N"]) if "ultimo" in item else None,
            ), int(item["version"]["N"])
        except (KeyError, ValueError) as e:
            raise EstadoNoDisponible(f"ítem malformado: {e!r}") from e

    def guardar_histeresis(self, estado, version: int) -> bool:
        """Escribe solo si nadie lo cambió desde `version`. False = conflicto: hay que releer."""
        # Bloqueo optimista: solo se escribe si la versión no cambió desde la lectura, y cada escritura la sube en 1.
        valores = {":v": {"N": str(version)}, ":v1": {"N": str(version + 1)},
                   ":s": {"N": str(estado.seq)}, ":n": {"N": str(estado.nivel)},
                   ":b": {"N": str(estado.errores_bloque)}, ":r": {"N": str(estado.racha)},
                   ":u": {"N": repr(estado.ultimo or 0.0)}, ":t": self._ttl()}
        try:
            self._db.update_item(
                TableName=self.tabla, Key=_CLAVE_V3,
                UpdateExpression="SET version = :v1, seq = :s, nivel = :n, errores_bloque = :b, racha = :r, "
                                 "ultimo = :u, #ttl = :t",
                ConditionExpression="attribute_not_exists(version) OR version = :v",
                ExpressionAttributeNames={"#ttl": "ttl"}, ExpressionAttributeValues=valores)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False
            raise EstadoNoDisponible(str(e)) from e
        except BotoCoreError as e:
            raise EstadoNoDisponible(str(e)) from e
