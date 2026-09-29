#!/usr/bin/env python3
"""
Variante TCP Python — servidor sobre TCP crudo.

Recibe 32 B con un identificador de host (IPv4) y responde 32 B con el veredicto
LOCAL / EXTERNO / DESCONOCIDO según `tabla-hosts.csv`, cargada una sola vez al arrancar.

Decisiones que afectan la latencia:
  - TCP_NODELAY: sin él, Nagle agrupa paquetes pequeños y aparecen picos de decenas de ms.
  - Conexión persistente: el handshake se paga una vez, no por iteración.
  - recv_into / pack_into sobre buffers preasignados: cero asignaciones por iteración.
  - La clasificación no hace E/S ni consulta nada externo.

Concurrencia: un hilo por conexión, creado en `accept()`, fuera de la ruta caliente.
Con un solo cliente el bucle de intercambio es idéntico al de un servidor sin hilos.
Cada hilo tiene sus propios buffers: compartirlos haría que dos clientes se pisaran
la respuesta y recibieran el veredicto del otro, sin ningún error visible.
"""

import argparse
import socket
import struct
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import clasificador  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=9101)
    ap.add_argument("--payload", type=int, default=32, help="tamaño fijo en bytes")
    ap.add_argument("--tabla", type=Path,
                    default=Path(__file__).resolve().parent.parent / "tabla-hosts.csv")
    a = ap.parse_args()

    # --- FUERA de la ruta caliente: una sola vez, al arrancar ----------------
    tabla = clasificador.cargar(a.tabla)
    clasificador.resumen("servidor tcp-python", a.tabla, tabla)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((a.host, a.port))
    # Backlog amplio: con 1, un segundo cliente concurrente sería rechazado.
    srv.listen(64)
    print(f"[servidor tcp-python] escuchando en {a.host}:{a.port}, payload={a.payload}B", flush=True)

    # Enlaces locales: sin búsquedas de atributo en la ruta caliente. Son de solo
    # lectura y se comparten entre hilos sin peligro.
    obtener = tabla.get
    DESCONOCIDO = clasificador.VEREDICTO_DESCONOCIDO
    leer_id = struct.Struct("<I").unpack_from
    escribir_resp = struct.Struct("<BxxxI").pack_into
    n = a.payload

    vivos = 0                      # hilos atendiendo ahora mismo
    atendidas = 0                  # conexiones atendidas desde que arrancó
    candado = threading.Lock()     # solo para los contadores, NUNCA en la ruta caliente

    def atender(conn: socket.socket, par) -> None:
        nonlocal vivos, atendidas
        with candado:
            vivos += 1
            atendidas += 1
            v, t = vivos, atendidas
        # Fuera del bucle de intercambio: se paga una vez por conexión.
        print(f"[servidor tcp-python] HILOS vivos={v} atendidas={t} conexión de {par}", flush=True)

        # Buffers PROPIOS de este hilo. Compartirlos sería una condición de carrera.
        buf = bytearray(n)
        vista = memoryview(buf)
        resp = bytearray(n)
        try:
            while True:
                # Lectura completa del estímulo: TCP es un flujo, no respeta mensajes.
                leidos = 0
                while leidos < n:
                    k = conn.recv_into(vista[leidos:], n - leidos)
                    if k == 0:
                        raise ConnectionResetError
                    leidos += k

                # --- EL DOMINIO: una búsqueda en tabla, sin E/S y sin asignar ---
                host_id = leer_id(buf, clasificador.OFF_HOST_ID)[0]
                escribir_resp(resp, 0, obtener(host_id, DESCONOCIDO), host_id)

                conn.sendall(resp)
        except (ConnectionResetError, BrokenPipeError, OSError):
            pass
        finally:
            conn.close()
            with candado:
                vivos -= 1
                v = vivos
            print(f"[servidor tcp-python] HILOS vivos={v} conexión cerrada", flush=True)

    while True:
        conn, par = srv.accept()
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        # daemon: al bajar el servidor no hay que esperar a que los clientes se vayan.
        threading.Thread(target=atender, args=(conn, par), daemon=True).start()


if __name__ == "__main__":
    main()
