"""Arranque del notifier: `python -m alerta.main_notifier`."""
from __future__ import annotations

import asyncio
import signal

from alerta.adapters.redis_queue import RedisAlertQueue, conectar
from alerta.adapters.smtp_notifier import SmtpNotifier
from alerta.config import load_settings
from alerta.logjson import JsonLogger
from alerta.notifier_worker import NotifierWorker


async def main() -> None:
    settings = load_settings()
    log = JsonLogger("notifier", settings.log_dir)
    client = conectar(settings.redis_url)
    queue = RedisAlertQueue(client, stream=settings.stream, group=settings.group,
                            consumer=settings.consumer, dlq_stream=settings.dlq_stream)
    await queue.ensure_group()  # si Redis no está listo, el proceso falla y compose lo reinicia
    notifier = SmtpNotifier(
        host=settings.smtp_host, port=settings.smtp_port, username=settings.smtp_user,
        password=settings.smtp_password, starttls=settings.smtp_starttls,
        mail_from=settings.mail_from, mail_to=settings.mail_to, timeout_s=settings.smtp_timeout_s,
    )
    worker = NotifierWorker(queue, notifier, log, concurrency=settings.notifier_concurrency,
                            max_attempts=settings.max_attempts)

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)

    log.log("NOTIFIER_STARTED", consumer=settings.consumer,
            concurrency=settings.notifier_concurrency, smtp_host=settings.smtp_host)
    try:
        await worker.run(stop)
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
