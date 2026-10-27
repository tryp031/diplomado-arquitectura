"""Corre el k6 OFICIAL desde el panel y lee lo que imprime.

El script del profesor no se modifica: se escribe una copia en .build/ con la URL reemplazada
y se verifica que esa sea la ÚNICA línea distinta (la misma garantía que scripts/correr-k6.sh).
"""
from __future__ import annotations

import asyncio
import difflib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from estado import RegistroMinuto
from reglas import Umbrales, decision_para

URL_PROFESOR = "https://6u2da0eye1.execute-api.us-east-2.amazonaws.com/prod/service-api"
TOTAL_ITERACIONES = 140
# Docente (Discord, 18/09/2026): «siempre vas a ver nivel 1-2-3-3-2-1». Comprimida: 1-2-3-2-1.
SECUENCIA_ESPERADA = [1, 2, 3, 2, 1]
# Errores que pide el script oficial en cada uno de sus 7 minutos (minutos 1, 3 y 5: < 5, < 15, < 15).
ERRORES_DEL_GUION = (5, 0, 15, 0, 15, 0, 0)

_LINEA = re.compile(
    r'time="(?P<ts>[^"]+)".*?msg="Minute: (?P<minuto>\d+), Iteration: (?P<it>\d+), '
    r'Error: (?P<error>true|false), Status: (?P<status>\d+), Message: (?P<cuerpo>.*)" source=console'
)


class ScriptAlterado(Exception):
    """La copia difiere del script oficial en algo más que la URL."""


@dataclass(frozen=True)
class Iteracion:
    ts: str            # reloj del cliente (k6), ISO con zona
    minuto_logico: int  # el «Minute» que imprime k6 (por iteración, no de reloj)
    iteracion: int
    error: bool
    status: int
    mensaje: str
    nivel: int | None   # sale del mensaje «Nivel N: …»; None si no hubo respuesta


def preparar_script(oficial: Path, url: str, destino: Path) -> str:
    """Escribe la copia con la URL cambiada y devuelve el diff como evidencia."""
    original = oficial.read_text(encoding="utf-8")
    if original.count(URL_PROFESOR) != 1:
        raise ScriptAlterado("la URL del profesor no aparece exactamente una vez en el script oficial")
    copia = original.replace(URL_PROFESOR, url)
    diff = list(difflib.unified_diff(original.splitlines(), copia.splitlines(),
                                     "k6-script-profesor-reto3.js", destino.name, lineterm="", n=0))
    cambiadas = [l for l in diff if l[:1] in "+-" and not l.startswith(("+++", "---"))]
    if len(cambiadas) != 2:
        raise ScriptAlterado(f"se esperaban 2 líneas distintas, hay {len(cambiadas)}")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(copia, encoding="utf-8")
    return "\n".join(diff) + "\n"


def parsear_linea(linea: str) -> Iteracion | None:
    m = _LINEA.search(linea)
    if not m:
        return None
    cuerpo = m["cuerpo"].replace('\\"', '"')
    try:
        mensaje = json.loads(cuerpo).get("message", "")
    except (ValueError, AttributeError):
        mensaje = cuerpo  # sin respuesta (status 0) k6 imprime null o vacío
    nivel = re.match(r"Nivel (\d):", mensaje or "")
    return Iteracion(ts=m["ts"], minuto_logico=int(m["minuto"]), iteracion=int(m["it"]),
                     error=m["error"] == "true", status=int(m["status"]), mensaje=mensaje or "",
                     nivel=int(nivel[1]) if nivel else None)


def secuencia(niveles: list[int | None]) -> list[int]:
    """Niveles consecutivos sin repetir: [1,1,2,2,1] → [1,2,1]."""
    out: list[int] = []
    for n in niveles:
        if n is not None and (not out or out[-1] != n):
            out.append(n)
    return out


def guion(u: Umbrales, iteraciones: list[Iteracion]) -> list[dict[str, Any]]:
    """El plan del k6 oficial minuto a minuto: errores pedidos, nivel que predice la regla y lo observado.

    El minuto 8 es la cola: las últimas iteraciones caen ahí por la latencia acumulada (riesgo R1).
    """
    registros: dict[int, RegistroMinuto] = {}
    vistos: dict[int, list[int]] = {}
    for it in iteraciones:
        if it.nivel is not None:
            vistos.setdefault(it.minuto_logico, []).append(it.nivel)
    out = []
    for m, errores in enumerate(ERRORES_DEL_GUION + (0,), start=1):
        d = decision_para(m, registros, u)
        registros[m] = RegistroMinuto(nivel=d.nivel, errores=errores, degradado_en=d.degradado_en)
        niveles = vistos.get(m, [])
        out.append({"minuto": m, "errores": errores, "nivel_esperado": d.nivel, "cola": m > len(ERRORES_DEL_GUION),
                    "niveles_vistos": secuencia(niveles), "iteraciones": len(niveles)})
    return out


