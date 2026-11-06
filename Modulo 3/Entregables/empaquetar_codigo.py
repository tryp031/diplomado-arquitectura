"""Arma el ZIP del código fuente del Reto 3 (entregable 1 del enunciado).

Uso, desde cualquier carpeta del repo:  python3 "Modulo 3/Entregables/empaquetar_codigo.py"

- Parte de `git ls-files`: solo entra lo versionado. Así quedan fuera `.env.aws`, `.venv/`, `.build/`
  y cachés sin tener que listarlos. `logs/` se excluye: la evidencia se entrega aparte.
- El README del proyecto es la bitácora interna del equipo: se reemplaza por `empaque/README.md`.
- `docs/` solo aporta el ADR vigente (ADR-002). ADR-001 (v1, histórica) queda fuera.
- El k6 oficial del profesor entra sin cambios en `k6/`, y las rutas que lo buscaban en el material
  de clase se ajustan a esa carpeta. La corrida real que usa `test_panel.py` entra en `tests/datos/`.
- **`src/` no se toca:** debe ser byte a byte el desplegado en AWS (mismo `CodeSha256`). Por eso sus
  docstrings conservan las citas a las aclaraciones del docente. El script lo verifica.
- Limpia notas internas con reemplazos EXACTOS. Si un texto ya no aparece (alguien cambió el código),
  el script falla en vez de empaquetar la nota en silencio: hay que actualizar LIMPIEZA.
"""
import base64
import hashlib
import importlib.util
import subprocess
import sys
import zipfile
from pathlib import Path

ENTREGABLES = Path(__file__).resolve().parent
MODULO = ENTREGABLES.parent
PROYECTO = MODULO / "Ejercicios" / "Reto3-Resiliencia"
K6_OFICIAL = MODULO / "Material-Clase" / "k6-script-profesor-reto3.js"
CORRIDA_TEST = MODULO / "Aportes" / "camilo" / "evidencia-corrida-oficial-v3-20261102"
EMPAQUE = ENTREGABLES / "empaque"
RAIZ_ZIP = "reto3-codigo-grupo2"
DESTINO = ENTREGABLES / "Entregable-1-Codigo-Fuente-Group2.zip"
SHA_DESPLEGADO = "Gq+DEPQOikPl9sW2XowRlIdEN8XHeXB+ek+uRyXHlqA="

EXCLUIR = ("logs/", "docs/", "README.md")
INCLUIR_DOCS = ("docs/ADR/ADR-002-histeresis-v3.md",)

