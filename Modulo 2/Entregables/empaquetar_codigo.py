"""Arma el ZIP del código fuente del Reto 2 (entregable 1 del enunciado).

Uso, desde cualquier carpeta del repo:  python3 "Modulo 2/Entregables/empaquetar_codigo.py"

- Parte de `git ls-files`: solo entra lo versionado. Así quedan fuera `.env`, `.env.aws`, `.venv/`,
  `logs/` y cachés sin tener que listarlos.
- Excluye `docs/` del sistema local: son el diseño y el plan internos del equipo, no el entregable.
- Limpia notas internas con reemplazos EXACTOS. Si un texto ya no aparece (alguien cambió el código),
  el script falla en vez de empaquetar la nota en silencio: hay que actualizar LIMPIEZA.
- Las Lambdas se copian del aporte de Camilo sin tocar su lógica. Solo se limpia el docstring de la
  ingesta, que describe pasos del despliegue ya terminados. Su aporte firmado no se modifica.
"""
import subprocess
import sys
import zipfile
from pathlib import Path

ENTREGABLES = Path(__file__).resolve().parent
MODULO = ENTREGABLES.parent
LOCAL = MODULO / "Ejercicios" / "Reto2-Alerta-Flota"
LAMBDAS = MODULO / "Aportes" / "camilo" / "m2-aws-opcion-b-camilo"
EMPAQUE = ENTREGABLES / "empaque"
RAIZ_ZIP = "reto2-codigo-grupo2"
DESTINO = ENTREGABLES / f"{RAIZ_ZIP}.zip"

EXCLUIR_LOCAL = ("docs/",)

# ruta dentro del ZIP -> [(texto exacto a quitar, reemplazo)]
LIMPIEZA = {
    "local/README.md": [
        ("Diseño: [`docs/2026-10-04-reto2-local-design.md`](docs/2026-10-04-reto2-local-design.md) ·\n"
         "Plan: [`docs/2026-10-04-reto2-plan.md`](docs/2026-10-04-reto2-plan.md) ·\n"
         "Enunciado oficial: `Modulo 2/Material-Clase/Actividad-Reto2.md`.\n",
         "Equivalente local de la solución en AWS (`../aws/`). Sirve para desarrollar, como plan B y\n"
         "como plano de control de la demo.\n"),
        ("Abrir http://localhost:8090. Versión 2 (11/10/2026), a partir de la maqueta\n"
         "`Modulo 2/Aportes/danny/m2-panel-v2-propuesta-danny.html` acordada por el equipo:\n",
         "Abrir http://localhost:8090. Versión 2 (11/10/2026):\n"),
        ("opción B de Camilo (CloudWatch Logs + SQS, solo lectura)",
         "solución en AWS (CloudWatch Logs + SQS, solo lectura)"),
        ("de AWS queda deshabilitado y el panel funciona igual que antes. Diseño, política IAM y límites:\n"
         "[`docs/2026-10-12-panel-switch-aws.md`](docs/2026-10-12-panel-switch-aws.md).\n",
         "de AWS queda deshabilitado y el panel funciona igual que antes. Política IAM de solo lectura:\n"
         "[`../aws/README.md`](../aws/README.md).\n"),
        ("(original intacto en\n`Modulo 2/Material-Clase/k6-script-profesor.js`)", "(original sin cambios\nen la lógica)"),
        ("**Nunca subas `.env`**: el repo es público.", "**Nunca subas `.env`**: contiene credenciales."),
    ],
    "local/.gitignore": [
        ("# Secretos: el repo es PÚBLICO. Nunca versionar .env", "# Secretos: nunca versionar .env"),
    ],
    "local/.env.aws.example": [
        ("(política en docs/2026-10-12-panel-switch-aws.md)", "(política en ../aws/README.md)"),
    ],
    "local/panel/aws.py": [
        ("(ver docs/2026-10-12-panel-switch-aws.md)", "(política en ../aws/README.md)"),
    ],
    "local/k6/profesor.js": [
        ("// Original sin tocar: Modulo 2/Material-Clase/k6-script-profesor.js (recibido el 06/10/2026).",
         "// Original: script oficial entregado por el profesor el 06/10/2026."),
    ],
    "local/panel/static/app.js": [
        ("// los del aporte de Camilo (arquitectura-aws-opcion-b.md, 11/10): configurados en la consola.",
         "// los configurados en la consola (ver ../aws/README.md)."),
        ("// reportado por Freddy (06/10); la rúbrica escrita dice 15 s",
         "// criterio dado en el encuentro del 06/10; la rúbrica escrita dice 15 s"),
    ],
    "local/panel/static/index.html": [
        ("Criterio reportado del profesor (notas de Freddy, 06/10)",
         "Criterio del profesor (encuentro del 06/10)"),
    ],
    # aws/ingesta.py no necesita limpieza: el PR #50 dejó sus docstrings sin referencias internas.
    "aws/notifier.py": [
        # Solo cambia el comentario: afirmaba que botocore no reintenta, y no es así. La lógica es la
        # desplegada en AWS; el aporte de Camilo no se edita (ver aws/README.md, Brechas conocidas).
        ("# max_attempts=1: el presupuesto de reintentos lo controla este código, no botocore.\n",
         "# Brecha conocida: max_attempts=1 cuenta reintentos sin el intento inicial, así que botocore\n"
         "# puede hacer 2 llamadas por intento si SES no responde (ver aws/README.md, Brechas conocidas).\n"),
    ],
}

