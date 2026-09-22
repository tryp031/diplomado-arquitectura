#!/usr/bin/env python3
"""
clasificador.py — EL DOMINIO del reto, para las variantes interpretadas (A y B).

Carga la MISMA `tabla-hosts.csv` que usa `clasificador.h`. Esa es la razón de que el
dominio viva en un CSV y no en código: dos lenguajes, una sola fuente de verdad. Si la
tabla estuviera duplicada en C y en Python, la comparación B vs Bc dejaría de aislar el
efecto del lenguaje y pasaría a mezclar «lenguaje» con «dos tablas que divergieron».

Decisión registrada en ADR-004.

─────────────────────────────────────────────────────────────────────────────────
ASIMETRÍA DECLARADA FRENTE A LA VERSIÓN EN C — hay que decirla, no esconderla

  C      barrido de 16 ranuras de tiempo constante, sin ramas   ~1-3 ns
  Python búsqueda en `dict`                                     ~40 ns

No son el mismo algoritmo, y por tanto B y Bc no hacen exactamente el mismo trabajo.
Se acepta deliberadamente, por dos razones:

  1. Replicar el barrido de 16 en Python costaría ~2 µs, es decir el 15 % del p50 de
     la variante B (13,2 µs). ESO SÍ contaminaría la medición. El `dict` cuesta 40 ns:
     el 0,3 %.
  2. Un `dict` es lo que escribiría cualquier desarrollador de Python. Forzar un
     barrido manual para «igualar» al C sería una distorsión artificial del lenguaje
     que precisamente estamos midiendo.

Consecuencia honesta que va al informe: **Python no puede ofrecer la garantía de tiempo
constante que sí ofrece C.** El `dict` usa hashing, y su coste depende de colisiones y
del estado de la tabla. Para este ejercicio da igual (40 ns sobre 13 200 ns); en un
sistema de autorización real, no daría igual. Es un trade-off del lenguaje, y es
material del informe, no un defecto que corregir.
─────────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import csv
import socket
import struct
from pathlib import Path

TABLA_MAX = 16

VEREDICTO_EXTERNO = 0
VEREDICTO_LOCAL = 1
VEREDICTO_DESCONOCIDO = 2

NOMBRE_VEREDICTO = {
    VEREDICTO_LOCAL: "LOCAL",
    VEREDICTO_EXTERNO: "EXTERNO",
    VEREDICTO_DESCONOCIDO: "DESCONOCIDO",
}

# Desplazamientos del formato de cable — idénticos a clasificador.h
OFF_HOST_ID = 0
OFF_SEQ = 4
OFF_VEREDICTO = 0
OFF_ECO_ID = 4


def id_de_ip(ip: str) -> int:
    """IPv4 textual -> uint32 en orden de red, igual que inet_pton en C."""
    return struct.unpack("<I", socket.inet_aton(ip))[0]


def cargar(ruta: Path) -> dict[int, int]:
    """Carga la tabla UNA VEZ, al arrancar. Nunca dentro del bucle de medición."""
    tabla: dict[int, int] = {}
    with Path(ruta).open(newline="") as fh:
        for fila in csv.reader(l for l in fh if not l.startswith("#") and l.strip()):
            if not fila or fila[0] == "nombre":
                continue
            nombre, ip, ver = fila[0].strip(), fila[1].strip(), fila[2].strip()
            if len(tabla) >= TABLA_MAX:
                raise SystemExit(
                    f"clasificador: la tabla excede {TABLA_MAX} filas. El límite es una "
                    f"DECISIÓN de diseño (64 B = 1 línea de caché), no un detalle: "
                    f"subirlo invalida ADR-004."
                )
            if ver == "local":
                v = VEREDICTO_LOCAL
            elif ver == "externo":
                v = VEREDICTO_EXTERNO
            else:
                raise SystemExit(f"clasificador: veredicto inválido '{ver}' (host {nombre})")
            try:
                tabla[id_de_ip(ip)] = v
            except OSError as e:
                raise SystemExit(f"clasificador: IP inválida '{ip}' (host {nombre}): {e}") from e
    if not tabla:
        raise SystemExit(f"clasificador: la tabla '{ruta}' no tiene ninguna entrada válida")
    return tabla


def resumen(etiqueta: str, ruta: Path, tabla: dict[int, int]) -> None:
    loc = sum(1 for v in tabla.values() if v == VEREDICTO_LOCAL)
    print(
        f"[{etiqueta}] tabla '{ruta}': {len(tabla)} hosts "
        f"({loc} locales, {len(tabla) - loc} externos) — dict, no barrido; ver docstring",
        flush=True,
    )


def armar_estimulo(host_id: int, seq: int, payload: int) -> bytes:
    """32 B fijos: host_id (4) + seq (4) + relleno."""
    return struct.pack("<II", host_id, seq) + b"\x00" * (payload - 8)
