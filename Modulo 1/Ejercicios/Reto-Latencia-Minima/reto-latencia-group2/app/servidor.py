#!/usr/bin/env python3
"""
servidor.py — PLANO DE CONTROL del sistema.

═══════════════════════════════════════════════════════════════════════════════
LO MÁS IMPORTANTE DE ESTE ARCHIVO: ESTE PROCESO NO ES EL SISTEMA DEL RETO.

El reto pide latencia por debajo de 1 ms. Un servidor HTTP y un navegador viven
en milisegundos: si el sistema medido fuera esta aplicación web, el objetivo
estaría perdido antes de empezar.

Por eso hay DOS PLANOS, y la separación es la decisión arquitectónica del módulo:

  PLANO DE CONTROL  (este archivo + index.html)   milisegundos   NO se mide
      Formularios, listas, botones, gráficas. Pide cosas y muestra resultados.
              │
              ▼  "medí 50 000 intercambios contra la variante TCP Python"
  PLANO DE DATOS  (sistema/variante-*)            µs y ns        SÍ se mide
      cliente ⇄ servidor. EL CRONÓMETRO VIVE AQUÍ DENTRO, nunca en el navegador.

Es el mismo patrón por el que el panel de una máquina industrial no es la
máquina: la enciende, la configura y muestra sus sensores, pero el trabajo real
ocurre en otro sitio y se mide allí.

CONSECUENCIA PRÁCTICA, que el formulario de estímulos hace visible a propósito:
al pedir un estímulo desde el navegador se reportan DOS números —lo que tardó el
sistema (µs, medido aquí con reloj monótono alrededor del intercambio real) y lo
que tardó el viaje completo desde el navegador (ms). Verlos juntos es la
demostración de por qué la web no puede ser el sistema.
═══════════════════════════════════════════════════════════════════════════════

Sin dependencias: solo la biblioteca estándar de Python 3. Es deliberado — el
proyecto lo comparten tres personas y cada dependencia obliga a las tres a
instalarla. Misma razón por la que `graficas.py` no usa matplotlib.

Uso:
    python3 app/servidor.py              # http://127.0.0.1:8080
    python3 app/servidor.py --puerto 9000
"""

from __future__ import annotations

import argparse
import collections
import csv
import datetime
import itertools
import json
import math
import re
import shutil
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
SISTEMA = RAIZ / "sistema"
TABLA = SISTEMA / "tabla-hosts.csv"

TABLA_MAX = 16          # 16 x 4 B = 64 B = una línea de caché. Ver ADR-004.
PAYLOAD = 32
UMBRAL_NS = 1_000_000   # 1 ms

VEREDICTOS = {0: "EXTERNO", 1: "LOCAL", 2: "DESCONOCIDO"}

# ──────────────────────────────────────────────────────────────────────────────
# Catálogo de variantes. `socket` indica si se le puede mandar un estímulo suelto
# desde aquí: la variante Memoria compartida C usa memoria compartida y solo habla con su cliente en
# C, así que participa en las mediciones pero no en el formulario de estímulos.
# ──────────────────────────────────────────────────────────────────────────────
VARIANTES = {
    "tcp-python": {
        "nombre": "TCP Python", "puerto": 9101, "socket": True,
        "dir": "tcp-python", "servidor": ["python3", "server.py"], "cliente": ["python3", "client.py"],
        "nota": "TCP_NODELAY · conexión persistente",
    },
    "memoria-compartida-c": {
        "nombre": "Memoria compartida C", "puerto": 9103, "socket": False,
        "dir": "memoria-compartida-c", "servidor": ["./server"], "cliente": ["./client"],
        "nota": "espera activa · cero llamadas al sistema",
        "concurrencia": False,
        "porque_no": (
            "Memoria compartida C no tiene conexiones que aceptar: cliente y servidor "
            "comparten UNA region "
            "de memoria con una sola ranura por sentido. Dos clientes se pisarian el "
            "payload y podrian leer la respuesta del otro. Ademas cada proceso gira "
            "ocupando un nucleo entero, asi que 8 clientes + 8 servidores pelearian por "
            "10 nucleos.\n\n"
            "No es una limitacion de implementacion: los 83 ns se pagan con exclusividad. "
            "Compartir exige o un barrido que crece con N, o contencion atomica — y eso "
            "es justo lo que esta variante elimino para ser rapida. Ver ADR-006."),
    },
}

