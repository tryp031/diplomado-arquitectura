"""Empaqueta src/ en .build/reto3-src.zip para subirlo a mano a las cuatro Lambdas (consola de AWS).

    python3 scripts/empaquetar.py          # crea el .zip e imprime su CodeSha256
    python3 scripts/empaquetar.py --sha    # solo imprime el CodeSha256 (lo usa verificar-aws.sh)

El .zip es determinista: fechas fijas, sin compresión y archivos en orden. El mismo src/ da los mismos
bytes en cualquier máquina (Mac o Windows), así que su CodeSha256 —base64 del SHA-256 del .zip, que es
lo que AWS muestra en cada Lambda— prueba que lo desplegado es exactamente este código.
"""
import base64
import hashlib
import io
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FECHA_FIJA = (1980, 1, 1, 0, 0, 0)


def empaquetar() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as z:
        for archivo in sorted((RAIZ / "src").glob("*.py")):
            info = zipfile.ZipInfo(archivo.name, date_time=FECHA_FIJA)
            info.external_attr = 0o644 << 16
            # Saltos de línea normalizados: un checkout de Windows con CRLF daría otro SHA.
            z.writestr(info, archivo.read_bytes().replace(b"\r\n", b"\n"))
    return buf.getvalue()


def code_sha256(datos: bytes) -> str:
    return base64.b64encode(hashlib.sha256(datos).digest()).decode()


if __name__ == "__main__":
    datos = empaquetar()
    if "--sha" in sys.argv:
        print(code_sha256(datos))
        sys.exit(0)
    destino = RAIZ / ".build" / "reto3-src.zip"
    destino.parent.mkdir(exist_ok=True)
    destino.write_bytes(datos)
    print(f"{destino.relative_to(RAIZ)}  ({len(datos)} bytes)")
    print(f"CodeSha256: {code_sha256(datos)}")
