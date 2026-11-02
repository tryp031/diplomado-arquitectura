"""Panel de control del Reto 3: `scripts/panel.sh` (uvicorn --factory panel.app:crear_app).

Observa, no mide. La evidencia oficial es el log del k6 y los logs de CloudWatch, y el panel los
muestra y los deja descargar. Lo que hace sobre el sistema entra por la MISMA puerta que el k6
(la URL del API Gateway). La única excepción es «Reiniciar estado», que solo existe en LocalStack.

Implementa la v3 (histéresis, ADR-002): lee el ítem `V3`, compara por «minuto del k6» (bloques de 20
peticiones) y predice con src/histeresis.py. El panel de la v1 (minuto de reloj y permanencia,
ítems `MIN#m`) quedó en el historial de git, hasta el commit 15bb5b7.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from panel import entornos as ent
from histeresis import ParamsHisteresis
from panel.evidencia import (coherencia, como_csv, como_jsonl, corrida_servidor, guion, resumen_coherencia,
                             zip_evidencia)
from panel.k6 import EjecutorK6

RAIZ = Path(__file__).resolve().parents[1]
ESTATICOS = Path(__file__).parent / "static"
OFICIAL = RAIZ.parents[1] / "Material-Clase" / "k6-script-profesor-reto3.js"
GRACIA_MS = 60_000
REGLA = ParamsHisteresis()  # la misma que despliega template.yaml por defecto (bloques de 20, 5 / 10, rachas 30 / 40)
VENTANA_SIN_CORRIDA_MIN = 12


class PedidoEntorno(BaseModel):
    entorno: Literal["local", "aws"]


class PedidoPeticion(BaseModel):
    error: bool


def crear_app(entornos: dict[str, Any] | None = None, k6: EjecutorK6 | None = None,
              cliente_http: httpx.AsyncClient | None = None) -> FastAPI:
    if entornos is None:
        entornos = {"local": ent.localstack(RAIZ)}
        try:
            entornos["aws"] = ent.aws(RAIZ, os.environ.get("PANEL_AWS_PERFIL"))
            motivo_aws = None
        except ent.EntornoNoDisponible as e:
            motivo_aws = str(e)
    else:
        motivo_aws = None if "aws" in entornos else "AWS no configurado"
    k6 = k6 or EjecutorK6(OFICIAL, RAIZ / ".build", RAIZ / "logs")
    http = cliente_http or httpx.AsyncClient(timeout=10)
    actual = {"entorno": "local"}
    app = FastAPI(title="Reto 3 — panel de control")

    def activo():
        return entornos[actual["entorno"]]

    def ventana_corrida() -> tuple[int, int] | None:
        """[inicio, fin] en ms de la corrida actual del entorno activo, con gracia."""
        if k6.inicio is None or k6.entorno != actual["entorno"]:
            return None
        fin = k6.fin or datetime.now(timezone.utc)
        return int(k6.inicio.timestamp() * 1000) - GRACIA_MS, int(fin.timestamp() * 1000) + GRACIA_MS

    def leer_servidor() -> dict[str, Any]:
        e = activo()
        v = ventana_corrida()
        desde_ms = v[0] if v else (ent.minuto_actual() - VENTANA_SIN_CORRIDA_MIN) * 60_000
        vacio = {"estado": None, "eventos": [], "peticiones": {}}
        try:
            estado_v3 = e.estado_v3()
            eventos = e.eventos_router(desde_ms)  # una sola lectura de CloudWatch por consulta
        except ent.SinLectura as err:  # no es una falla: el panel sigue con la mirada del cliente
            return {**vacio, "error": None, "lectura": False, "motivo": str(err)}
        except ent.EntornoNoDisponible as err:
            return {**vacio, "error": str(err), "lectura": True, "motivo": None}
        clave = [d for d in eventos if d["evento"] in ent.EVENTOS_CLAVE]
        corrida = corrida_servidor(eventos, int(k6.inicio.timestamp() * 1000) if v else None)
        return {"estado": estado_v3, "eventos": clave[::-1][:40], "peticiones": corrida,
                "error": None, "lectura": True, "motivo": None}

    def nivel_v3(estado_v3: dict[str, Any] | None) -> dict[str, Any]:
        """Lo que dice el ítem V3: nivel, petición, bloque en curso y racha hacia el siguiente umbral."""
        if not estado_v3 or not estado_v3.get("seq"):
            return {"actual": None, "peticion": 0, "minuto_k6": None, "errores_bloque": 0, "racha": 0,
                    "meta_racha": None, "ultimo": None, "corrida_cerrada": True}
        n, seq = estado_v3["nivel"], estado_v3["seq"]
        ultimo = estado_v3.get("ultimo")
        return {"actual": n, "peticion": seq, "minuto_k6": (seq - 1) // REGLA.tamano + 1,
                "errores_bloque": estado_v3["errores_bloque"], "racha": estado_v3["racha"],
                "meta_racha": {3: REGLA.racha_n2, 2: REGLA.racha_n1}.get(n),
                "ultimo": datetime.fromtimestamp(ultimo, tz=timezone.utc).isoformat() if ultimo else None,
                # Pasado este tiempo sin tráfico, la próxima petición abre una corrida nueva en N1.
                "corrida_cerrada": ultimo is None or time.time() - ultimo > REGLA.inactividad_s}

    def regla() -> dict[str, Any]:
        return {"tamano": REGLA.tamano, "degradado": REGLA.degradado, "minimo": REGLA.minimo,
                "racha_n2": REGLA.racha_n2, "racha_n1": REGLA.racha_n1, "inactividad_s": REGLA.inactividad_s}

    @app.get("/api/estado")
    async def estado() -> dict[str, Any]:
        e = activo()
        servidor = await asyncio.to_thread(leer_servidor)
        mio = k6.entorno == actual["entorno"]
        corrida = k6.resumen() if mio else EjecutorK6.resumen_vacio()
        filas = coherencia(k6.iteraciones if mio else [], servidor["peticiones"], REGLA)
        return {
            "entorno": {"activo": e.nombre, "url": e.url, "aws_disponible": "aws" in entornos,
                        "aws_motivo": motivo_aws, "permite_reinicio": e.permite_reinicio},
            "reloj": {"ahora": datetime.now(timezone.utc).isoformat()},
            "regla": regla(),
            "nivel": nivel_v3(servidor["estado"]),
            "servidor": {k: v for k, v in servidor.items() if k != "peticiones"},
            "coherencia": {"filas": filas, **resumen_coherencia(filas)},
            "k6": corrida,
            "guion": guion(REGLA, k6.iteraciones if mio else []),
        }

    @app.post("/api/entorno")
    async def cambiar_entorno(p: PedidoEntorno):
        if p.entorno not in entornos:
            return JSONResponse({"error": motivo_aws or "entorno no configurado"}, status_code=400)
        if k6.corriendo:
            return JSONResponse({"error": "hay una corrida del k6 en curso"}, status_code=409)
        actual["entorno"] = p.entorno
        return {"entorno": p.entorno}

    @app.post("/api/k6")
    async def correr_k6():
        url = activo().url
        if not url:
            return JSONResponse({"error": "no hay URL desplegada: corra scripts/deploy.sh primero"}, status_code=400)
        try:
            await k6.iniciar(actual["entorno"], url)
        except RuntimeError as err:
            return JSONResponse({"error": str(err)}, status_code=409)
        except Exception as err:  # script alterado, k6 ausente…
            return JSONResponse({"error": f"no se pudo iniciar k6: {err}"}, status_code=500)
        return {"ok": True, "diff": k6.diff}

    @app.post("/api/k6/detener")
    async def detener_k6():
        await k6.detener()
        return {"ok": True}

    @app.post("/api/peticion")
    async def peticion(p: PedidoPeticion):
        """Una petición a mano, con el mismo cuerpo que manda el k6."""
        url = activo().url
        if not url:
            return JSONResponse({"error": "no hay URL desplegada"}, status_code=400)
        cuerpo = {"message": "Petición manual desde el panel", "timestamp": datetime.now(timezone.utc).isoformat(),
                  "error": p.error}
        inicio = time.perf_counter()
        try:
            r = await http.post(url, json=cuerpo)
        except httpx.HTTPError as err:
            return JSONResponse({"error": f"sin respuesta del API: {err}"}, status_code=502)
        try:
            mensaje = r.json().get("message", r.text)
        except ValueError:
            mensaje = r.text
        return {"status": r.status_code, "mensaje": mensaje, "ms": round((time.perf_counter() - inicio) * 1000)}

    @app.post("/api/reiniciar")
    async def reiniciar():
        if k6.corriendo:
            return JSONResponse({"error": "hay una corrida del k6 en curso"}, status_code=409)
        try:
            n = await asyncio.to_thread(activo().reiniciar)
        except PermissionError as err:
            return JSONResponse({"error": str(err)}, status_code=403)
        except ent.EntornoNoDisponible as err:
            return JSONResponse({"error": str(err)}, status_code=503)
        return {"borrados": n}

    # ── Descargas: la evidencia de la corrida actual ──
    def _sin_corrida():
        return JSONResponse({"error": "no hay corrida del k6 en este entorno"}, status_code=404)

    def _nombre(tipo: str, ext: str) -> str:
        sello = k6.inicio.strftime("%Y%m%dT%H%M%SZ") if k6.inicio else "sin-corrida"
        return f"reto3-{actual['entorno']}-{sello}-{tipo}.{ext}"

    def _adjunto(contenido: str | bytes, nombre: str, tipo: str) -> Response:
        return Response(contenido, media_type=tipo, headers={"Content-Disposition": f'attachment; filename="{nombre}"'})

    def _archivos() -> dict[str, str]:
        v = ventana_corrida()
        e = activo()
        try:
            registros = e.registros(v[0], v[1])
            peticiones = corrida_servidor(e.peticiones(v[0], v[1]), v[0] + GRACIA_MS)
            sin_lectura = None
        except ent.SinLectura as err:  # la evidencia del cliente sigue valiendo sola
            registros, peticiones, sin_lectura = [], {}, str(err)
        filas = coherencia(k6.iteraciones, peticiones, REGLA)
        resumen = {k: val for k, val in k6.resumen(ultimas=0).items() if k != "ultimas"}
        resumen.update({"coherencia_cliente_servidor": resumen_coherencia(filas),
                        "regla": {"version": "v3 (histéresis, ADR-002)", **regla()},
                        "servidor_sin_lectura": sin_lectura,
                        "generado": datetime.now(timezone.utc).isoformat(),
                        "nota": "Evidencia exportada por el panel. El log del k6 es la salida cruda del script oficial; "
                                "el diff muestra que solo cambió la URL."})
        return {
            _nombre("k6", "log"): k6.log_path.read_text(encoding="utf-8") if k6.log_path else "",
            _nombre("servidor", "jsonl"): como_jsonl(registros),
            _nombre("minutos", "csv"): como_csv(filas),
            _nombre("resumen", "json"): json.dumps(resumen, ensure_ascii=False, indent=2),
            _nombre("k6-diff", "txt"): k6.diff,
        }

    @app.get("/api/descargas/{tipo}")
    async def descargar(tipo: Literal["k6", "servidor", "minutos", "zip"]):
        if ventana_corrida() is None:
            return _sin_corrida()
        try:
            archivos = await asyncio.to_thread(_archivos)
        except ent.EntornoNoDisponible as err:
            return JSONResponse({"error": str(err)}, status_code=503)
        if tipo == "zip":
            return _adjunto(zip_evidencia(archivos), _nombre("evidencia", "zip"), "application/zip")
        ext = {"k6": "log", "servidor": "jsonl", "minutos": "csv"}[tipo]
        nombre = _nombre(tipo, ext)
        return _adjunto(archivos[nombre], nombre, "text/plain; charset=utf-8")

    app.mount("/", StaticFiles(directory=ESTATICOS, html=True), name="estaticos")
    return app