# Quien admite --hilos. Se declara aqui, en el catalogo, y no se deduce en la interfaz:
# el plano de control no debe ofrecer lo que el plano de datos no puede hacer.
for _v in VARIANTES.values():
    _v.setdefault("concurrencia", True)
    _v.setdefault("porque_no", "")

# Progreso de la medicion en curso. Lo alimenta el propio cliente medidor, que emite
# lineas PROGRESO entre lotes —nunca dentro del tramo cronometrado—. El plano de
# control solo las lee: no cronometra nada y no participa en la medicion.
progreso: dict = {"activa": False, "variante": None, "hilos": 0, "hilos_total": 0,
                  "lotes": 0, "lotes_total": 0}

procesos: dict[str, subprocess.Popen] = {}
conexiones: dict[str, socket.socket] = {}
candado = threading.Lock()

# ──────────────────────────────────────────────────────────────────────────────
# Historial de estímulos.
#
# Vive aquí y no solo en el navegador para que el log sobreviva a un F5 y se
# pueda descargar aunque se cierre la pestaña. Es estado en el plano de control
# —algo que en general conviene evitar— pero acotado a propósito: un buffer
# circular en memoria, sin disco, sin base de datos, que se pierde al apagar.
# El plano de datos no sabe que existe y nada de esto toca la ruta caliente.
# ──────────────────────────────────────────────────────────────────────────────
HISTORIAL_MAX = 500
historial: collections.deque = collections.deque(maxlen=HISTORIAL_MAX)
candado_hist = threading.Lock()
secuencia = itertools.count(1)


def ahora() -> str:
    """Reloj de PARED: dice a qué hora ocurrió algo. Jamás para medir duraciones."""
    return datetime.datetime.now().astimezone().isoformat(timespec="microseconds")


def anotar(entrada: dict) -> dict:
    with candado_hist:
        historial.append(entrada)
    return entrada


# ──────────────────────────────────────────────────────────────────────────────
# La tabla de hosts — el dominio (ADR-004)
# ──────────────────────────────────────────────────────────────────────────────
CABECERA = """# tabla-hosts.csv — DOMINIO del reto. Fuente unica de verdad para TODAS las variantes.
#
# Se carga UNA VEZ al arrancar cada servidor. Nunca se lee dentro del bucle de medicion.
#
# Limite duro: 16 filas. 16 x 4 bytes = 64 bytes = UNA linea de cache.
#   Ese limite es una DECISION de diseno, no una casualidad: es lo que permite
#   afirmar que la clasificacion no contamina la medicion. Ver ADR-004.
#
# veredicto: local | externo      (cualquier host ausente -> desconocido)
#
"""


def ip_valida(ip: str) -> bool:
    partes = ip.split(".")
    if len(partes) != 4:
        return False
    try:
        return all(p.isdigit() and 0 <= int(p) <= 255 for p in partes)
    except ValueError:
        return False


def leer_tabla() -> list[dict]:
    filas = []
    if not TABLA.exists():
        return filas
    with TABLA.open(newline="") as fh:
        for linea in fh:
            if linea.startswith("#") or not linea.strip():
                continue
            partes = [c.strip() for c in linea.split(",")]
            if len(partes) >= 3 and partes[0] != "nombre":
                filas.append({"nombre": partes[0], "ip": partes[1], "veredicto": partes[2]})
    return filas


def cabecera_conservada() -> str:
    """
    Devuelve los comentarios que YA tiene el CSV, no los que este archivo cree que
    deberia tener.

    Por que existe esta funcion: hasta el 15/09 se escribia `CABECERA` tal cual, y
    guardar la tabla desde la interfaz BORRABA en silencio todo comentario que no
    estuviera en esa constante. Asi se perdio la justificacion del escenario y de los
    rangos RFC 5737, y entraron IPs reales enrutables (8.8.8.8) como datos de ejemplo.

    El fondo es arquitectonico: el plano de control es EDITOR de las filas del dominio,
    no AUTOR del dominio. El razonamiento que acompana a la tabla pertenece al plano de
    datos y sobrevive a cualquier edicion hecha desde la web. `CABECERA` queda solo como
    semilla para cuando el archivo todavia no existe.
    """
    try:
        lineas = TABLA.read_text().splitlines(keepends=True)
    except OSError:
        return CABECERA
    previos = list(itertools.takewhile(lambda l: l.lstrip().startswith("#") or not l.strip(), lineas))
    return "".join(previos) or CABECERA


