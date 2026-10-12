#!/usr/bin/env bash
# Empieza de cero sin perder evidencia: ARCHIVA los logs (no los borra), vacía las colas de Redis
# y vuelve a encender los servicios con la misma configuración (Gmail o Mailpit, la que tengan).
#
#   scripts/reiniciar.sh            # pide confirmación
#   scripts/reiniciar.sh -y         # sin preguntar
#   scripts/reiniciar.sh --simular  # muestra qué haría, sin tocar nada
#
# Por qué detener antes de mover: cada servicio tiene su archivo de log abierto. Si se mueve con el
# servicio encendido, sigue escribiendo en el archivo ya archivado.
set -euo pipefail

cd "$(dirname "$0")/.."
PROYECTO="${COMPOSE_PROJECT:-reto2-alerta-flota}"
STREAM="${STREAM:-emergencies}"
DLQ_STREAM="${DLQ_STREAM:-emergencies-dlq}"
SERVICIOS=(panel gateway ingest notifier)   # orden de apagado; se encienden al revés
DESTINO="logs-archivo/$(date +%Y%m%d-%H%M%S)"

SIMULAR=0
CONFIRMADO=0
for arg in "$@"; do
  case "$arg" in
    -y) CONFIRMADO=1 ;;
    --simular) SIMULAR=1 ;;
    *) echo "Uso: $0 [-y] [--simular]" >&2; exit 2 ;;
  esac
done

contenedores() {  # ids de los contenedores de un servicio del proyecto (puede haber réplicas)
  docker ps -a -q --filter "label=com.docker.compose.project=$PROYECTO" \
    --filter "label=com.docker.compose.service=$1"
}

ejecutar() {
  if [[ $SIMULAR -eq 1 ]]; then echo "  [simulado] $*" >&2; else "$@"; fi
}

REDIS=$(contenedores redis)
if [[ -z "$REDIS" ]]; then
  echo "No encuentro el contenedor de Redis del proyecto '$PROYECTO'. ¿Está levantado el sistema?" >&2
  exit 1
fi

echo "Esto va a:"
echo "  1. Detener: ${SERVICIOS[*]} (una carga k6 en curso se corta)."
echo "  2. Vaciar los streams de Redis '$STREAM' y '$DLQ_STREAM'."
echo "  3. Mover logs/ a $DESTINO/ (incluye el historial de corridas del panel)."
echo "  4. Encender de nuevo los servicios."
if [[ $SIMULAR -eq 0 && $CONFIRMADO -eq 0 ]]; then
  read -r -p "¿Continuar? [s/N] " respuesta
  [[ "$respuesta" =~ ^[sS]$ ]] || { echo "Cancelado."; exit 0; }
fi

echo "→ Deteniendo servicios"
for servicio in "${SERVICIOS[@]}"; do
  ids=$(contenedores "$servicio")
  if [[ -n "$ids" ]]; then ejecutar docker stop -t 10 $ids >/dev/null; fi
done

echo "→ Vaciando colas (el notifier recrea su grupo al arrancar)"
ejecutar docker exec "$REDIS" redis-cli DEL "$STREAM" "$DLQ_STREAM" >/dev/null

echo "→ Archivando logs en $DESTINO/"
if [[ -d logs ]] && [[ -n "$(ls -A logs 2>/dev/null)" ]]; then
  ejecutar mkdir -p "$DESTINO"
  ejecutar mv logs/* "$DESTINO/"
fi
ejecutar mkdir -p logs/nginx

echo "→ Encendiendo servicios"
for (( i=${#SERVICIOS[@]}-1; i>=0; i-- )); do
  ids=$(contenedores "${SERVICIOS[$i]}")
  if [[ -n "$ids" ]]; then ejecutar docker start $ids >/dev/null; fi
done

echo "Listo. Historial vacío; lo anterior quedó en $DESTINO/."
