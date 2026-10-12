import json
from datetime import datetime, timedelta, timezone

from panel.corridas import Historial

COL = timezone(timedelta(hours=-5))
INICIO = datetime(2026, 10, 12, 10, 42, 5, tzinfo=COL)


def test_abrir_numera_y_persiste(tmp_path):
    historial = Historial(tmp_path / "corridas.json")
    primera = historial.abrir(INICIO, "profesor", "smtp.gmail.com")
    segunda = historial.abrir(INICIO + timedelta(minutes=5), "rafaga", "mailpit")
    assert (primera["n"], segunda["n"]) == (1, 2)
    guardado = json.loads((tmp_path / "corridas.json").read_text(encoding="utf-8"))
    assert [c["n"] for c in guardado] == [1, 2]
    assert Historial(tmp_path / "corridas.json").ultima()["modo"] == "rafaga"  # sobrevive a reinicios


def test_actualizar_solo_escribe_si_cambia(tmp_path):
    path = tmp_path / "corridas.json"
    historial = Historial(path)
    historial.abrir(INICIO, "profesor", "mailpit")
    assert historial.actualizar(1, fin="x", medida={"segundos": 1.33}) is True
    assert historial.actualizar(1, fin="x", medida={"segundos": 1.33}) is False
    assert historial.buscar(1)["medida"] == {"segundos": 1.33}
    assert historial.buscar(9) is None


def test_listar_trae_la_mas_reciente_primero(tmp_path):
    historial = Historial(tmp_path / "corridas.json")
    for i in range(3):
        historial.abrir(INICIO + timedelta(minutes=i), "rafaga", "mailpit")
    assert [c["n"] for c in historial.listar()] == [3, 2, 1]
    assert [c["n"] for c in historial.listar(limite=2)] == [3, 2]


def test_archivo_corrupto_empieza_vacio_sin_romper_el_panel(tmp_path):
    path = tmp_path / "corridas.json"
    path.write_text("{no es json", encoding="utf-8")
    historial = Historial(path)
    assert historial.listar() == []
    assert historial.abrir(INICIO, "rafaga", "mailpit")["n"] == 1
