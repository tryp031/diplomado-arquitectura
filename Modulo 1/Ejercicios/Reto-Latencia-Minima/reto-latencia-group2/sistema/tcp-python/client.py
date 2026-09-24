#!/usr/bin/env python3
"""
Variante TCP Python — cliente medidor sobre TCP crudo.  IMPLEMENTACIÓN DE REFERENCIA.

Este archivo es la PLANTILLA de medición. Toda variante replica exactamente este
bucle; solo cambia el transporte. Todo lo demás está congelado en
docs/ESPEC-MEDICION.md y no debe modificarse por variante.

Frontera de medición F1 (ADR-001):
    t0 = inmediatamente ANTES de la llamada de escritura
    t1 = inmediatamente DESPUÉS de que la respuesta esté completamente leída
    latencia = t1 - t0   (RTT en espacio de usuario)

No incluye: establecimiento de conexión (se paga en el warmup) ni arranque del proceso.

─────────────────────────────────────────────────────────────────────────────────
EL CICLO DE ESTÍMULOS — decisión que hay que declarar en el informe (ADR-004 §4)

Los 16 estímulos se construyen ANTES del bucle y se recorren con `i & 15`: un AND,
sin módulo (que es una división) y sin asignar memoria por iteración.

Mezcla de veredictos en el bucle medido:  10 LOCAL · 6 EXTERNO · 0 DESCONOCIDO.

Que no haya DESCONOCIDO en el bucle medido NO sesga el resultado, y esa afirmación
está verificada, no supuesta: el clasificador en C compila a 16 `csel` sin un solo
salto condicional, así que los tres veredictos cuestan exactamente lo mismo. El caso
DESCONOCIDO se ejercita en la autoprueba de arranque y en `demo.py`.
─────────────────────────────────────────────────────────────────────────────────
CONCURRENCIA — `--hilos N` (añadido el 15/09, ADR-006)

Hasta ahora se medía el caso MÁS FAVORABLE que existe: un cliente, un servidor, cero
contención. En producción eso no ocurre nunca. `--hilos N` lanza N clientes a la vez,
cada uno con su propia conexión, y permite trazar cómo se degrada la cola p99,9 al
subir la concurrencia — que es la curva que de verdad separa arquitecturas.

  · N=1 es EXACTAMENTE lo que se medía antes. Las 9,15 M de muestras históricas
    siguen siendo válidas y comparables: son el punto N=1 de la curva.
  · El CSV gana una columna `hilo`. `analyze.py` lee la latencia de la columna 1, así
    que los CSV nuevos y viejos se analizan igual.
  · Cada hilo tiene su conexión, sus estímulos y su array de muestras. No comparten
    nada en la ruta caliente: ni un lock, ni un contador, ni un buffer.

LOTES — por qué el progreso se reporta entre lotes y no por iteración

Mostrar avance exige actualizar un contador, y un contador dentro del bucle medido es
trabajo que se cronometra junto con el intercambio. La medición no puede pagar por su
propia barra de progreso.

Solución: las iteraciones se agrupan en LOTES. El cronómetro sigue midiendo cada
intercambio por separado —la frontera F1 no cambia—, pero el contador de progreso se
toca entre lote y lote, fuera de toda medición. Es la misma técnica de lotes que usa
`control-dominio/micro.c`, aplicada a otro fin.
─────────────────────────────────────────────────────────────────────────────────
"""

import argparse
import csv
import socket
import struct
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import clasificador  # noqa: E402


