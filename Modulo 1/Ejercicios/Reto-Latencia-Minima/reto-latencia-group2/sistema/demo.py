#!/usr/bin/env python3
"""
demo.py — DEMOSTRACIÓN EN VIVO del sistema (entregable 5 del enunciado).

Escribes un host, el sistema responde el veredicto y el tiempo que tardó.

    $ python3 demo.py --variante tcp-python
    host> pepito
      pepito           127.0.0.1        LOCAL           14.2 µs
    host> google
      google           142.250.78.14    EXTERNO         13.9 µs
    host> pepito5
      pepito5          ?                DESCONOCIDO      -       (no está en la tabla)

═══════════════════════════════════════════════════════════════════════════════
POR QUÉ ESTO ES UN PROGRAMA APARTE Y NO UN MODO DEL CLIENTE MEDIDOR

Un `print` a terminal cuesta entre 10 y 50 µs. Eso es 600 veces el p50 de la
variante D (64 ns). Si la demostración compartiera la ruta caliente con la
medición, la medición dejaría de medir el sistema y pasaría a medir la terminal.

Por eso: MISMO servidor, sin tocar una línea; cliente distinto.

  MODO DEMO                        MODO MEDICIÓN
  1 estímulo por tecla             1 000 000 iteraciones seguidas
  imprime en pantalla              array preasignado, volcado al final
  el printf domina el tiempo       nada de E/S en el bucle

El número que muestra esta demo es REAL —se mide con el mismo reloj monótono y la
misma frontera F1—, pero es UNA muestra, y una muestra no es una medición. Los
resultados del informe salen de `run.sh` + `analyze.py`, nunca de aquí. La demo
demuestra que el sistema FUNCIONA; el harness demuestra CUÁNTO TARDA.
═══════════════════════════════════════════════════════════════════════════════
"""

import argparse
import socket
import struct
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clasificador  # noqa: E402

PUERTOS = {"tcp-python": 9101, "memoria-compartida-c": 9103}

VERDE, ROJO, AMAR, GRIS, FIN = "\033[32m", "\033[31m", "\033[33m", "\033[90m", "\033[0m"
COLOR = {
    clasificador.VEREDICTO_LOCAL: VERDE,
    clasificador.VEREDICTO_EXTERNO: ROJO,
    clasificador.VEREDICTO_DESCONOCIDO: AMAR,
}


def cargar_nombres(ruta: Path) -> dict[str, str]:
    """nombre -> ip textual, para poder escribir 'pepito' en vez de '127.0.0.1'."""
    nombres: dict[str, str] = {}
    with ruta.open(newline="") as fh:
        for linea in fh:
            if linea.startswith("#") or not linea.strip():
                continue
            partes = [c.strip() for c in linea.split(",")]
            if len(partes) >= 2 and partes[0] != "nombre":
                nombres[partes[0]] = partes[1]
    return nombres


def main() -> None:
    ap = argparse.ArgumentParser(description="Demostración en vivo del clasificador de hosts")
    ap.add_argument("--variante", default="tcp-python", choices=sorted(PUERTOS))
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--payload", type=int, default=32)
    ap.add_argument("--tabla", type=Path,
                    default=Path(__file__).resolve().parent / "tabla-hosts.csv")
    a = ap.parse_args()
    port = a.port if a.port is not None else PUERTOS[a.variante]

    nombres = cargar_nombres(a.tabla)

    try:
        sock = socket.create_connection((a.host, port), timeout=3.0)
    except OSError as e:
        raise SystemExit(
            f"No hay servidor en {a.host}:{port} — {e}\n"
            f"Levántelo primero:  python3 tcp-python/server.py --port {port}"
        )
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.settimeout(3.0)

    print(f"\n  Clasificador de hosts — {a.variante} · {a.host}:{port}")
    print(f"  {len(nombres)} hosts en tabla. Escriba un nombre o una IP. "
          f"'lista' para verlos, Ctrl-D para salir.\n")

    buf = bytearray(a.payload)
    leer_resp = struct.Struct("<BxxxI").unpack_from

    while True:
        try:
            entrada = input("  host> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  fin.\n")
            break
        if not entrada:
            continue
        if entrada in ("lista", "ls"):
            for n, ip in nombres.items():
                print(f"{GRIS}    {n:<12} {ip}{FIN}")
            continue

        ip = nombres.get(entrada, entrada)
        try:
            host_id = clasificador.id_de_ip(ip)
        except OSError:
            # No está en la tabla y tampoco es una IP: es el caso 'pepito5'.
            print(f"    {entrada:<16} {'?':<16} {AMAR}DESCONOCIDO{FIN}"
                  f"      {GRIS}—   (no está en la tabla){FIN}")
            continue

        estimulo = clasificador.armar_estimulo(host_id, 0, a.payload)

        # Misma frontera F1 que el harness: t0 antes de escribir, t1 tras leer todo.
        try:
            t0 = time.perf_counter_ns()
            sock.sendall(estimulo)
            leidos = 0
            vista = memoryview(buf)
            while leidos < a.payload:
                k = sock.recv_into(vista[leidos:], a.payload - leidos)
                if k == 0:
                    raise ConnectionResetError
                leidos += k
            t1 = time.perf_counter_ns()
        except OSError as e:
            print(f"    {ROJO}error de transporte: {e}{FIN}")
            break

        veredicto, eco = leer_resp(buf, 0)
        if eco != host_id:
            print(f"    {ROJO}error de integridad: el eco no coincide{FIN}")
            continue

        nombre_v = clasificador.NOMBRE_VEREDICTO[veredicto]
        print(f"    {entrada:<16} {ip:<16} {COLOR[veredicto]}{nombre_v:<12}{FIN}"
              f"  {(t1 - t0) / 1000:7.1f} µs")

    sock.close()


if __name__ == "__main__":
    main()
