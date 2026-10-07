from datetime import datetime, timezone

from alerta.adapters import smtp_notifier
from alerta.adapters.smtp_notifier import SUBJECT, SmtpNotifier, build_message
from alerta.domain import EmergencyAlert
from alerta.logjson import COLOMBIA

ALERT = EmergencyAlert("ev-1", "VFH-600", "OK", "2026-10-12T23:04:11.482-05:00")
SENT_AT = datetime(2026, 10, 12, 23, 4, 12, 732_000, tzinfo=COLOMBIA)


def test_mensaje_sigue_el_formato_del_enunciado():
    msg = build_message(ALERT, "alertas@x.co", "danny@x.co", sent_at=SENT_AT)
    assert msg["Subject"] == SUBJECT == "🚨 Alerta de Emergencia 🚨"
    assert (msg["From"], msg["To"]) == ("alertas@x.co", "danny@x.co")
    texto = msg.get_body(("plain",)).get_content()
    for esperado in ("Alerta de Emergencia", "Placa: VFH-600", "Estado: OK", "Evento: Emergency",
                     "ev-1"):
        assert esperado in texto


def test_mensaje_muestra_hora_de_recepcion_hora_de_envio_y_la_diferencia():
    msg = build_message(ALERT, "a@x.co", "b@x.co", sent_at=SENT_AT)
    for parte in ("plain", "html"):
        contenido = msg.get_body((parte,)).get_content()
        assert "2026-10-12 23:04:11.482 (UTC-05:00)" in contenido
        assert "2026-10-12 23:04:12.732 (UTC-05:00)" in contenido
        assert "1250 ms" in contenido


def test_hora_de_envio_en_otra_zona_se_muestra_en_hora_colombia():
    sent_utc = datetime(2026, 10, 13, 4, 4, 12, 732_000, tzinfo=timezone.utc)
    texto = build_message(ALERT, "a@x.co", "b@x.co", sent_at=sent_utc).get_body(("plain",)).get_content()
    assert "2026-10-12 23:04:12.732 (UTC-05:00)" in texto
    assert "1250 ms" in texto


def test_html_escapa_la_placa():
    alert = EmergencyAlert("ev-2", "<b>X</b>", "", "2026-10-12T23:04:11.482-05:00")
    msg = build_message(alert, "a@x.co", "b@x.co", sent_at=SENT_AT)
    assert "&lt;b&gt;X&lt;/b&gt;" in msg.get_body(("html",)).get_content()
    assert "Estado: —" in msg.get_body(("plain",)).get_content()


async def test_send_usa_la_configuracion_smtp(monkeypatch):
    llamadas = []

    async def fake_send(message, **kwargs):
        llamadas.append((message, kwargs))

    monkeypatch.setattr(smtp_notifier.aiosmtplib, "send", fake_send)
    monkeypatch.setattr(smtp_notifier, "now_local", lambda: SENT_AT)
    notifier = SmtpNotifier(host="smtp.gmail.com", port=587, username="u", password="p",
                            starttls=True, mail_from="a@x.co", mail_to="b@x.co")
    await notifier.send(ALERT)

    [(message, kwargs)] = llamadas
    assert message["To"] == "b@x.co"
    assert "2026-10-12 23:04:12.732 (UTC-05:00)" in message.get_body(("plain",)).get_content()
    assert kwargs == {"hostname": "smtp.gmail.com", "port": 587, "username": "u",
                      "password": "p", "start_tls": True, "timeout": 4.0}
