#!/usr/bin/env python3
"""
verificar.py — el contrato de trabajo del proyecto.

Comprueba los invariantes que sostienen las conclusiones del informe. No es un
test de que el codigo funcione: es un test de que el EXPERIMENTO sigue siendo
valido. Un sistema puede funcionar perfectamente y a la vez haber dejado de medir
lo que dice medir.

Cada invariante aqui existe porque romperlo INVALIDA algo en silencio —sin error,
sin caida, sin que nadie se entere hasta que alguien pregunta en la sustentacion—.
Por eso la salida no dice solo que fallo: dice que conclusion del informe deja de
sostenerse y en que ADR esta la decision.

LIMITE HONESTO: mientras el proyecto no este en un repositorio, esto DETECTA, no
IMPIDE. Se corre antes de dar algo por terminado y antes de empaquetar. El dia que
haya repositorio, el mismo archivo se engancha como hook de pre-commit sin cambiar
una linea.

    python3 verificar.py              comprueba
    python3 verificar.py --registrar  fija los hashes actuales como referencia
"""
from __future__ import annotations

import csv
import hashlib
import ipaddress
import json
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SISTEMA = AQUI / "sistema"
TABLA = SISTEMA / "tabla-hosts.csv"
REGISTRO = AQUI / "contrato" / "invariantes.json"

TABLA_MAX = 16
PAYLOAD = 32

# Archivos que fijan el METODO. Cambiarlos no es un cambio de codigo: es un cambio
# de experimento, y exige registrar la decision antes de que los numeros nuevos
# puedan compararse con los viejos.
VIGILADOS = {
    "sistema/reloj.h": ("AC-3 · comparabilidad entre variantes", "ADR-003"),
    "sistema/clasificador.h": ("el dominio y el formato de 32 bytes", "ADR-004"),
    "sistema/clasificador.py": ("el dominio en las variantes interpretadas", "ADR-004"),
}

# Rangos que SI pueden aparecer como datos de ejemplo: no pertenecen a nadie y no
# enrutan. Poner una IP real en la tabla la convierte en un dato sobre un tercero.
RESERVADOS = [
    ipaddress.ip_network("10.0.0.0/8"),        # RFC 1918
    ipaddress.ip_network("172.16.0.0/12"),     # RFC 1918
    ipaddress.ip_network("192.168.0.0/16"),    # RFC 1918
    ipaddress.ip_network("192.0.2.0/24"),      # RFC 5737 TEST-NET-1
    ipaddress.ip_network("198.51.100.0/24"),   # RFC 5737 TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),    # RFC 5737 TEST-NET-3
    ipaddress.ip_network("127.0.0.0/8"),       # loopback
    ipaddress.ip_network("169.254.0.0/16"),    # RFC 3927 link-local
]

fallos: list[str] = []
avisos: list[str] = []


def bien(t: str) -> None:
    print(f"  ok     {t}")


def mal(titulo: str, porque: str, adr: str = "") -> None:
    print(f"  FALLA  {titulo}")
    for l in porque.splitlines():
        print(f"         {l}")
    if adr:
        print(f"         decision: {adr}")
    fallos.append(titulo)


def aviso(titulo: str, porque: str = "") -> None:
    print(f"  aviso  {titulo}")
    for l in porque.splitlines():
        print(f"         {l}")
    avisos.append(titulo)


