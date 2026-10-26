"""Router: el monitor del sistema. Decide el nivel del minuto, invoca el servicio de ese
nivel, cuenta el resultado y registra cada cambio de nivel.

API Gateway (proxy) → handler → Router.atender → InvocadorLambda → reto3-nivel{n}
"""
import base64
import json
import os
import time
from datetime import datetime, timezone
from typing import Callable

from estado import EstadoNoDisponible
from niveles import MENSAJES, respuesta
from observabilidad import Observabilidad
from reglas import N3, Umbrales, decision_para, memoria_minutos, nivel_para

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
            crudo = evento.get("body") or "{}"
            # API Gateway manda el cuerpo en base64 cuando no lo trata como texto (p. ej., sin Content-Type).
            if evento.get("isBase64Encoded"):
                crudo = base64.b64decode(crudo).decode("utf-8")
            cuerpo = json.loads(crudo)
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
        # Se leen el minuto actual y los anteriores que pueden influir (+1 para el nivel previo).
        registros = self.repo.leer_minutos([minuto - k for k in range(memoria_minutos(self.u) + 2)])
        actual = registros.get(minuto)
        if actual is not None and actual.nivel is not None:
            return actual.nivel

        nuevo = decision_para(minuto, registros, self.u)
        vigente, lo_decidi = self.repo.fijar_nivel(minuto, nuevo.nivel, nuevo.degradado_en)
        if lo_decidi:
            anterior = registros.get(minuto - 1)
            previo = anterior.nivel if anterior and anterior.nivel is not None else nivel_para(minuto - 1, registros, self.u)
            if previo != vigente:
                self.obs.emitir(
                    "CAMBIO_NIVEL", minuto=_iso(minuto), de=previo, a=vigente,
                    motivo="degradacion" if vigente > previo else "recuperacion",
                    errores_minuto_anterior=anterior.errores if anterior else 0,
                    umbrales={"degradado": self.u.degradado, "minimo": self.u.minimo,
                              "permanencia": self.u.permanencia},
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
        # Una respuesta sin statusCode es una falla del servicio, no un éxito: se cuenta.
        if not (isinstance(datos, dict) and isinstance(datos.get("statusCode"), int)):
            raise RuntimeError(f"reto3-nivel{nivel}: respuesta inválida {datos!r}")
        return datos


_router: Router | None = None


def _desde_entorno() -> Router:
    from estado import RepositorioDynamo
    funciones = {n: os.environ[f"NIVEL{n}_FN"] for n in (1, 2, 3)}
    umbrales = Umbrales(degradado=int(os.environ.get("UMBRAL_DEGRADADO", 5)),
                        minimo=int(os.environ.get("UMBRAL_MINIMO", 10)),
                        permanencia=int(os.environ.get("PERMANENCIA_MINUTOS", 2)))
    return Router(RepositorioDynamo(os.environ["TABLA"]), InvocadorLambda(funciones), umbrales)


def handler(event, context):
    """Última red: nada sale como un 502 crudo del API Gateway, ni siquiera con mala configuración."""
    global _router
    request_id = getattr(context, "aws_request_id", "local")
    try:
        if _router is None:
            _router = _desde_entorno()
        return _router.atender(event, request_id)
    except Exception as e:
        Observabilidad("router").emitir("FALLA_ROUTER", detalle=repr(e), request_id=request_id)
        return respuesta(*MENSAJES[N3][True])
