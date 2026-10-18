"""Los tres servicios, uno por nivel. Cada nivel se despliega como una Lambda distinta.

Mensajes de N1 y N2: capturas oficiales de «Resultados esperados».
Mensajes de N3: texto del enunciado.
El fallo lo pide el cliente con "error": true (así funciona el k6 oficial).
"""
import json
from typing import Callable

from observabilidad import Observabilidad
from reglas import N1, N2, N3

MENSAJES = {
    N1: {False: (200, "Nivel 1: OK"), True: (500, "Nivel 1: Operación Full con Error")},
    N2: {False: (200, "Nivel 2: OK"), True: (500, "Nivel 2: Operación Limitada")},
    N3: {False: (200, "Nivel 3: Operación al mínimo"),
         True: (503, "Nivel 3: Sistema bajo mantenimiento, intente más tarde")},
}

TODAS = ("validar", "registrar", "analisis_riesgo", "notificar")
CAPACIDADES = {N1: TODAS, N2: ("validar", "registrar"), N3: ()}


def respuesta(status: int, mensaje: str) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps({"message": mensaje}, ensure_ascii=False),
    }


def atender(nivel: int, cuerpo: dict, escribir: Callable[[str], None] = print) -> dict:
    falla = cuerpo.get("error") is True
    status, mensaje = MENSAJES[nivel][falla]
    capacidades = [] if falla else list(CAPACIDADES[nivel])
    Observabilidad(f"nivel{nivel}", escribir=escribir).emitir(
        "ATENCION", nivel=nivel, status=status, capacidades=capacidades,
        diferidas=[c for c in TODAS if c not in CAPACIDADES[nivel]],
    )
    return respuesta(status, mensaje)


# El router invoca cada Lambda con el cuerpo de la petición como evento.
def handler_nivel1(event, context):
    return atender(N1, event or {})


def handler_nivel2(event, context):
    return atender(N2, event or {})


def handler_nivel3(event, context):
    return atender(N3, event or {})
