"""Panel de control del Reto 3: `scripts/panel.sh` (uvicorn --factory panel.app:crear_app).

Observa, no mide. La evidencia oficial es el log del k6 y los logs de CloudWatch, y el panel los
muestra y los deja descargar. Lo que hace sobre el sistema entra por la MISMA puerta que el k6
(la URL del API Gateway). La única excepción es «Reiniciar estado», que solo existe en LocalStack.
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
from panel.evidencia import coherencia, como_csv, como_jsonl, resumen_coherencia, zip_evidencia
from panel.k6 import EjecutorK6, guion
from reglas import Umbrales

RAIZ = Path(__file__).resolve().parents[1]
ESTATICOS = Path(__file__).parent / "static"
OFICIAL = RAIZ.parents[1] / "Material-Clase" / "k6-script-profesor-reto3.js"
GRACIA_MS = 60_000
REGLA = Umbrales()  # la misma que despliega template.yaml por defecto (5 / 10 / permanencia 2)
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
        ahora = ent.minuto_actual()
        v = ventana_corrida()
        desde_min = v[0] // 60_000 if v else ahora - VENTANA_SIN_CORRIDA_MIN
        hasta_min = min(v[1] // 60_000, ahora) if v else ahora
        desde_min = max(desde_min, hasta_min - 20)
        try:
            minutos = e.minutos(desde_min, hasta_min)
            eventos = e.eventos_clave(desde_min * 60_000)
            return {"minutos": minutos, "eventos": eventos[::-1][:40], "error": None, "lectura": True, "motivo": None}
        except ent.SinLectura as err:  # no es una falla: el panel sigue con la mirada del cliente
            return {"minutos": [], "eventos": [], "error": None, "lectura": False, "motivo": str(err)}
        except ent.EntornoNoDisponible as err:
            return {"minutos": [], "eventos": [], "error": str(err), "lectura": True, "motivo": None}

    @app.get("/api/estado")
    async def estado() -> dict[str, Any]:
        e = activo()
        servidor = await asyncio.to_thread(leer_servidor)
        ahora = ent.minuto_actual()
        por_minuto = {m["minuto"]: m for m in servidor["minutos"]}
        actual_srv = por_minuto.get(ahora)
        anterior = por_minuto.get(ahora - 1)
        corrida = k6.resumen() if k6.entorno == actual["entorno"] else EjecutorK6.resumen_vacio()
        filas = coherencia(k6.iteraciones if k6.entorno == actual["entorno"] else [], servidor["minutos"])
        return {
            "entorno": {"activo": e.nombre, "url": e.url, "aws_disponible": "aws" in entornos,
                        "aws_motivo": motivo_aws, "permite_reinicio": e.permite_reinicio},
            "reloj": {"minuto": ent.iso_minuto(ahora), "segundos_a_proximo": 60 - int(time.time() % 60)},
            "regla": {"degradado": REGLA.degradado, "minimo": REGLA.minimo, "permanencia": REGLA.permanencia},
            "nivel": {"actual": actual_srv["nivel"] if actual_srv else None,
                      "degradado_en": ent.iso_minuto(actual_srv["degradado_en"])
                      if actual_srv and actual_srv.get("degradado_en") is not None else None,
                      "errores_minuto_anterior": anterior["errores"] if anterior else 0,
                      "errores_minuto_actual": actual_srv["errores"] if actual_srv else 0},
            "servidor": servidor,
            "coherencia": {"filas": filas, **resumen_coherencia(filas)},
            "k6": corrida,
            "guion": guion(REGLA, k6.iteraciones if k6.entorno == actual["entorno"] else []),
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
            minutos = e.minutos(v[0] // 60_000, v[1] // 60_000)
            sin_lectura = None
        except ent.SinLectura as err:  # la evidencia del cliente sigue valiendo sola
            registros, minutos, sin_lectura = [], [], str(err)
        filas = coherencia(k6.iteraciones, minutos, REGLA)
        resumen = {k: val for k, val in k6.resumen(ultimas=0).items() if k != "ultimas"}
        resumen.update({"coherencia_cliente_servidor": resumen_coherencia(filas),
                        "regla": {"degradado": REGLA.degradado, "minimo": REGLA.minimo,
                                  "permanencia": REGLA.permanencia},
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
    async def descargar(tipo: Literal["k6", "servidor", "minutos", "resumen", "zip"]):
        if ventana_corrida() is None:
            return _sin_corrida()
        try:
            archivos = await asyncio.to_thread(_archivos)
        except ent.EntornoNoDisponible as err:
            return JSONResponse({"error": str(err)}, status_code=503)
        if tipo == "zip":
            return _adjunto(zip_evidencia(archivos), _nombre("evidencia", "zip"), "application/zip")
        ext = {"k6": "log", "servidor": "jsonl", "minutos": "csv", "resumen": "json"}[tipo]
        nombre = _nombre(tipo, ext)
        return _adjunto(archivos[nombre], nombre, "text/plain; charset=utf-8")

    app.mount("/", StaticFiles(directory=ESTATICOS, html=True), name="estaticos")
    return app
