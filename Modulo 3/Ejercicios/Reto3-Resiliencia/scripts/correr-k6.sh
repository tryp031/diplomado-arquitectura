#!/usr/bin/env bash
# Corre el k6 OFICIAL sin modificarlo: solo se reemplaza la URL del profesor por la nuestra.
#   scripts/correr-k6.sh localstack|aws
set -euo pipefail
cd "$(dirname "$0")/.."
ENTORNO="${1:?uso: correr-k6.sh localstack|aws}"
URL=$(cat ".build/url-$ENTORNO.txt")
OFICIAL="../../Material-Clase/k6-script-profesor-reto3.js"
URL_PROFE='https://6u2da0eye1.execute-api.us-east-2.amazonaws.com/prod/service-api'
COPIA=".build/k6-reto3-$ENTORNO.js"
sed "s#$URL_PROFE#$URL#" "$OFICIAL" > "$COPIA"
# Evidencia de que el único cambio es la URL:
diff "$OFICIAL" "$COPIA" | tee ".build/k6-diff-$ENTORNO.txt" || true
[[ $(diff "$OFICIAL" "$COPIA" | grep -c '^[<>]') -eq 2 ]] || { echo "ABORTO: el script cambió en algo más que la URL" >&2; exit 1; }
mkdir -p logs
LOG="logs/k6-$ENTORNO-$(date -u +%Y%m%dT%H%M%SZ).log"
echo "log: $LOG"
k6 run "$COPIA" 2>&1 | tee "$LOG"