class EjecutorK6:
    """Una corrida a la vez. Guarda la salida cruda completa: es la evidencia del cliente."""

    def __init__(self, oficial: Path, build_dir: Path, log_dir: Path, binario: str = "k6"):
        self.oficial, self.build_dir, self.log_dir, self.binario = oficial, build_dir, log_dir, binario
        self._reiniciar()

    def _reiniciar(self) -> None:
        self.estado = "inactivo"  # inactivo | corriendo | terminado | fallido | detenido
        self.entorno: str | None = None
        self.url: str | None = None
        self.inicio: datetime | None = None
        self.fin: datetime | None = None
        self.salida: list[str] = []
        self.iteraciones: list[Iteracion] = []
        self.diff = ""
        self.log_path: Path | None = None
        self.error: str | None = None
        self._proceso: asyncio.subprocess.Process | None = None

    @property
    def corriendo(self) -> bool:
        return self.estado == "corriendo"

    async def iniciar(self, entorno: str, url: str) -> None:
        if self.corriendo:
            raise RuntimeError("ya hay una corrida en curso")
        self._reiniciar()
        self.entorno, self.url = entorno, url
        copia = self.build_dir / f"k6-reto3-{entorno}.js"
        self.diff = preparar_script(self.oficial, url, copia)
        self.inicio = datetime.now(timezone.utc)
        sello = self.inicio.strftime("%Y%m%dT%H%M%SZ")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / f"k6-{entorno}-{sello}.log"
        self._proceso = await asyncio.create_subprocess_exec(
            self.binario, "run", str(copia), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
        self.estado = "corriendo"
        asyncio.create_task(self._seguir(self._proceso))

    async def _seguir(self, proceso: asyncio.subprocess.Process) -> None:
        assert proceso.stdout is not None
        with self.log_path.open("w", encoding="utf-8") as log:  # se escribe a medida: sobrevive a un corte
            async for crudo in proceso.stdout:
                linea = crudo.decode("utf-8", "replace").rstrip("\n")
                self.salida.append(linea)
                log.write(linea + "\n")
                log.flush()
                if (it := parsear_linea(linea)) is not None:
                    self.iteraciones.append(it)
        codigo = await proceso.wait()
        self.fin = datetime.now(timezone.utc)
        if self.estado == "corriendo":
            self.estado = "terminado" if codigo == 0 else "fallido"
            if codigo != 0:
                self.error = f"k6 terminó con código {codigo}"

    async def detener(self) -> None:
        if self.corriendo and self._proceso is not None:
            self.estado = "detenido"
            self._proceso.terminate()

    @staticmethod
    def resumen_vacio() -> dict[str, Any]:
        """Lo que ve un entorno en el que no se corrió el k6."""
        return {"estado": "inactivo", "entorno": None, "url": None, "error": None, "inicio": None, "fin": None,
                "hechas": 0, "total": TOTAL_ITERACIONES, "esperando_segundo_00": False, "secuencia": [],
                "veredicto": {"recorrio_3_niveles": False, "termino_en_n1": False, "sin_saltos": True,
                              "secuencia_esperada": False, "completa": False},
                "secuencia_esperada": SECUENCIA_ESPERADA,
                "ultimas": []}

    def resumen(self, ultimas: int = TOTAL_ITERACIONES) -> dict[str, Any]:
        niveles = [i.nivel for i in self.iteraciones]
        sec = secuencia(niveles)
        completa = len(self.iteraciones) == TOTAL_ITERACIONES
        return {
            "estado": self.estado, "entorno": self.entorno, "url": self.url, "error": self.error,
            "inicio": self.inicio.isoformat() if self.inicio else None,
            "fin": self.fin.isoformat() if self.fin else None,
            "hechas": len(self.iteraciones), "total": TOTAL_ITERACIONES,
            "esperando_segundo_00": self.corriendo and not self.iteraciones,
            "secuencia": sec,
            "veredicto": {
                "recorrio_3_niveles": {1, 2, 3} <= set(sec),
                "termino_en_n1": completa and bool(niveles) and niveles[-1] == 1,
                # Ni 1 → 3 al degradar ni 3 → 1 al recuperar: «si te salta es problema del sistema».
                "sin_saltos": all(abs(a - b) == 1 for a, b in zip(sec, sec[1:])),
                "secuencia_esperada": completa and sec == SECUENCIA_ESPERADA,
                "completa": completa,
            },
            "secuencia_esperada": SECUENCIA_ESPERADA,
            "ultimas": [asdict(i) for i in self.iteraciones[-ultimas:]][::-1],
        }
