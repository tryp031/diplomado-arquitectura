"""Router: el monitor del sistema. Decide el nivel del minuto, invoca el servicio de ese
nivel, cuenta el resultado y registra cada cambio de nivel.

Modo `histeresis` (el valor por defecto): la ventana es el «minuto» del k6, un bloque de 20
peticiones numeradas, y la recuperación es por rachas de peticiones sin error (ver histeresis.py).
Modo `reloj`: la ventana es el minuto de reloj y la recuperación se rige por la permanencia
(ver reglas.py).

API Gateway (proxy) → handler → Router.atender → InvocadorLambda → reto3-nivel{n}

API Gateway es la puerta de entrada HTTP de AWS; en modo proxy entrega la petición
completa a esta Lambda.

Entrada: evento de API Gateway (el cuerpo JSON viene en `body`).
Salida:  la respuesta del servicio del nivel (200, 500 o 503); 400 si el cuerpo
         no es un objeto JSON.
Variables de entorno: TABLA, NIVEL1_FN, NIVEL2_FN, NIVEL3_FN,
                      UMBRAL_DEGRADADO (5), UMBRAL_MINIMO (10),
                      MODO (histeresis o reloj; si falta, el código usa histeresis),
                      RACHA_N2 (30) y RACHA_N1 (40), solo en modo histeresis,
                      PERMANENCIA_MINUTOS (2), solo en modo reloj.
Un MODO desconocido hace fallar al router al arrancar, a propósito.

Reglas (modo histeresis):
- Cada petición: 1) se numera y se decide su nivel con el estado guardado en DynamoDB,
  2) se invoca la Lambda de ese nivel, 3) se cuenta el resultado, 4) se registra el evento.
- Es error toda respuesta con statusCode 500 o más (500 y 503).
- Si DynamoDB no responde, se contesta como Nivel 3 y esa petición no se cuenta
  (falla segura).
- Si la Lambda del nivel falla o no responde, se contesta como Nivel 3 con error y
  esa petición sí se cuenta.
- Cada cambio de nivel queda como evento CAMBIO_NIVEL en los logs; la primera petición
  tras 15 s sin tráfico abre una corrida nueva y queda como CORRIDA_NUEVA.
"""
import base64
import json
import os
import time
from datetime import datetime, timezone
from typing import Callable

from estado import EstadoNoDisponible
import histeresis
from niveles import MENSAJES, respuesta
from observabilidad import Observabilidad
from reglas import N3, Umbrales, decision_para, memoria_minutos, nivel_para

Invocar = Callable[[int, dict], dict]


