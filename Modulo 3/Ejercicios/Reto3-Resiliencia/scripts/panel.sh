#!/usr/bin/env bash
# Panel de control del Reto 3 en http://localhost:8030
#   scripts/panel.sh                                   # solo LocalStack
#   PANEL_AWS_PERFIL=diplomado-lectura scripts/panel.sh   # habilita el switch AWS (perfil de solo lectura)
# Nunca usa el perfil `default`: en esta máquina es corporativo.
set -euo pipefail
cd "$(dirname "$0")/.."
[[ -x .venv/bin/uvicorn ]] || { python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt; }
unset AWS_PROFILE
exec .venv/bin/uvicorn --factory panel.app:crear_app --host 127.0.0.1 --port "${PANEL_PUERTO:-8030}"
