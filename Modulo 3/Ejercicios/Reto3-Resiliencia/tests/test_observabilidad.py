import json

from observabilidad import Observabilidad


def test_evento_sin_metricas_es_una_linea_json():
    lineas = []
    obs = Observabilidad("router", escribir=lineas.append, reloj=lambda: 1.5)
    obs.emitir("CAMBIO_NIVEL", de=1, a=3, motivo="degradacion")
    assert len(lineas) == 1
    d = json.loads(lineas[0])
    assert d == {"evento": "CAMBIO_NIVEL", "servicio": "router", "de": 1, "a": 3, "motivo": "degradacion"}


def test_metricas_generan_bloque_emf():
    lineas = []
    obs = Observabilidad("router", escribir=lineas.append, reloj=lambda: 2.0)
    obs.emitir("PETICION", metricas={"Errores": 1, "LatenciaRouter": 12.5}, nivel=2)
    d = json.loads(lineas[0])
    emf = d["_aws"]
    assert emf["Timestamp"] == 2000
    cw = emf["CloudWatchMetrics"][0]
    assert cw["Namespace"] == "Reto3"
    assert cw["Dimensions"] == [["servicio"]]
    assert {m["Name"] for m in cw["Metrics"]} == {"Errores", "LatenciaRouter"}
    assert d["Errores"] == 1 and d["LatenciaRouter"] == 12.5 and d["nivel"] == 2


def test_acentos_se_conservan():
    lineas = []
    Observabilidad("nivel1", escribir=lineas.append).emitir("X", mensaje="Operación")
    assert "Operación" in lineas[0]