def sha(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()[:16]


def filas_tabla() -> list[tuple[str, str, str]]:
    filas = []
    with TABLA.open(newline="") as fh:
        for f in csv.reader(l for l in fh if not l.startswith("#") and l.strip()):
            if len(f) >= 3 and f[0].strip() != "nombre":
                filas.append((f[0].strip(), f[1].strip(), f[2].strip()))
    return filas


# ── 1 · El tamano de la tabla es una decision, no un detalle ─────────────────
def inv_tamano_tabla() -> None:
    filas = filas_tabla()
    n = len(filas)
    if n > TABLA_MAX:
        mal(f"la tabla tiene {n} hosts (limite {TABLA_MAX})",
            f"{TABLA_MAX} x 4 B = 64 B = una linea de cache. Pasarse saca la tabla de L1,\n"
            "los fallos de cache meten varianza en los percentiles altos, y entonces\n"
            "'clasificar no contamina la medicion' deja de ser cierto.",
            "ADR-004")
    else:
        bien(f"la tabla cabe en una linea de cache ({n}/{TABLA_MAX} hosts = {n*4} B)")


# ── 2 · Los datos de ejemplo no hablan de terceros ───────────────────────────
def inv_direcciones() -> None:
    malas = []
    for nombre, ip, _ in filas_tabla():
        try:
            dir_ip = ipaddress.ip_address(ip)
        except ValueError:
            malas.append(f"{nombre}: '{ip}' no es una IPv4 valida")
            continue
        if not any(dir_ip in r for r in RESERVADOS):
            malas.append(f"{nombre}: {ip} es una direccion real y enrutable")
    if malas:
        mal("hay direcciones reales en la tabla del dominio",
            "\n".join(malas) + "\n"
            "Los datos de ejemplo van en rangos reservados (RFC 1918 para la lista\n"
            "blanca, RFC 5737 para la negra): no pertenecen a nadie y no enrutan.\n"
            "Una IP real convierte un ejemplo en una afirmacion sobre un tercero —y en\n"
            "un caso de control de acceso, en una acusacion—.",
            "ADR-004")
    else:
        bien("todas las direcciones estan en rangos reservados (RFC 1918 / 5737)")


# ── 3 · El instrumento de medicion no cambia sin dejar constancia ────────────
def inv_metodo_estable(registrar: bool) -> None:
    registro = json.loads(REGISTRO.read_text()) if REGISTRO.exists() else {}
    actuales = {r: sha(AQUI / r) for r in VIGILADOS if (AQUI / r).exists()}

    if registrar:
        REGISTRO.parent.mkdir(exist_ok=True)
        REGISTRO.write_text(json.dumps(actuales, indent=2, ensure_ascii=False) + "\n")
        print(f"  registrado  {len(actuales)} archivos del metodo en {REGISTRO.relative_to(AQUI)}")
        return

    if not registro:
        aviso("no hay hashes de referencia del metodo",
              "Corre:  python3 verificar.py --registrar")
        return

    for ruta, hash_actual in actuales.items():
        motivo, adr = VIGILADOS[ruta]
        if registro.get(ruta) != hash_actual:
            mal(f"{ruta} cambio desde la ultima referencia",
                f"Este archivo fija {motivo}.\n"
                "Cambiarlo no es un cambio de codigo, es un cambio de EXPERIMENTO: las\n"
                "mediciones anteriores dejan de ser comparables con las nuevas.\n"
                "Si el cambio es intencionado: registra un ADR, vuelve a medir lo que\n"
                "haga falta, y despues corre `python3 verificar.py --registrar`.",
                adr)
        else:
            bien(f"{ruta} sin cambios ({motivo})")


# ── 4 · C y Python clasifican igual ──────────────────────────────────────────
def inv_coherencia_clasificadores() -> None:
    binario = AQUI / "contrato" / ("coherencia.exe" if sys.platform.startswith("win") else "coherencia")
    fuente = AQUI / "contrato" / "coherencia.c"
    compilador = next((c for c in ("cc", "gcc", "clang") if shutil.which(c)), None)

    if not binario.exists():
        if not compilador:
            aviso("coherencia C/Python: no se pudo comprobar (no hay compilador)",
                  "Es lo esperado en Windows nativo. En WSL2 o macOS si se comprueba.")
            return
        r = subprocess.run([compilador, "-O2", "-I", str(SISTEMA), "-o", str(binario), str(fuente)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            mal("no compila contrato/coherencia.c", (r.stderr or r.stdout)[-400:])
            return

    sys.path.insert(0, str(SISTEMA))
    import clasificador  # noqa: E402

    tabla = clasificador.cargar(TABLA)
    casos = [ip for _, ip, _ in filas_tabla()]
    casos += ["203.0.113.1", "10.255.255.254", "127.0.0.1", "192.0.2.99"]  # ausentes a proposito

    r = subprocess.run([str(binario), str(TABLA)], input="\n".join(casos) + "\n",
                       capture_output=True, text=True)
    if r.returncode != 0:
        mal("el comprobador de coherencia fallo", (r.stderr or r.stdout)[-400:])
        return

    desacuerdos = []
    for linea in r.stdout.splitlines():
        ip, _, ver_c = linea.partition(" ")
        ver_py = clasificador.NOMBRE_VEREDICTO[
            tabla.get(clasificador.id_de_ip(ip), clasificador.VEREDICTO_DESCONOCIDO)]
        if ver_c != ver_py:
            desacuerdos.append(f"{ip}: C dice {ver_c}, Python dice {ver_py}")

    if desacuerdos:
        mal("los clasificadores de C y Python NO coinciden",
            "\n".join(desacuerdos) + "\n"
            "B clasifica con clasificador.py y D con clasificador.h. Si los dos dejan\n"
            "de coincidir, B y D hacen trabajos distintos y la unica comparacion que\n"
            "queda en pie deja de decir lo que el informe afirma que dice.",
            "ADR-004")
    else:
        bien(f"C y Python clasifican igual ({len(casos)} casos, incluidos ausentes)")


# ── 5 · El formato de cable sigue siendo de 32 bytes ─────────────────────────
def inv_payload() -> None:
    sospechosas = []
    for d in sorted(SISTEMA.glob("variante-*")) + sorted(SISTEMA.glob("control-*")):
        fuentes = list(d.glob("*.py")) + list(d.glob("*.c"))
        if not fuentes:
            continue
        texto = "\n".join(f.read_text(errors="ignore") for f in fuentes)
        if "PAYLOAD" in texto or str(PAYLOAD) in texto:
            continue
        sospechosas.append(d.name)
    if sospechosas:
        aviso("no se encontro rastro del payload de 32 B en: " + ", ".join(sospechosas),
              "Revisar a mano. El contrato es 32 B en ambos sentidos (ADR-004).")
    else:
        bien(f"todas las variantes implementadas usan el payload de {PAYLOAD} B")


# ── 6 y 7 · La evidencia del informe se puede rastrear ───────────────────────
def inv_evidencia() -> None:
    resultados = SISTEMA / "resultados"
    if not resultados.exists():
        aviso("todavia no hay resultados")
        return
    csvs = sorted(resultados.glob("resultados-*.csv"))
    huerfanos = [c.name for c in csvs
                 if not (resultados / c.name.replace("resultados-", "ejecucion-").replace(".csv", ".log")).exists()]
    if huerfanos:
        mal(f"{len(huerfanos)} CSV sin su log de ejecucion",
            ", ".join(huerfanos[:6]) + ("..." if len(huerfanos) > 6 else "") + "\n"
            "El log es lo unico que dice EN QUE MAQUINA se tomo la corrida. Sin el, la\n"
            "cifra no se puede atribuir a una plataforma y analyze.py no puede impedir\n"
            "que se compare con corridas de otra.",
            "ADR-005")
    else:
        bien(f"los {len(csvs)} CSV de resultados tienen su log con la plataforma")


# ── 8 · Una sola copia del plano de datos ────────────────────────────────────
def inv_copia_unica() -> None:
    padre = AQUI.parent
    gemelas = [d for d in padre.iterdir()
               if d.is_dir() and d != AQUI and (d / "clasificador.h").exists()]
    if gemelas:
        mal("hay otra copia del plano de datos: " + ", ".join(d.name for d in gemelas),
            "Dos copias divergen en silencio. Ya paso el 14/09: las dos tablas del\n"
            "dominio dejaron de coincidir y la que se empaqueto era la que habia perdido\n"
            "la justificacion de sus direcciones.\n"
            "La fuente unica de verdad es este directorio.")
    else:
        bien("una sola copia del plano de datos")


def main() -> int:
    registrar = "--registrar" in sys.argv
    print()
    print("  Contrato de trabajo — Reto de Latencia Minima")
    print("  " + "-" * 62)
    print()

    inv_tamano_tabla()
    inv_direcciones()
    inv_metodo_estable(registrar)
    if not registrar:
        inv_coherencia_clasificadores()
        inv_payload()
        inv_evidencia()
        inv_copia_unica()

    print()
    print("  " + "-" * 62)
    if fallos:
        print(f"  {len(fallos)} invariante(s) roto(s). Cada uno invalida algo del informe.")
        print("  Arreglalo, o registra un ADR explicando por que el experimento cambio.")
        print()
        return 1
    print(f"  Todo en orden{f' ({len(avisos)} aviso[s])' if avisos else ''}.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
