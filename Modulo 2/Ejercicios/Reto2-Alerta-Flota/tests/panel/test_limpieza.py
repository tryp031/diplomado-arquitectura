from panel.limpieza import vaciar_logs


def test_vaciar_logs_trunca_sin_borrar_los_archivos(tmp_path):
    # Cada servicio tiene su log abierto en modo append: borrarlo lo dejaría escribiendo en un
    # archivo fantasma. Truncarlo lo deja seguir escribiendo desde cero en el mismo archivo.
    (tmp_path / "nginx").mkdir()
    for nombre in ("ingest-a.log", "notifier-b.log", "nginx/gateway-access.log"):
        (tmp_path / nombre).write_text('{"event": "x"}\n', encoding="utf-8")
    (tmp_path / "k6-summary.json").write_text("{}", encoding="utf-8")
    (tmp_path / "otro.txt").write_text("no es del sistema", encoding="utf-8")

    vaciados = vaciar_logs(tmp_path)

    assert vaciados == 3
    for nombre in ("ingest-a.log", "notifier-b.log", "nginx/gateway-access.log"):
        assert (tmp_path / nombre).exists() and (tmp_path / nombre).stat().st_size == 0
    assert not (tmp_path / "k6-summary.json").exists()
    assert (tmp_path / "otro.txt").read_text(encoding="utf-8") == "no es del sistema"


def test_vaciar_logs_tolera_directorio_vacio(tmp_path):
    assert vaciar_logs(tmp_path) == 0
