import json

from conftest import T0, RelojFalso, RepositorioMemoria
import niveles
from reglas import N1, N2, N3
from router import Router


def evento(error=False):
    return {"body": json.dumps({"message": "x", "timestamp": "t", "error": error})}


def armar(repo=None, invocar=None):
    repo = repo or RepositorioMemoria()
    reloj = RelojFalso()
    lineas = []
    invocar = invocar or (lambda nivel, cuerpo: niveles.atender(nivel, cuerpo, escribir=lambda _: None))
    r = Router(repo, invocar, reloj=reloj, escribir=lineas.append)
    return r, repo, reloj, lineas


def mensaje(resp):
    return json.loads(resp["body"])["message"]


def eventos(lineas, tipo):
    return [d for d in map(json.loads, lineas) if d["evento"] == tipo]


def test_arranca_en_n1():
    r, *_ = armar()
    assert mensaje(r.atender(evento(), "id")) == "Nivel 1: OK"


def test_el_minuto_en_curso_no_cambia_de_nivel():
    r, repo, reloj, _ = armar()
    for _ in range(12):
        resp = r.atender(evento(error=True), "id")
    assert mensaje(resp) == "Nivel 1: Operación Full con Error"
    assert repo.minutos[T0 // 60]["errores"] == 12


def test_errores_del_minuto_anterior_degradan_y_se_registra_el_cambio():
    r, repo, reloj, lineas = armar()
    for _ in range(10):
        r.atender(evento(error=True), "id")
    reloj.t += 60
    assert mensaje(r.atender(evento(), "id")) == "Nivel 3: Operación al mínimo"
    cambio = eventos(lineas, "CAMBIO_NIVEL")
    assert len(cambio) == 1
    assert cambio[0]["de"] == N1 and cambio[0]["a"] == N3
    assert cambio[0]["motivo"] == "degradacion" and cambio[0]["errores_minuto_anterior"] == 10


def test_recuperacion_escalonada():
    r, repo, reloj, lineas = armar()
    for _ in range(10):
        r.atender(evento(error=True), "id")
    niveles_vistos = []
    for _ in range(3):
        reloj.t += 60
        niveles_vistos.append(mensaje(r.atender(evento(), "id")))
    assert niveles_vistos == ["Nivel 3: Operación al mínimo", "Nivel 2: OK", "Nivel 1: OK"]
    assert [c["motivo"] for c in eventos(lineas, "CAMBIO_NIVEL")] == ["degradacion", "recuperacion", "recuperacion"]


def test_falla_de_estado_responde_n3_mantenimiento():
    repo = RepositorioMemoria()
    repo.fallar = True
    r, _, _, lineas = armar(repo=repo)
    resp = r.atender(evento(), "id")
    assert resp["statusCode"] == 503
    assert mensaje(resp) == "Nivel 3: Sistema bajo mantenimiento, intente más tarde"
    assert eventos(lineas, "ESTADO_NO_DISPONIBLE")


def test_falla_del_servicio_de_nivel_cuenta_como_error():
    def invocar_roto(nivel, cuerpo):
        raise TimeoutError("lambda lenta")
    r, repo, _, lineas = armar(invocar=invocar_roto)
    resp = r.atender(evento(), "id")
    assert resp["statusCode"] == 503
    assert repo.minutos[T0 // 60]["errores"] == 1
    assert eventos(lineas, "FALLA_NIVEL")


def test_cuerpo_invalido_es_400_y_no_cuenta():
    r, repo, _, _ = armar()
    resp = r.atender({"body": "{no-json"}, "id")
    assert resp["statusCode"] == 400
    assert repo.minutos.get(T0 // 60, {}).get("peticiones", 0) == 0


def test_carrera_dos_routers_mismo_minuto_usan_el_mismo_nivel():
    repo = RepositorioMemoria()
    a, _, reloj_a, _ = armar(repo=repo)
    b, _, reloj_b, _ = armar(repo=repo)
    for _ in range(5):
        a.atender(evento(error=True), "id")
    reloj_a.t += 60
    reloj_b.t += 60
    assert mensaje(b.atender(evento(), "id")) == mensaje(a.atender(evento(), "id")) == "Nivel 2: OK"


def test_cada_peticion_emite_metricas():
    r, _, _, lineas = armar()
    r.atender(evento(error=True), "id")
    p = eventos(lineas, "PETICION")[0]
    assert p["NivelActual"] == N1 and p["Errores"] == 1 and p["Peticiones"] == 1
    assert "_aws" in p