def conectar(host: str, port: int, reintentos: int, espera_s: float) -> socket.socket:
    """Reintenta la conexión para no depender de un `sleep` externo al arrancar el servidor."""
    ultimo: Exception | None = None
    for _ in range(reintentos):
        try:
            s = socket.create_connection((host, port), timeout=5.0)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(None)  # bloqueante: sin timeout en la ruta caliente
            return s
        except OSError as e:
            ultimo = e
            time.sleep(espera_s)
    raise SystemExit(f"error: no se pudo conectar a {host}:{port} — {ultimo}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=9101)
    ap.add_argument("--payload", type=int, default=32)
    ap.add_argument("--warmup", type=int, default=100_000, help="iteraciones descartadas")
    ap.add_argument("--iters", type=int, default=1_000_000, help="iteraciones medidas")
    ap.add_argument("--out", type=Path, required=True, help="CSV de salida")
    ap.add_argument("--reintentos", type=int, default=50)
    ap.add_argument("--hilos", type=int, default=1,
                    help="clientes concurrentes; 1 = el caso historico (ADR-006)")
    ap.add_argument("--lote", type=int, default=10_000,
                    help="iteraciones por lote; el progreso se reporta ENTRE lotes")
    ap.add_argument("--tabla", type=Path,
                    default=Path(__file__).resolve().parent.parent / "tabla-hosts.csv")
    a = ap.parse_args()

    if a.hilos < 1:
        raise SystemExit("--hilos tiene que ser 1 o mas")

    # --- FUERA de la ruta caliente ------------------------------------------
    tabla = clasificador.cargar(a.tabla)
    clasificador.resumen("cliente B", a.tabla, tabla)

    ids = list(tabla.keys())
    assert len(ids) == 16, f"el ciclo exige exactamente 16 hosts, hay {len(ids)}"
    # Estímulos PRECONSTRUIDOS: nada se serializa dentro del bucle medido.
    ciclo = [clasificador.armar_estimulo(hid, i, a.payload) for i, hid in enumerate(ids)]
    esperado = [tabla[hid] for hid in ids]
    leer_ver = struct.Struct("<BxxxI").unpack_from

    # Reparto de las iteraciones entre hilos. Cada hilo mide `iters` completas: subir
    # la concurrencia no reduce el trabajo de nadie, aumenta la carga total. Es lo que
    # se quiere observar — cómo se degrada CADA cliente cuando hay más clientes.
    n_lotes = max(1, -(-a.iters // a.lote))        # techo de la división
    lotes_hechos = [0] * a.hilos                   # un entero por hilo: sin lock
    resultados: list[list[int] | None] = [None] * a.hilos
    errores: list[str] = []
    listos = threading.Barrier(a.hilos)            # todos miden a la vez, o no hay contención

    def trabajador(k: int) -> None:
        try:
            sock = conectar(a.host, a.port, a.reintentos, 0.05)
            buf = bytearray(a.payload)
            vista = memoryview(buf)

            # Enlaces locales: evita búsquedas de atributo en la ruta caliente.
            reloj = time.perf_counter_ns      # monótono, ns (ESPEC §2, ADR-003)
            enviar = sock.sendall
            recibir = sock.recv_into
            n_payload = a.payload

            def intercambio(estimulo: bytes) -> None:
                enviar(estimulo)
                leidos = 0
                while leidos < n_payload:
                    j = recibir(vista[leidos:], n_payload - leidos)
                    if j == 0:
                        raise ConnectionResetError("el servidor cerró la conexión")
                    leidos += j

            # --- AUTOPRUEBA: el sistema clasifica bien ANTES de medir nada ----
            # Solo el primer hilo: los demás hablan con el mismo servidor y la misma
            # tabla, así que repetirla 8 veces ensucia el log sin cerrar ningún riesgo.
            if k == 0:
                for est, esp in zip(ciclo, esperado):
                    intercambio(est)
                    v, eco = leer_ver(buf, 0)
                    hid = struct.unpack_from("<I", est, clasificador.OFF_HOST_ID)[0]
                    if v != esp or eco != hid:
                        raise SystemExit(f"error de integridad: esperaba veredicto {esp} "
                                         f"para {hid}, recibí {v} con eco {eco}")
                # El caso DESCONOCIDO — el "pepito5" de las notas del equipo.
                desconocido = clasificador.id_de_ip("203.0.113.77")   # TEST-NET-3, RFC 5737
                intercambio(clasificador.armar_estimulo(desconocido, 0, a.payload))
                v, _ = leer_ver(buf, 0)
                if v != clasificador.VEREDICTO_DESCONOCIDO:
                    raise SystemExit(f"error de integridad: un host fuera de tabla devolvió {v}")
                print("[cliente B] autoprueba OK: 16 hosts de tabla + 1 desconocido", flush=True)

            # --- WARMUP: descartado ------------------------------------------
            # Estabiliza cachés, TLB, ramp-up de frecuencia de CPU y rutas del kernel.
            for i in range(a.warmup):
                intercambio(ciclo[i & 15])

            # Nadie empieza a medir hasta que TODOS terminaron el warmup. Si no, los
            # primeros hilos medirían un tramo sin contención y la curva saldría
            # mejor de lo que es — el sesgo iría justo en la dirección que halaga.
            listos.wait(timeout=120)

            # --- MEDICIÓN, por lotes -----------------------------------------
            # El cronómetro sigue midiendo CADA intercambio (frontera F1 intacta).
            # El lote solo marca dónde es seguro tocar el contador de progreso.
            latencias = [0] * a.iters          # preasignado (ESPEC §5)
            i = 0
            for lote in range(n_lotes):
                fin = min(i + a.lote, a.iters)
                while i < fin:
                    est = ciclo[i & 15]
                    t0 = reloj()
                    intercambio(est)
                    t1 = reloj()
                    latencias[i] = t1 - t0
                    i += 1
                lotes_hechos[k] = lote + 1     # FUERA del tramo cronometrado

            sock.close()
            resultados[k] = latencias
        except BaseException as e:             # noqa: BLE001 — el hilo no puede tragárselo
            errores.append(f"hilo {k}: {e}")
            lotes_hechos[k] = n_lotes

    # --- Supervisor: informa avance sin tocar la ruta caliente ---------------
    # Lee los contadores que los hilos dejan ENTRE lotes. El plano de control lee estas
    # líneas para mostrar hilos activos y lotes procesados.
    fin_todo = threading.Event()

    def supervisor() -> None:
        while not fin_todo.wait(0.4):
            hechos = sum(lotes_hechos)
            total = n_lotes * a.hilos
            vivos = sum(1 for k in range(a.hilos) if lotes_hechos[k] < n_lotes)
            print(f"[cliente B] PROGRESO hilos={vivos}/{a.hilos} "
                  f"lotes={hechos}/{total} iters_por_lote={a.lote}", flush=True)

    print(f"[cliente B] midiendo {a.iters:,} iteraciones x {a.hilos} hilo(s) "
          f"en {n_lotes} lote(s) de {a.lote:,}…", flush=True)

    hilos = [threading.Thread(target=trabajador, args=(k,)) for k in range(a.hilos)]
    sup = threading.Thread(target=supervisor, daemon=True)
    sup.start()
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    fin_todo.set()

    if errores:
        raise SystemExit("error durante la medición:\n  " + "\n  ".join(errores))

    # --- VOLCADO: siempre al final, nunca dentro del bucle -------------------
    # La columna `hilo` va TERCERA a propósito: analyze.py lee la latencia de la
    # columna 1, así que los CSV con y sin concurrencia se analizan con la misma
    # herramienta y las corridas históricas siguen siendo legibles.
    a.out.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with a.out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["iteracion", "latencia_ns", "hilo"])
        for k, muestras in enumerate(resultados):
            for i, v in enumerate(muestras or [], start=1):
                w.writerow((i, v, k))
                total += 1
    print(f"[cliente B] {total:,} muestras ({a.hilos} hilo[s]) -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