def _iso(minuto: int) -> str:
    return datetime.fromtimestamp(minuto * 60, tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


class Router:
    def __init__(self, repo, invocar: Invocar, umbrales: Umbrales = Umbrales(),
                 reloj: Callable[[], float] = time.time, escribir: Callable[[str], None] = print,
                 params_histeresis: histeresis.ParamsHisteresis | None = None):
        self.repo = repo
        self.histeresis = params_histeresis
        self.invocar = invocar
        self.u = umbrales
        self.reloj = reloj
        self.obs = Observabilidad("router", escribir=escribir, reloj=reloj)

    def atender(self, evento: dict, request_id: str) -> dict:
        inicio = self.reloj()
        # Minuto de reloj: segundos desde 1970 entre 60 (UTC). Solo lo usa el modo `reloj`.
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

        # Con parámetros de histéresis el flujo es otro: la ventana no es el reloj.
        if self.histeresis:
            return self._atender_histeresis(cuerpo, inicio, request_id)

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

    def _atender_histeresis(self, cuerpo: dict, inicio: float, request_id: str) -> dict:
        try:
            estado = self._actualizar(lambda e: histeresis.entrar(e, inicio, self.histeresis), request_id)
        except EstadoNoDisponible as e:
            # Falla segura: sin estado no sabemos la salud, así que se opera al mínimo.
            self.obs.emitir("ESTADO_NO_DISPONIBLE", detalle=str(e), request_id=request_id)
            return respuesta(*MENSAJES[N3][True])
        # `seq` es el número de la petición dentro de la corrida.
        nivel, seq = estado.nivel, estado.seq
        # Bloques de `tamano` peticiones: de la 1 a la 20 es el minuto 1, de la 21 a la 40 el minuto 2, y así.
        minuto_k6 = (seq - 1) // self.histeresis.tamano + 1

        try:
            resultado = self.invocar(nivel, cuerpo)
        except Exception as e:  # cualquier falla del servicio de nivel es un error de salud
            self.obs.emitir("FALLA_NIVEL", nivel=nivel, detalle=repr(e), request_id=request_id)
            resultado = respuesta(*MENSAJES[N3][True])

        es_error = resultado["statusCode"] >= 500
        # Segunda escritura: cuenta el resultado en el bloque y en la racha. Si falla, la petición ya se
        # atendió y solo se deja el aviso en el log.
        try:
            self._actualizar(lambda e: (histeresis.registrar(e, es_error), None), request_id)
        except EstadoNoDisponible as e:
            self.obs.emitir("ESTADO_NO_DISPONIBLE", detalle=str(e), request_id=request_id)

        self.obs.emitir(
            "PETICION", peticion=seq, minuto_k6=minuto_k6, nivel=nivel, status=resultado["statusCode"],
            request_id=request_id,
            metricas={"NivelActual": nivel, "Errores": int(es_error), "Peticiones": 1,
                      "LatenciaRouter": round((self.reloj() - inicio) * 1000, 1)},
        )
        return resultado

    def _actualizar(self, paso, request_id: str):
        """Lectura-modificación-escritura con versión. Si otro router escribió antes, se recalcula
        sobre su estado: ninguna petición se pierde ni se numera dos veces."""
        # Hasta 5 intentos: cada conflicto significa que otro router escribió primero.
        for _ in range(5):
            previo, version = self.repo.leer_histeresis()
            nuevo, transicion = paso(previo)
            if self.repo.guardar_histeresis(nuevo, version):
                break
        else:
            raise EstadoNoDisponible("5 conflictos seguidos al guardar el estado v3")
        if nuevo.seq == 1 and previo.seq > 0 and nuevo.ultimo != previo.ultimo:  # entrar() reinició
            self.obs.emitir("CORRIDA_NUEVA", nivel_previo=previo.nivel, peticiones_previas=previo.seq,
                            request_id=request_id)
        if transicion:
            self.obs.emitir(
                "CAMBIO_NIVEL", peticion=nuevo.seq, minuto_k6=(nuevo.seq - 1) // self.histeresis.tamano + 1,
                de=transicion.de, a=transicion.a, motivo=transicion.motivo,
                errores_minuto_anterior=transicion.errores_bloque_anterior, racha_sin_error=transicion.racha,
                umbrales={"degradado": self.histeresis.degradado, "minimo": self.histeresis.minimo,
                          "racha_n2": self.histeresis.racha_n2, "racha_n1": self.histeresis.racha_n1},
                request_id=request_id, metricas={"Transiciones": 1},
            )
        return nuevo

    def _nivel_del_minuto(self, minuto: int, request_id: str) -> int:
        # Modo `reloj`: si el minuto ya tiene nivel, se usa ese; si no, se decide con la regla y se fija
        # con una escritura condicional para que solo la primera petición del minuto lo escriba.
        # Se leen el minuto actual y los anteriores que pueden influir (+1 para el nivel previo).
        registros = self.repo.leer_minutos([minuto - k for k in range(memoria_minutos(self.u) + 2)])
        actual = registros.get(minuto)
        if actual is not None and actual.nivel is not None:
            return actual.nivel

        # Primera petición del minuto: se decide con la regla del minuto anterior.
        nuevo = decision_para(minuto, registros, self.u)
        vigente, lo_decidi = self.repo.fijar_nivel(minuto, nuevo.nivel, nuevo.degradado_en)
        # Solo quien fijó el nivel registra el cambio, para no duplicar el evento.
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
    # Nombre de la Lambda de cada nivel y umbrales, desde las variables de entorno (con valor por defecto).
    funciones = {n: os.environ[f"NIVEL{n}_FN"] for n in (1, 2, 3)}
    umbrales = Umbrales(degradado=int(os.environ.get("UMBRAL_DEGRADADO", 5)),
                        minimo=int(os.environ.get("UMBRAL_MINIMO", 10)),
                        permanencia=int(os.environ.get("PERMANENCIA_MINUTOS", 2)))
    # `reloj` conserva la regla por minuto de reloj; cualquier valor que no sea `reloj` o `histeresis` falla a propósito.
    modo = os.environ.get("MODO", "histeresis")
    if modo == "reloj":
        return Router(RepositorioDynamo(os.environ["TABLA"]), InvocadorLambda(funciones), umbrales)
    if modo != "histeresis":
        raise ValueError(f"MODO desconocido: {modo!r}")
    params = histeresis.ParamsHisteresis(
        degradado=umbrales.degradado, minimo=umbrales.minimo,
        racha_n2=int(os.environ.get("RACHA_N2", 30)), racha_n1=int(os.environ.get("RACHA_N1", 40)))
    return Router(RepositorioDynamo(os.environ["TABLA"]), InvocadorLambda(funciones), umbrales,
                  params_histeresis=params)


def handler(event, context):
    """Última red: nada sale como un 502 crudo del API Gateway, ni siquiera con mala configuración."""
    global _router
    request_id = getattr(context, "aws_request_id", "local")
    try:
        # El router se crea una vez por contenedor y se reutiliza en las invocaciones siguientes.
        if _router is None:
            _router = _desde_entorno()
        return _router.atender(event, request_id)
    except Exception as e:
        Observabilidad("router").emitir("FALLA_ROUTER", detalle=repr(e), request_id=request_id)
        return respuesta(*MENSAJES[N3][True])
