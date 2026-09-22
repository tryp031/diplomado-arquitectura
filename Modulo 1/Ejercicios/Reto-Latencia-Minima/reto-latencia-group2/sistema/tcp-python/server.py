#!/usr/bin/env python3
"""
Variante TCP Python — servidor sobre TCP crudo.  IMPLEMENTACIÓN DE REFERENCIA.

Qué hace (dominio del reto, ADR-004):
  Recibe 32 B con un identificador de host (IPv4) y responde 32 B con un veredicto:
  LOCAL / EXTERNO / DESCONOCIDO, según la tabla precargada `tabla-hosts.csv`.

Contrato que cumple (ver ../README.md):
  - Escucha permanentemente (requisito básico del enunciado).
  - Ante un estímulo de N bytes responde con N bytes: una RESPUESTA ESPECÍFICA,
    que depende del estímulo. Con el eco puro anterior la respuesta era constante.
  - La clasificación NO hace E/S, NO asigna memoria y NO consulta nada externo:
    la tabla se carga una sola vez, al arrancar.

Decisiones de diseño relevantes para la latencia:
  - TCP_NODELAY: desactiva el algoritmo de Nagle. Sin esto el kernel agrupa paquetes
    pequeños y aparecen picos de decenas de milisegundos. Es EL error clásico del reto.
  - Conexión persistente: el handshake se paga una vez, no por iteración.
  - recv_into sobre un buffer preasignado: cero asignaciones de memoria por iteración.
  - pack_into sobre un bytearray preasignado: la respuesta se escribe EN SITIO, sin
    construir un objeto bytes nuevo en cada vuelta.
  - `dict.get` enlazado a una variable local: evita la búsqueda de atributo por iteración.

CONCURRENCIA (añadida el 15/09 — ADR-006)
  Un hilo por conexión. El hilo se crea en `accept()`, es decir FUERA de la ruta
  caliente: con un solo cliente el bucle de intercambio es byte por byte el mismo que
  antes, y por eso las mediciones previas siguen siendo comparables. Eso no se supone:
  se verifica midiendo con un cliente y comparando contra el histórico.

  Cada hilo tiene sus PROPIOS buffers. Antes eran tres variables compartidas del
  ámbito de `main()`; con hilos, dos clientes escribiendo `resp` a la vez se pisarían
  la respuesta y cada uno podría recibir el veredicto del otro. No daría error: daría
  resultados incorrectos de vez en cuando, que es peor.

  Lo que este servidor NO hace, a propósito: crecer un hilo «cada X peticiones». Un
  hilo por conexión responde a una causa real —hay un cliente más que atender—;
  un hilo cada X peticiones es una política sin causa, y el número de hilos pasaría a
  depender de cuándo se mire. Ver ADR-006.
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
    clasificador.resumen("servidor B", a.tabla, tabla)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((a.host, a.port))
    # El backlog era 1: con varios clientes concurrentes, el segundo era rechazado
    # antes de que nadie pudiera atenderlo.
    srv.listen(64)
    print(f"[servidor B] escuchando en {a.host}:{a.port}, payload={a.payload}B", flush=True)

    # Enlaces locales: sin búsquedas de atributo ni de global en la ruta caliente.
    # Son de SOLO LECTURA y se comparten entre hilos sin peligro; lo que no se puede
    # compartir son los buffers de escritura, que se crean por hilo.
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
        # Este print está fuera del bucle de intercambio: se paga una vez por conexión.
        # Lo lee el plano de control para mostrar cuántos hilos hay vivos.
        print(f"[servidor B] HILOS vivos={v} atendidas={t} conexión de {par}", flush=True)

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
            print(f"[servidor B] HILOS vivos={v} conexión cerrada", flush=True)

    while True:
        conn, par = srv.accept()
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        # daemon: al bajar el servidor no hay que esperar a que los clientes se vayan.
        threading.Thread(target=atender, args=(conn, par), daemon=True).start()


if __name__ == "__main__":
    main()