# ruta dentro del ZIP -> [(texto exacto a quitar, reemplazo)]
LIMPIEZA = {
    ".env.aws.example": [
        ("# Es el mismo esquema del Reto 2, con su propio archivo: no se mezcla con ~/.aws ni con el Reto 2.\n",
         "# Es un archivo propio: no se mezcla con ~/.aws.\n"),
        ("# --- Usuario IAM de SOLO LECTURA del Reto 3 (reto3-panel-lectura, cuenta del equipo) ---",
         "# --- Usuario IAM de SOLO LECTURA (CloudWatch Logs, DynamoDB GetItem, Lambda GetFunction) ---"),
    ],
    "docs/ADR/ADR-002-histeresis-v3.md": [
        ("El equipo (Freddy, Camilo y Danny) eligió", "El equipo eligió"),
        ("**Reemplaza a ADR-001** (permanencia de 2 min)",
         "**Reemplaza a ADR-001** (v1: minuto de reloj y permanencia de 2 min)"),
        ("· **Autor:** Danny (con IA)", "· **Autor:** Group 2"),
        ("latencia (riesgo R1).", "latencia."),
        ("el 27/10 (k6 manual,\n  `logs/k6-local-v3-20261028T011300Z.log`) y el 30/10",
         "el 27/10 (k6 manual) y el 30/10"),
    ],
    "panel/app.py": [
        ('OFICIAL = RAIZ.parents[1] / "Material-Clase" / "k6-script-profesor-reto3.js"',
         'OFICIAL = RAIZ / "k6" / "k6-script-profesor-reto3.js"'),
    ],
    "panel/entornos.py": [
        ("Guarda de cuenta: en la máquina de Danny el perfil `default` de ~/.aws es corporativo. El\n"
         "entorno AWS nunca usa",
         "Guarda de cuenta: el perfil `default` de ~/.aws puede ser de otra cuenta, así que el\n"
         "entorno AWS nunca usa"),
        ("(gitignored, igual que en el Reto 2)", "(fuera del control de versiones)"),
        ('"el perfil «default» de esta máquina es corporativo: use un perfil del equipo"',
         '"el perfil «default» no se usa: use un perfil de solo lectura con nombre"'),
    ],
    "panel/k6.py": [
        ("# Docente (Discord, 18/09/2026):", "# Docente (aclaración del 18/09/2026):"),
    ],
    "scripts/correr-k6.sh": [
        ('OFICIAL="../../Material-Clase/k6-script-profesor-reto3.js"', 'OFICIAL="k6/k6-script-profesor-reto3.js"'),
    ],
    "scripts/deploy.sh": [
        ("AWS_PROFILE=diplomado CUENTA_ESPERADA=<id de 12 dígitos de Camilo> scripts/deploy.sh aws",
         "AWS_PROFILE=<perfil> CUENTA_ESPERADA=<id de 12 dígitos> scripts/deploy.sh aws"),
        ("# Guarda: en esta máquina el perfil `default` es corporativo. Para AWS se exige el\n"
         "# perfil `diplomado` Y que la cuenta coincida con CUENTA_ESPERADA; si no, aborta.",
         "# Guarda: para AWS se exige un perfil con nombre (nunca `default`) Y que la cuenta\n"
         "# coincida con CUENTA_ESPERADA; si no, aborta."),
        ('[[ "${AWS_PROFILE:-}" == diplomado ]] || { echo "ABORTO: usa AWS_PROFILE=diplomado" >&2; exit 1; }',
         '[[ -n "${AWS_PROFILE:-}" && "$AWS_PROFILE" != default ]] || '
         '{ echo "ABORTO: usa AWS_PROFILE=<perfil> (nunca default)" >&2; exit 1; }'),
    ],
    "scripts/verificar-aws.sh": [
        (" (como el Reto 2)", ""),
    ],
    "scripts/panel.sh": [
        (" (como el Reto 2)", ""),
        ("# Nunca usa el perfil `default`: en esta máquina es corporativo.",
         "# Nunca usa el perfil `default`, para no tocar por accidente otra cuenta."),
    ],
    "tests/test_empaquetar.py": [
        ("(el caso de Camilo, 02/11)", "(empaquetado desde Windows)"),
    ],
    "tests/test_k6_oficial.py": [
        ("Documenta el riesgo R1 de la spec:", "Documenta el riesgo de latencia de la v1:"),
    ],
    "tests/test_panel.py": [
        ('OFICIAL = Path(__file__).resolve().parents[3] / "Material-Clase" / "k6-script-profesor-reto3.js"',
         'OFICIAL = Path(__file__).resolve().parents[1] / "k6" / "k6-script-profesor-reto3.js"'),
        ('EVIDENCIA_CAMILO = (Path(__file__).resolve().parents[3] / "Aportes" / "camilo" / '
         '"evidencia-corrida-oficial-v3-20261102")',
         'EVIDENCIA_AWS = Path(__file__).resolve().parent / "datos" / "corrida-aws-20261102"'),
        ("def test_coherencia_con_la_corrida_oficial_de_camilo():",
         "def test_coherencia_con_una_corrida_real_en_aws():"),
        ('next(EVIDENCIA_CAMILO.glob("*-k6.log"))', 'next(EVIDENCIA_AWS.glob("*-k6.log"))'),
        ('next(EVIDENCIA_CAMILO.glob("*-servidor.jsonl"))', 'next(EVIDENCIA_AWS.glob("*-servidor.jsonl"))'),
    ],
    "tests/test_reglas.py": [
        ("# Discord-Aclaraciones-Docente.md §5:", "# Diagrama de la sesión del docente:"),
        ("(ADR de permanencia)", "(ADR-001, v1)"),
        ("(Discord, 18/09/2026)", "(aclaración del 18/09/2026)"),
    ],
}

