#!/usr/bin/env bash
# Arranca el plano de control y abre el navegador.
#
# El plano de control NO es el sistema del reto: enciende los servidores del
# plano de datos y muestra lo que miden. Ver README.md.
set -euo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PUERTO="${1:-8080}"

command -v python3 >/dev/null || { echo "Falta python3. Instalalo y volve a intentar." >&2; exit 1; }
if ! command -v cc >/dev/null; then
  echo "Aviso: no hay compilador de C. La variante Memoria compartida C no va a arrancar."
  echo "       Diagnostico completo:  python3 doctor.py"
fi

echo "Compilando las variantes en C..."
for d in "$AQUI"/sistema/*/; do
  [[ -f "$d/Makefile" ]] && make -C "$d" >/dev/null 2>&1 && echo "  $(basename "$d") ok" || true
done

( sleep 1.5
  if   command -v open    >/dev/null; then open "http://127.0.0.1:$PUERTO"
  elif command -v xdg-open >/dev/null; then xdg-open "http://127.0.0.1:$PUERTO"
  fi ) &

exec python3 "$AQUI/app/servidor.py" --puerto "$PUERTO"
