import pytest

from alerta.config import load_settings


def test_valores_por_defecto_apuntan_a_mailpit():
    settings = load_settings({})
    assert settings.smtp_host == "mailpit"
    assert settings.smtp_port == 1025
    assert settings.smtp_starttls is False
    assert settings.notifier_concurrency == 5
    assert settings.max_attempts == 4
    assert settings.log_dir is None


def test_variables_de_entorno_sobrescriben():
    settings = load_settings({
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_STARTTLS": "true",
        "NOTIFIER_CONCURRENCY": "3",
        "LOG_DIR": "/logs",
        "CONSUMER_NAME": "notifier-1",
    })
    assert (settings.smtp_host, settings.smtp_port, settings.smtp_starttls) == ("smtp.gmail.com", 587, True)
    assert settings.notifier_concurrency == 3
    assert settings.log_dir == "/logs"
    assert settings.consumer == "notifier-1"


@pytest.mark.parametrize("valor", ["0", "-1"])
def test_concurrencia_menor_a_uno_es_error(valor):
    with pytest.raises(ValueError):
        load_settings({"NOTIFIER_CONCURRENCY": valor})


@pytest.mark.parametrize("valor", ["0", "-2"])
def test_max_attempts_menor_a_uno_es_error(valor):
    # Con 0 intentos el worker no enviaría ni confirmaría nada, sin decirlo.
    with pytest.raises(ValueError):
        load_settings({"MAX_ATTEMPTS": valor})