GITIGNORE = b".venv/\n__pycache__/\n.pytest_cache/\n.build/\nlogs/\n.env.aws\n"

# Si alguno aparece en el ZIP final, algo se escapó de la limpieza. `src/` queda exento de los que
# están en EXENTO_SRC: no se edita para conservar el CodeSha256 desplegado.
PROHIBIDO = ("Aportes", "Material-Clase", "superpowers", "Camilo", "Freddy", "Danny", "corporativo",
             "AWS_PROFILE=diplomado", "perfil `diplomado`", "Reto 2", "reto3-panel-lectura", "con IA",
             "Claude", "Discord", "spec §", "/Users/", "chcrdwyl0d", "w2raf46cp3", "EVIDENCIA_CAMILO")
EXENTO_SRC = ("Discord", "spec §")
EXENTO_README = ("Camilo", "Freddy")  # la línea de integrantes


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
    entradas = [(EMPAQUE / "README.md", "README.md"),
                (K6_OFICIAL, "k6/k6-script-profesor-reto3.js")]
    entradas += [(PROYECTO / r, r) for r in archivos_versionados(PROYECTO)
                 if not r.startswith(EXCLUIR) or r in INCLUIR_DOCS]
    entradas += [(f, f"tests/datos/corrida-aws-20261102/{f.name}")
                 for f in sorted(CORRIDA_TEST.glob("*")) if f.name.endswith(("-k6.log", "-servidor.jsonl"))]
    return entradas


def sha_de_src() -> str:
    """CodeSha256 del .zip de Lambda que arma scripts/empaquetar.py con el src/ actual."""
    spec = importlib.util.spec_from_file_location("empaquetar_lambdas", PROYECTO / "scripts" / "empaquetar.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return base64.b64encode(hashlib.sha256(modulo.empaquetar()).digest()).decode()


def main() -> None:
    sha = sha_de_src()
    if sha != SHA_DESPLEGADO:
        sys.exit(f"ERROR: src/ no es el desplegado en AWS ({sha} != {SHA_DESPLEGADO}).")

    entradas = plan()
    usados = {ruta for _, ruta in entradas}
    sin_usar = set(LIMPIEZA) - usados
    if sin_usar:
        sys.exit(f"ERROR: LIMPIEZA apunta a archivos que no entran al ZIP: {sorted(sin_usar)}")
    if len([r for r in usados if r.startswith("tests/datos/")]) != 2:
        sys.exit(f"ERROR: falta la corrida de prueba en {CORRIDA_TEST}")

    # Todo se valida en memoria antes de abrir el ZIP: si algo falla, el ZIP anterior queda intacto.
    archivos = [(ruta, contenido(origen, ruta)) for origen, ruta in sorted(entradas, key=lambda e: e[1])]
    archivos.append((".gitignore", GITIGNORE))
    escapes = [f"{ruta}: {p}" for ruta, datos in archivos for p in PROHIBIDO
               if p.encode() in datos and not (ruta.startswith("src/") and p in EXENTO_SRC)
               and not (ruta == "README.md" and p in EXENTO_README)]
    if escapes:
        sys.exit("ERROR: notas internas en el paquete (ZIP sin cambios):\n  " + "\n  ".join(escapes))

    with zipfile.ZipFile(DESTINO, "w", zipfile.ZIP_DEFLATED) as zf:
        for ruta, datos in archivos:
            info = zipfile.ZipInfo(f"{RAIZ_ZIP}/{ruta}", date_time=(2026, 11, 5, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3  # Unix: si no, unzip ignora los permisos
            info.external_attr = (0o100755 if ruta.endswith(".sh") else 0o100644) << 16  # los .sh se ejecutan
            zf.writestr(info, datos)
    print(f"OK: {DESTINO.name} · {len(archivos)} archivos · {DESTINO.stat().st_size / 1024:.0f} KB · "
          f"src/ = desplegado ({sha})")


if __name__ == "__main__":
    main()
