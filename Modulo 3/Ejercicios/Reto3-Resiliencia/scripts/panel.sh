#!/usr/bin/env bash
# Panel de control del Reto 3 en http://localhost:8030
#   scripts/panel.sh                                   # con .env.aws: switch AWS con lectura (como el Reto 2)
#   PANEL_AWS_PERFIL=<perfil> scripts/panel.sh           # alternativa: perfil de solo lectura de ~/.aws
# Nunca usa el perfil `default`: en esta máquina es corporativo.
set -euo pipefail
cd "$(dirname "$0")/.."
[[ -x .venv/bin/uvicorn ]] || { python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt; }
unset AWS_PROFILE
exec .venv/bin/uvicorn --factory panel.app:crear_app --host 127.0.0.1 --port "${PANEL_PUERTO:-8030}"