def escribir_tabla(filas: list[dict]) -> None:
    """Valida y reescribe el CSV. Hay que reiniciar los servidores para que lo relean."""
    if len(filas) > TABLA_MAX:
        raise ValueError(
            f"La tabla no puede pasar de {TABLA_MAX} hosts. No es un tope arbitrario: "
            f"{TABLA_MAX} × 4 B = 64 B = una línea de caché, y de ahí sale la garantía de "
            f"que clasificar cuesta ~1,9 ns. Subirlo invalidaría el ADR-004."
        )
    if not filas:
        raise ValueError("La tabla no puede quedar vacía: el sistema necesita al menos un host.")

    vistos = set()
    for f in filas:
        nombre = (f.get("nombre") or "").strip()
        ip = (f.get("ip") or "").strip()
        ver = (f.get("veredicto") or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,32}", nombre):
            raise ValueError(f"Nombre inválido: «{nombre}». Use letras, números, punto, guion o guion bajo.")
        if not ip_valida(ip):
            raise ValueError(f"«{ip}» no es una IPv4 válida. Cada número va de 0 a 255.")
        if ver not in ("local", "externo"):
            raise ValueError(f"Veredicto inválido: «{ver}». Solo «local» o «externo».")
        if nombre in vistos:
            raise ValueError(f"El host «{nombre}» está repetido.")
        vistos.add(nombre)

    with TABLA.open("w", newline="") as fh:
        fh.write(cabecera_conservada())
        fh.write("nombre,ip,veredicto\n")
        for f in filas:
            fh.write(f"{f['nombre'].strip()},{f['ip'].strip()},{f['veredicto'].strip()}\n")


def id_de_ip(ip: str) -> int:
    return struct.unpack("<I", socket.inet_aton(ip))[0]


# ──────────────────────────────────────────────────────────────────────────────
# Ciclo de vida de los servidores del plano de datos
# ──────────────────────────────────────────────────────────────────────────────
WINDOWS = sys.platform.startswith("win")


def resolver_cmd(cmd: list[str], d: Path) -> list[str]:
    """
    Traduce un comando del catalogo al de ESTE sistema operativo.

    El catalogo VARIANTES se escribe en notacion POSIX (`python3`, `./server`) porque
    ese es el entorno de referencia donde se mide. Traducir aqui, en un solo sitio,
    evita que el catalogo se llene de condicionales por sistema —que es como empiezan
    a divergir dos versiones de la misma verdad.

      python3    -> sys.executable, el MISMO interprete que corre el plano de control.
                    En Windows el ejecutable se llama `python`, y usar `sys.executable`
                    ademas garantiza que servidor y variante compartan version.
      ./server   -> ruta absoluta, con .exe en Windows.
    """
    cmd = list(cmd)
    if cmd[0] == "python3":
        cmd[0] = sys.executable
    elif cmd[0].startswith("./"):
        exe = d / cmd[0][2:]
        if WINDOWS:
            exe = exe.with_suffix(".exe")
        cmd[0] = str(exe)
    return cmd


def como_liberar_puerto(puerto: int) -> str:
    """El comando para ver quien tiene un puerto, en el sistema de quien lee el error."""
    if WINDOWS:
        return (f"Ver quien lo tiene:\n  netstat -ano | findstr :{puerto}\n\n"
                f"Liberarlo (con el PID de la ultima columna):\n  taskkill /PID <pid> /F")
    return (f"Ver quien lo tiene:\n  lsof -nP -iTCP:{puerto} -sTCP:LISTEN\n\n"
            f"Liberarlo:\n  kill $(lsof -t -iTCP:{puerto} -sTCP:LISTEN)")


