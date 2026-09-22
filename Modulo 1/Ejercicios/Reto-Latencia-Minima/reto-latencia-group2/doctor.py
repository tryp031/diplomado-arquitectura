#!/usr/bin/env python3
"""
doctor.py — ¿qué puede correr ESTA máquina, y qué le falta?

Existe porque el equipo trabaja en sistemas distintos (macOS y Windows) y el reto
NO es portable de forma uniforme: el plano de control es Python puro y corre en
todas partes, pero el plano de datos usa POSIX —memoria compartida, sockets ICMP,
un compilador de C— y eso en Windows nativo no existe.

La respuesta a «¿no me funciona?» no debería ser preguntarle a alguien. Debería
ser este archivo, diciendo exactamente qué falta y con qué comando se obtiene.

Se escribe en Python y no en bash + PowerShell a propósito: dos implementaciones
de la misma comprobación divergen. Ya pasó en este proyecto con tabla-hosts.csv.

    python3 doctor.py
"""
from __future__ import annotations

import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SISTEMA = AQUI / "sistema"
WINDOWS = sys.platform.startswith("win")

OK, FALTA, AVISO = "  ok  ", " falta", " aviso"


def linea(estado: str, texto: str, detalle: str = "") -> None:
    print(f"[{estado}] {texto}")
    if detalle:
        for l in detalle.splitlines():
            print(f"         {l}")


def hay(programa: str) -> bool:
    return shutil.which(programa) is not None


def puerto_libre(puerto: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", puerto))
            return True
        except OSError:
            return False


def hay_wsl() -> bool:
    """¿Windows con al menos una distribución WSL instalada?"""
    if not WINDOWS or not hay("wsl"):
        return False
    try:
        r = subprocess.run(["wsl", "-l", "-q"], capture_output=True, timeout=10)
        # wsl -l -q devuelve UTF-16 en la consola de Windows.
        salida = r.stdout.decode("utf-16-le", errors="ignore").strip()
        return r.returncode == 0 and bool(salida)
    except (OSError, subprocess.SubprocessError):
        return False


def main() -> int:
    print()
    print("  Reto de Latencia Mínima — Group 2")
    print("  diagnóstico de esta máquina")
    print("  " + "─" * 62)
    print(f"  sistema : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"  python  : {platform.python_version()}  →  {sys.executable}")
    print()

    problemas: list[str] = []

    # ── Lo mínimo para ver el sistema funcionando ────────────────────────────
    print("  PLANO DE CONTROL — la interfaz web")
    if sys.version_info >= (3, 9):
        linea(OK, f"Python {platform.python_version()} (se pide 3.9 o superior)")
    else:
        linea(FALTA, f"Python {platform.python_version()} es demasiado viejo",
              "Se necesita 3.9 o superior: https://www.python.org/downloads/")
        problemas.append("python")

    for f in ("app/servidor.py", "app/index.html", "sistema/tabla-hosts.csv"):
        if (AQUI / f).exists():
            linea(OK, f)
        else:
            linea(FALTA, f"{f} no está — ¿se descomprimió el proyecto entero?")
            problemas.append(f)

    if puerto_libre(8080):
        linea(OK, "puerto 8080 libre")
    else:
        linea(AVISO, "el puerto 8080 está ocupado",
              "Arrancá en otro:  python3 app/servidor.py --puerto 8081")

    # ── Lo que hace falta para el plano de datos completo ────────────────────
    print()
    print("  PLANO DE DATOS — las variantes que se miden")

    compilador = next((c for c in ("cc", "gcc", "clang") if hay(c)), None)
    tiene_make = hay("make")

    if compilador and tiene_make:
        linea(OK, f"compilador de C ({compilador}) y make")
    elif WINDOWS:
        linea(AVISO, "no hay compilador de C — es lo esperado en Windows nativo",
              "La variante Memoria compartida C usa POSIX y no existe en\n"
              "Windows. Para tenerla, instalá WSL2:\n"
              "  wsl --install\n"
              "Sin eso el resto del sistema funciona igual (ver README, «Tres caminos»).")
    else:
        linea(FALTA, "no hay compilador de C o falta make",
              "macOS:  xcode-select --install\n"
              "Debian/Ubuntu:  sudo apt install build-essential")
        problemas.append("compilador")

    if WINDOWS:
        if hay_wsl():
            linea(OK, "WSL2 instalado — tenés acceso al camino completo",
                  "Para medir, entrá con `wsl` y trabajá desde ahí.")
        else:
            linea(AVISO, "sin WSL2: camino Windows nativo",
                  "Podés usar la interfaz y las variantes en Python.\n"
                  "Para las variantes en C y la medición oficial:  wsl --install")

    # ── Qué variantes existen hoy ────────────────────────────────────────────
    print()
    print("  VARIANTES DISPONIBLES AQUÍ")
    # Alcance: TCP Python y Memoria compartida C (ADR-007). A y C nunca se
    # implementaron; Bc y E
    # se midieron y se retiraron del arbol el 16/09 — ver docs/archivo/.
    catalogo = [
        ("tcp-python",           "tcp-python",           "TCP Python",           "python"),
        ("memoria-compartida-c", "memoria-compartida-c", "Memoria compartida C", "c"),
    ]
    for vid, carpeta, nombre, lenguaje in catalogo:
        d = SISTEMA / carpeta
        implementada = d.exists() and any(d.glob("*.py")) or (d / "Makefile").exists()
        if not implementada:
            linea(AVISO, f"{vid}  {nombre}", "todavía sin implementar")
        elif lenguaje == "c" and not (compilador and tiene_make):
            linea(AVISO, f"{vid}  {nombre}", "necesita compilador de C — no disponible aquí")
        else:
            linea(OK, f"{vid}  {nombre}")

    # ── Veredicto ────────────────────────────────────────────────────────────
    print()
    print("  " + "─" * 62)
    if "python" in problemas or any(p.startswith("app/") for p in problemas):
        print("  ✗  Falta algo imprescindible. Mirá los [ falta] de arriba.")
        return 1
    if WINDOWS and not (compilador and tiene_make):
        print("  ✓  Podés arrancar el proyecto:   iniciar.cmd")
        print("     Camino Windows nativo: interfaz + variantes en Python.")
        print("     Para el sistema completo (variantes en C y medición): wsl --install")
    else:
        print("  ✓  Todo listo. Arrancá con:   ./iniciar.sh")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