# Si alguno aparece en el ZIP final, algo se escapó de la limpieza.
PROHIBIDO = ("Aportes/", "Material-Clase", "docs/2026-", "superpowers", "repo es P", "notas de Freddy",
             "paso 3 pendiente")


def archivos_versionados(carpeta: Path) -> list[str]:
    salida = subprocess.run(["git", "ls-files", "-z"], cwd=carpeta, check=True, capture_output=True)
    return [r for r in salida.stdout.decode().split("\0") if r]


def contenido(origen: Path, ruta_zip: str) -> bytes:
    datos = origen.read_bytes()
    reemplazos = LIMPIEZA.get(ruta_zip)
    if not reemplazos:
        return datos
    texto = datos.decode("utf-8")
    for viejo, nuevo in reemplazos:
        if texto.count(viejo) != 1:
            sys.exit(f"ERROR: en {ruta_zip} no se encontró exactamente una vez:\n  {viejo[:90]!r}\n"
                     "El código cambió: actualiza LIMPIEZA antes de empaquetar.")
        texto = texto.replace(viejo, nuevo)
    return texto.encode("utf-8")


def plan() -> list[tuple[Path, str]]:
    entradas = [(EMPAQUE / r, r) for r in ("README.md", "aws/README.md")]
    entradas += [(LAMBDAS / f, f"aws/{f}") for f in ("ingesta.py", "notifier.py")]
    entradas += [(LOCAL / r, f"local/{r}") for r in archivos_versionados(LOCAL)
                 if not r.startswith(EXCLUIR_LOCAL)]
    return entradas


def main() -> None:
    entradas = plan()
    usados = {ruta for _, ruta in entradas}
    sin_usar = set(LIMPIEZA) - usados
    if sin_usar:
        sys.exit(f"ERROR: LIMPIEZA apunta a archivos que no entran al ZIP: {sorted(sin_usar)}")

    # Todo se valida en memoria antes de abrir el ZIP: si algo falla, el ZIP anterior queda intacto.
    archivos = [(ruta, contenido(origen, ruta)) for origen, ruta in sorted(entradas, key=lambda e: e[1])]
    escapes = [f"{ruta}: {p}" for ruta, datos in archivos for p in PROHIBIDO if p.encode() in datos]
    if escapes:
        sys.exit("ERROR: notas internas en el paquete (ZIP sin cambios):\n  " + "\n  ".join(escapes))

    with zipfile.ZipFile(DESTINO, "w", zipfile.ZIP_DEFLATED) as zf:
        for ruta, datos in archivos:
            zf.writestr(f"{RAIZ_ZIP}/{ruta}", datos)
    print(f"OK: {DESTINO.name} · {len(entradas)} archivos · {DESTINO.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