def puerto_ocupado(puerto: int) -> bool:
    """
    ¿Alguien tiene ya ese puerto? Se responde intentando bindearlo nosotros, que
    es exactamente la pregunta que el servidor hará un instante después.

    Sondearlo con connect_ex NO sirve: al ponerle timeout el socket queda en modo
    no bloqueante y devuelve EINPROGRESS/EAGAIN en vez de 0, así que un puerto
    ocupado se veía libre. SO_REUSEADDR deja rebindear un TIME_WAIT —que no
    estorba— pero nunca un LISTEN vivo, que es justo lo que queremos detectar.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", puerto))
            return False
        except OSError:
            return True


def compilar(vid: str):
    d = SISTEMA / VARIANTES[vid]["dir"]
    if not (d / "Makefile").exists():
        return None
    if shutil.which("make") is None:
        # Camino Windows nativo: no hay cadena de compilacion. Es un escenario
        # PREVISTO (ver README, "tres caminos"), no un fallo: el plano de control y
        # las variantes en Python funcionan igual. Se dice que falta y como tenerlo.
        return ("Esta variante esta escrita en C y aqui no hay compilador (`make`).\n\n"
                "En Windows, las variantes en C y la medicion oficial necesitan WSL2:\n"
                "  wsl --install\n\n"
                "Sin WSL2 podes usar igual el plano de control y las variantes en Python.\n"
                "Ver README.md, seccion «Tres caminos».")
    r = subprocess.run(["make"], cwd=d, capture_output=True, text=True)
    return None if r.returncode == 0 else (r.stderr or r.stdout)[-800:]


def arrancar(vid: str) -> dict:
    v = VARIANTES[vid]
    d = SISTEMA / v["dir"]
    with candado:
        if vid in procesos and procesos[vid].poll() is None:
            return {"ok": True, "aviso": "ya estaba corriendo"}

        # Un servidor huerfano de una sesion anterior sigue escuchando: pasa cada vez
        # que se cierra la terminal sin Ctrl-C. El bind fallaria con un
        # "Address already in use" que no dice nada; mejor decir que pasa y como salir.
        if puerto_ocupado(v["puerto"]):
            time.sleep(0.3)                      # margen por si acabamos de pararlo
            if puerto_ocupado(v["puerto"]):
                return {"ok": False, "error": (
                    f"El puerto {v['puerto']} ya esta ocupado, y no por un proceso de este plano de "
                    f"control. Casi siempre es un servidor huerfano de una sesion anterior.\n\n"
                    + como_liberar_puerto(v['puerto']))}

        err = compilar(vid)
        if err:
            return {"ok": False, "error": f"No compila:\n{err}"}

        declarado = list(v["servidor"])
        cmd = resolver_cmd(declarado, d)
        if declarado[0] == "./server" and not Path(cmd[0]).exists():
            return {"ok": False, "error": f"Falta el binario {v['dir']}/server."}
        if declarado[0] == "python3" and not (d / declarado[1]).exists():
            return {"ok": False, "error": f"Falta {v['dir']}/{cmd[1]} — esta variante todavía no está implementada."}

        cmd += ["--port", str(v["puerto"]), "--tabla", str(TABLA)]
        try:
            p = subprocess.Popen(cmd, cwd=d, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True)
        except OSError as e:
            return {"ok": False, "error": str(e)}
        procesos[vid] = p
        time.sleep(0.7)
        if p.poll() is not None:
            salida = (p.stdout.read() if p.stdout else "")[-800:]
            return {"ok": False, "error": f"El servidor murió al arrancar:\n{salida}"}
    return {"ok": True}


def parar(vid: str) -> dict:
    with candado:
        s = conexiones.pop(vid, None)
        if s:
            try:
                s.close()
            except OSError:
                pass
        p = procesos.pop(vid, None)
        if p and p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                p.kill()
    return {"ok": True}


def corriendo(vid: str) -> bool:
    p = procesos.get(vid)
    return bool(p and p.poll() is None)


# ──────────────────────────────────────────────────────────────────────────────
# Un estímulo suelto — el formulario de la interfaz
# ──────────────────────────────────────────────────────────────────────────────
def conexion(vid: str) -> socket.socket:
    """Conexión persistente: el handshake se paga una vez, fuera de la medición (F1)."""
    s = conexiones.get(vid)
    if s is not None:
        return s
    s = socket.create_connection(("127.0.0.1", VARIANTES[vid]["puerto"]), timeout=3.0)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    conexiones[vid] = s
    return s


def estimulo_por_cliente(v: dict, ip: str) -> tuple:
    """
    Un estimulo contra una variante que no habla por sockets: se lanza SU cliente
    con `--clasificar`, que hace un solo intercambio y reporta el veredicto.

    Por que asi y no manteniendo un cliente residente: la region compartida tiene
    UNA ranura por sentido. Un cliente permanente del plano de control la ocupa, y
    si alguien lanza una medicion a la vez, los dos se pisan el payload y la corrida
    sale contaminada SIN dar error. Por eso este camino es de usar y tirar, y por eso
    se niega a correr mientras haya una medicion en curso.

    El precio es el arranque del proceso (milisegundos). No entra en la cifra del
    reto: la latencia que se devuelve la mide el cliente entre sus dos marcas de la
    frontera F1, igual que en una corrida.
    """
    if progreso.get("activa"):
        raise RuntimeError(
            "Hay una medicion en curso. Esta variante tiene una sola ranura de memoria "
            "compartida: mandar un estimulo ahora corromperia la medicion. Espera a que "
            "termine.")

    d = SISTEMA / v["dir"]
    cmd = resolver_cmd(v["cliente"], d) + [
        "--clasificar", ip, "--port", str(v["puerto"]), "--tabla", str(TABLA),
    ]
    try:
        r = subprocess.run(cmd, cwd=d, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        raise RuntimeError("El cliente no respondio en 30 s.")

    linea = next((l for l in r.stdout.splitlines() if l.startswith("ESTIMULO ")), None)
    if linea is None:
        detalle = (r.stderr or r.stdout or "").strip().splitlines()
        raise RuntimeError("El cliente no devolvio un veredicto. "
                           + (detalle[-1] if detalle else f"codigo {r.returncode}"))

    campos = dict(par.split("=", 1) for par in linea.split() if "=" in par)
    try:
        return int(campos["veredicto"]), int(campos["latencia_ns"])
    except (KeyError, ValueError):
        raise RuntimeError(f"No se entiende la respuesta del cliente: {linea}")


def estimulo(vid: str, host: str) -> dict:
    """
    Manda UN estímulo y devuelve el veredicto con el log completo de tiempos.

    DOS RELOJES, Y NO SE MEZCLAN (ADR-003):

      · reloj MONÓTONO (time.perf_counter_ns) — origen arbitrario, no retrocede,
        no lo mueve NTP. Es el único del que salen DURACIONES.
      · reloj de PARED (datetime.now) — dice a qué hora pasó algo, sirve para
        correlacionar con otros logs, y no sirve para medir.

    Restar un reloj contra otro —o el del servidor contra el del navegador, que
    ni siquiera están sincronizados— da un número sin significado. Por eso cada
    campo del registro lleva de qué reloj vino, y las restas se hacen siempre
    dentro de un mismo reloj.

    La frontera F1 (ADR-001) sigue siendo exactamente las mismas dos líneas:
    t0 antes del sendall, t1 tras leer los 32 bytes completos. Las marcas nuevas
    se toman FUERA de ese par, nunca entre medio: el cronómetro del reto no se
    ensancha ni un nanosegundo por tener mejor logging.
    """
    seq = next(secuencia)
    ts_recibe = ahora()
    t_entra = time.perf_counter_ns()          # monótono, para el overhead del control

    base = {"seq": seq, "ts_control_recibe": ts_recibe, "variante": vid,
            "nombre_variante": VARIANTES[vid]["nombre"], "host": host}

    def fallo(texto):
        return anotar(dict(base, ok=False, error=texto, ts_control_responde=ahora(),
                           veredicto=None, ip=None, latencia_sistema_ns=None,
                           control_overhead_ns=None, t0_f1_ns=None, t1_f1_ns=None))

    v = VARIANTES[vid]
    if not corriendo(vid):
        return fallo(f"El servidor de la variante {vid} no está corriendo.")

    filas = leer_tabla()
    ip = next((f["ip"] for f in filas if f["nombre"] == host), host)
    if not ip_valida(ip):
        # Ni está en la tabla ni es una IP: es el caso «pepito5» de las notas del
        # equipo. Se resuelve sin tocar el plano de datos, así que no hay F1 que
        # medir: la latencia del sistema queda en null, no en cero.
        return anotar(dict(base, ok=True, ip=None, veredicto="DESCONOCIDO",
                           latencia_sistema_ns=None, t0_f1_ns=None, t1_f1_ns=None,
                           control_overhead_ns=time.perf_counter_ns() - t_entra,
                           ts_control_responde=ahora(),
                           nota="no está en la tabla y tampoco es una IPv4 · "
                                "resuelto en el plano de control, sin viaje al plano de datos"))

    if not v["socket"]:
        # Esta variante no tiene conexiones que aceptar (ADR-002): se le habla
        # lanzando su propio cliente en C, una vez por estimulo. Ver ADR-009.
        try:
            ver_byte, latencia = estimulo_por_cliente(v, ip)
        except Exception as e:                                  # noqa: BLE001
            return fallo(str(e))
        total_control = time.perf_counter_ns() - t_entra
        return anotar(dict(
            base, ok=True, ip=ip, veredicto=VEREDICTOS.get(ver_byte, "?"),
            t0_f1_ns=None, t1_f1_ns=None,
            latencia_sistema_ns=latencia,
            control_overhead_ns=total_control - latencia,
            ts_control_responde=ahora(),
            nota="estimulo suelto: el cliente arranca en frio, sin warmup, y mide UN "
                 "intercambio. Sirve para ver que clasifica, no para comparar con el "
                 "p50 del informe, que sale de un millon de intercambios en caliente."))

    host_id = id_de_ip(ip)
    msg = struct.pack("<II", host_id, 0) + b"\x00" * (PAYLOAD - 8)
    buf = bytearray(PAYLOAD)
    vista = memoryview(buf)

    try:
        with candado:
            s = conexion(vid)
            # ── frontera F1: el cronómetro empieza y termina aquí ─────────────
            t0 = time.perf_counter_ns()
            s.sendall(msg)
            leidos = 0
            while leidos < PAYLOAD:
                k = s.recv_into(vista[leidos:], PAYLOAD - leidos)
                if k == 0:
                    raise ConnectionResetError("el servidor cerró la conexión")
                leidos += k
            t1 = time.perf_counter_ns()
            # ─────────────────────────────────────────────────────────────────
    except OSError as e:
        conexiones.pop(vid, None)
        return fallo(f"Error de transporte: {e}")

    veredicto, eco = struct.unpack_from("<BxxxI", buf, 0)
    if eco != host_id:
        return fallo("Error de integridad: el eco no coincide con lo enviado.")

    latencia = t1 - t0
    total_control = time.perf_counter_ns() - t_entra
    return anotar(dict(
        base, ok=True, ip=ip, veredicto=VEREDICTOS.get(veredicto, "?"),
        t0_f1_ns=t0, t1_f1_ns=t1,
        latencia_sistema_ns=latencia,            # lo único que cuenta para el reto
        control_overhead_ns=total_control - latencia,  # misma resta, mismo reloj
        ts_control_responde=ahora()))



# ──────────────────────────────────────────────────────────────────────────────
# Una medición de verdad — lanza el cliente real del plano de datos
# ──────────────────────────────────────────────────────────────────────────────
def percentiles(m: list) -> dict:
    m.sort()
    n = len(m)

    def p(q):
        return m[min(n - 1, int(n * q / 100.0))]

    hist = [0] * 84
    for x in m:
        b = 0 if x <= 0 else int((math.log10(x) - 1) * 12)
        hist[max(0, min(83, b))] += 1

    return {"n": n, "min": m[0], "p50": p(50), "p75": p(75), "p90": p(90),
            "p99": p(99), "p999": p(99.9), "p9999": p(99.99), "max": m[-1],
            "sobre1ms": sum(1 for x in m if x > UMBRAL_NS), "hist": hist}


def medir(vid: str, iters, hilos: int = 1) -> dict:
    """
    Corre el cliente REAL de la variante. Aquí no se mide nada desde Python: se
    lanza el mismo binario que produce los resultados del informe y se leen sus
    muestras. La única diferencia con `run.sh` es quién aprieta el botón.
    """
    if not corriendo(vid):
        return {"ok": False, "error": f"Arrancá primero el servidor de la variante {vid}."}

    v = VARIANTES[vid]
    d = SISTEMA / v["dir"]

    # Los servidores atienden UNA conexión a la vez: es lo correcto para el reto
    # (un solo cliente, una petición en vuelo — supuesto S2), pero significa que la
    # conexión persistente del formulario de estímulos dejaría al cliente medidor
    # esperando para siempre. Se suelta antes de medir y se vuelve a abrir sola.
    with candado:
        s = conexiones.pop(vid, None)
        if s:
            try:
                s.close()
            except OSError:
                pass

    try:
        iters = max(1000, min(int(iters), 1_000_000))
    except (TypeError, ValueError):
        iters = 50_000
    warmup = max(500, iters // 10)

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        salida = Path(tmp.name)

    cmd = resolver_cmd(v["cliente"], d) + [
        "--port", str(v["puerto"]), "--tabla", str(TABLA),
        "--warmup", str(warmup), "--iters", str(iters), "--out", str(salida),
    ]
    if hilos > 1:
        if not v.get("concurrencia", True):
            return {"ok": False, "error":
                    f"La variante {vid} no admite clientes concurrentes.\n\n"
                    + v.get("porque_no", "")}
        cmd += ["--hilos", str(hilos)]

    # Popen y no subprocess.run: con `run` no hay salida hasta que el proceso termina,
    # y entonces no habria nada que mostrar mientras la medicion ocurre.
    t0 = time.perf_counter()
    progreso.update({"activa": True, "variante": vid, "hilos": hilos,
                     "hilos_total": hilos, "lotes": 0, "lotes_total": 0})
    lineas: list[str] = []
    try:
        proc = subprocess.Popen(cmd, cwd=d, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, bufsize=1)
        for linea in proc.stdout:
            lineas.append(linea)
            if "PROGRESO" in linea:
                campos = dict(par.split("=", 1) for par in linea.split() if "=" in par)
                try:
                    vivos, _ = campos.get("hilos", "0/0").split("/")
                    hechos, total = campos.get("lotes", "0/0").split("/")
                    progreso.update({"hilos": int(vivos), "lotes": int(hechos),
                                     "lotes_total": int(total)})
                except ValueError:
                    pass
        codigo = proc.wait(timeout=300)
    finally:
        # Al cerrar, el contador salta al total: el ultimo reporte del supervisor cae
        # hasta 0,4 s antes del final, y dejar "152 de 160" en pantalla sugiere que
        # algo quedo a medias cuando en realidad termino entero.
        progreso.update({"activa": False, "hilos": 0,
                         "lotes": progreso.get("lotes_total", 0) or progreso.get("lotes", 0)})
    dur = time.perf_counter() - t0
    r_salida = "".join(lineas)

    if codigo != 0:
        salida.unlink(missing_ok=True)
        return {"ok": False, "error": (r_salida or "el cliente falló")[-800:]}

    muestras = []
    with salida.open(newline="") as fh:
        rd = csv.reader(fh)
        next(rd, None)
        for fila in rd:
            if len(fila) >= 2:
                try:
                    muestras.append(int(fila[1]))
                except ValueError:
                    pass
    salida.unlink(missing_ok=True)

    if not muestras:
        return {"ok": False, "error": "El cliente no produjo muestras."}

    res = percentiles(muestras)
    res.update({"ok": True, "variante": vid, "nombre": v["nombre"], "warmup": warmup,
                "segundos": round(dur, 2), "consola": (r_salida or "")[-1200:]})
    return res


# ──────────────────────────────────────────────────────────────────────────────
# HTTP
# ──────────────────────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    server_version = "PlanoDeControl/1.0"

    def log_message(self, fmt, *args):
        pass  # sin ruido en la consola

    def _json(self, datos, codigo=200):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def _cuerpo(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}") if n else {}

    def do_GET(self):
        ruta = self.path.split("?")[0]
        if ruta in ("/", "/index.html"):
            return self._archivo(AQUI / "index.html", "text/html; charset=utf-8")
        if ruta == "/api/estado":
            return self._json({
                "progreso": dict(progreso),
                "variantes": [{
                    "id": k, "nombre": v["nombre"], "puerto": v["puerto"],
                    "socket": v["socket"], "nota": v["nota"],
                    "concurrencia": v.get("concurrencia", True),
                    "porque_no": v.get("porque_no", ""),
                    "corriendo": corriendo(k),
                    "existe": (SISTEMA / v["dir"] / "server.py").exists()
                              or (SISTEMA / v["dir"] / "Makefile").exists(),
                } for k, v in VARIANTES.items()],
                "tabla": leer_tabla(),
                "limite": TABLA_MAX,
            })
        if ruta == "/api/tabla":
            return self._json({"ok": True, "tabla": leer_tabla(), "limite": TABLA_MAX})
        if ruta == "/api/historial":
            with candado_hist:
                return self._json({"ok": True, "historial": list(historial),
                                   "limite": HISTORIAL_MAX})
        self.send_error(404)

    def do_PUT(self):
        if self.path == "/api/tabla":
            try:
                escribir_tabla(self._cuerpo().get("tabla", []))
            except (ValueError, KeyError, TypeError, AttributeError) as e:
                return self._json({"ok": False, "error": str(e)}, 400)
            # La tabla se carga al arrancar: para que el cambio tenga efecto hay que
            # reiniciar. Es el precio de NO releer el archivo en la ruta caliente.
            reiniciados = [k for k in list(procesos) if corriendo(k)]
            for k in reiniciados:
                parar(k)
                arrancar(k)
            return self._json({"ok": True, "tabla": leer_tabla(), "reiniciados": reiniciados})
        self.send_error(404)

    def do_POST(self):
        try:
            cuerpo = self._cuerpo()
        except json.JSONDecodeError:
            return self._json({"ok": False, "error": "JSON inválido"}, 400)

        if self.path == "/api/servidor":
            vid = cuerpo.get("variante")
            if vid not in VARIANTES:
                return self._json({"ok": False, "error": "variante desconocida"}, 400)
            return self._json(arrancar(vid) if cuerpo.get("accion") == "arrancar" else parar(vid))

        if self.path == "/api/historial":
            if cuerpo.get("accion") == "limpiar":
                with candado_hist:
                    historial.clear()
                return self._json({"ok": True, "historial": []})
            return self._json({"ok": False, "error": "acción desconocida"}, 400)

        if self.path == "/api/estimulo":
            vid = cuerpo.get("variante")
            host = (cuerpo.get("host") or "").strip()
            if vid not in VARIANTES:
                return self._json({"ok": False, "error": "variante desconocida"}, 400)
            if not host:
                return self._json({"ok": False, "error": "Escribí un host o una IP."}, 400)
            return self._json(estimulo(vid, host))

        if self.path == "/api/medir":
            vid = cuerpo.get("variante")
            if vid not in VARIANTES:
                return self._json({"ok": False, "error": "variante desconocida"}, 400)
            try:
                return self._json(medir(vid, cuerpo.get("iters", 50000),
                                        max(1, min(32, int(cuerpo.get("hilos", 1))))))
            except subprocess.TimeoutExpired:
                return self._json({"ok": False, "error": "La medición superó los 5 minutos."}, 504)

        self.send_error(404)

    def _archivo(self, ruta: Path, tipo: str):
        if not ruta.exists():
            return self.send_error(404)
        datos = ruta.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(datos)


def apagar(*_):
    print("\nbajando los servidores del plano de datos…", flush=True)
    for k in list(procesos):
        parar(k)
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser(description="Plano de control del sistema clasificador de hosts")
    ap.add_argument("--puerto", type=int, default=8080)
    a = ap.parse_args()

    if not TABLA.exists():
        sys.exit(f"error: no encuentro {TABLA}\n"
                 f"Ejecutalo desde la raíz del proyecto:  python3 app/servidor.py")

    # SIGHUP incluido: cerrar la ventana de la terminal es justo el caso que dejaba
    # servidores huerfanos escuchando y bloqueaba el siguiente arranque.
    for sig in ("SIGINT", "SIGTERM", "SIGHUP"):
        if hasattr(signal, sig):
            signal.signal(getattr(signal, sig), apagar)

    print()
    print("  ┌────────────────────────────────────────────────────────────┐")
    print("  │  PLANO DE CONTROL                                          │")
    print(f"  │  http://127.0.0.1:{a.puerto}".ljust(62) + "│")
    print("  │                                                            │")
    print("  │  Este proceso NO es el sistema del reto: lo enciende y      │")
    print("  │  muestra sus mediciones. El cronómetro vive en el plano     │")
    print("  │  de datos (sistema/variante-*), nunca en el navegador.      │")
    print("  │                                                            │")
    print("  │  Ctrl-C para bajar todo.                                    │")
    print("  └────────────────────────────────────────────────────────────┘")
    print(flush=True)

    ThreadingHTTPServer(("127.0.0.1", a.puerto), Handler).serve_forever()


if __name__ == "__main__":
    main()
