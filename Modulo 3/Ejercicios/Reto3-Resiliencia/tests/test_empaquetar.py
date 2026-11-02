"""El .zip de las Lambdas da el mismo CodeSha256 en Mac y en Windows: verificar-aws.sh depende de eso."""
import importlib.util
import io
import zipfile
from pathlib import Path

_RUTA = Path(__file__).resolve().parents[1] / "scripts" / "empaquetar.py"
_spec = importlib.util.spec_from_file_location("empaquetar", _RUTA)
empaquetar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(empaquetar)


def test_mismo_sha_en_windows_y_en_unix(monkeypatch):
    unix = empaquetar.empaquetar()
    # zipfile.ZipInfo anota create_system=0 cuando sys.platform es win32 (el caso de Camilo, 02/11).
    monkeypatch.setattr(zipfile.sys, "platform", "win32")
    assert empaquetar.empaquetar() == unix


def test_es_determinista_y_trae_solo_src():
    datos = empaquetar.empaquetar()
    assert datos == empaquetar.empaquetar()
    nombres = zipfile.ZipFile(io.BytesIO(datos)).namelist()
    assert nombres == sorted(p.name for p in (_RUTA.parents[1] / "src").glob("*.py"))
