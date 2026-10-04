from alerta.adapters import smtp_notifier
from alerta.adapters.smtp_notifier import SUBJECT, SmtpNotifier, build_message
from alerta.domain import EmergencyAlert

ALERT = EmergencyAlert("ev-1", "VFH-600", "OK", "2026-10-12T23:04:11.482-05:00")


def test_mensaje_sigue_el_formato_del_enunciado():
    msg = build_message(ALERT, "alertas@x.co", "danny@x.co")
    assert msg["Subject"] == SUBJECT == "🚨 Alerta de Emergencia 🚨"
    assert (msg["From"], msg["To"]) == ("alertas@x.co", "danny@x.co")
    texto = msg.get_body(("plain",)).get_content()
    for esperado in ("Alerta de Emergencia", "Placa: VFH-600", "Estado: OK", "Evento: Emergency",
                     "ev-1", "2026-10-12T23:04:11.482-05:00"):
        assert esperado in texto


def test_html_escapa_la_placa():
    alert = EmergencyAlert("ev-2", "<b>X</b>", "", "2026-10-12T23:04:11.482-05:00")
    html = build_message(alert, "a@x.co", "b@x.co").get_body(("html",)).get_content()
    assert "&lt;b&gt;X&lt;/b&gt;" in html
    assert "Estado: —" in build_message(alert, "a@x.co", "b@x.co").get_body(("plain",)).get_content()


async def test_send_usa_la_configuracion_smtp(monkeypatch):
    llamadas = []

    async def fake_send(message, **kwargs):
        llamadas.append((message, kwargs))

    monkeypatch.setattr(smtp_notifier.aiosmtplib, "send", fake_send)
    notifier = SmtpNotifier(host="smtp.gmail.com", port=587, username="u", password="p",
                            starttls=True, mail_from="a@x.co", mail_to="b@x.co")
    await notifier.send(ALERT)

    [(message, kwargs)] = llamadas
    assert message["To"] == "b@x.co"
    assert kwargs == {"hostname": "smtp.gmail.com", "port": 587, "username": "u",
                      "password": "p", "start_tls": True, "timeout": 10.0}
