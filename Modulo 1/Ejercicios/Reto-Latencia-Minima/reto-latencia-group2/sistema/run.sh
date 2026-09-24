#!/usr/bin/env bash
# Orquestador de una corrida: levanta el servidor, mide, lo baja y analiza.
#
# Uso:
#   ./run.sh tcp-python 1               # TCP Python, ronda 1, valores por defecto
#   ./run.sh tcp-python 1 --iters 200000   # parámetros extra van al cliente
#
# El cliente reintenta la conexión, así que no hace falta esperar al servidor.
set -euo pipefail

VARIANTE="${1:?uso: ./run.sh <VARIANTE> <RONDA> [args extra del cliente]}"
RONDA="${2:?uso: ./run.sh <VARIANTE> <RONDA> [args extra del cliente]}"
shift 2

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# El alcance de la entrega son las variantes TCP Python y Memoria compartida C
# (ADR-007). Las variantes A y C nunca se
# implementaron; los controles Bc y E se midieron y se retiraron del arbol el 16/09.
# Sus hallazgos siguen en docs/archivo/ y su codigo en el historial de git.
case "$VARIANTE" in
  tcp-python)           DIR="$AQUI/tcp-python" ;;
  memoria-compartida-c) DIR="$AQUI/memoria-compartida-c" ;;
  *) echo "variante desconocida: $VARIANTE (use tcp-python|memoria-compartida-c)" >&2; exit 2 ;;
esac
[[ -d "$DIR" ]] || { echo "falta el directorio $DIR" >&2; exit 2; }

OUT="$AQUI/resultados/resultados-${VARIANTE}-${RONDA}.csv"
LOG="$AQUI/resultados/ejecucion-${VARIANTE}-${RONDA}.log"
mkdir -p "$AQUI/resultados" "$AQUI/resultados/archivo"

# Los resultados crudos son la EVIDENCIA del informe (atributo AC-4): toda cifra debe
# poder reproducirse desde un CSV versionado. Sobrescribirlos en silencio destruye esa
# cadena — ya ocurrio una vez, el 14/09, y se perdieron las corridas del 10/09.
# Ahora una corrida repetida ARCHIVA lo anterior con su fecha en vez de pisarlo.
#
# La fecha sale de la cabecera `fecha:` del log, no del mtime: el .log esta versionado
# y un `git clone` o `checkout` le pone la fecha del checkout. El 24/09 eso archivo
# la corrida del 17/09 con fecha del 23/09. El mtime queda solo como respaldo.
marca_log=""
if [[ -f "$LOG" ]]; then
  marca_log=$(sed -n 's/^fecha: *\([0-9]\{4\}\)-\([0-9]\{2\}\)-\([0-9]\{2\}\)T\([0-9]\{2\}\):\([0-9]\{2\}\):\([0-9]\{2\}\).*/\1\2\3-\4\5\6/p' "$LOG" | head -1)
fi
for viejo in "$OUT" "$LOG"; do
  if [[ -f "$viejo" ]]; then
    marca="$marca_log"
    [[ -n "$marca" ]] || marca=$(date -r "$viejo" +%Y%m%d-%H%M%S 2>/dev/null || date +%Y%m%d-%H%M%S)
    base=$(basename "$viejo"); ext="${base##*.}"; nom="${base%.*}"
    mv "$viejo" "$AQUI/resultados/archivo/${nom}--${marca}.${ext}"
    echo "archivado: resultados/archivo/${nom}--${marca}.${ext}"
  fi
done

echo "== variante $VARIANTE, ronda $RONDA =="
{
  echo "fecha:     $(date -Iseconds)"
  echo "host:      $(uname -a)"
  echo "cpu:       $(sysctl -n machdep.cpu.brand_string 2>/dev/null || lscpu 2>/dev/null | head -20)"
  echo "nucleos:   $(sysctl -n hw.ncpu 2>/dev/null || nproc)"
  echo "carga:     $(uptime | sed 's/.*load average[s]*: *//')"   # supuesto S4 del informe
  echo "python:    $(python3 --version)"
  echo "compilador: $(cc --version 2>/dev/null | head -1 || echo 'n/a')"
  echo "variante:  $VARIANTE   ronda: $RONDA"
  echo "args:      $*"
  echo "---"
} | tee "$LOG"

# Las variantes pueden ser interpretadas (server.py) o compiladas (server).
# Si hay Makefile se compila antes de medir: nunca se mide un binario obsoleto.
if [[ -f "$DIR/Makefile" ]]; then
  echo "compilando $VARIANTE..." | tee -a "$LOG"
  make -C "$DIR" 2>&1 | tee -a "$LOG"
fi

# Toda variante recibe la MISMA tabla de hosts: el dominio no se replica (ADR-004).
TABLA="$AQUI/tabla-hosts.csv"
[[ -f "$TABLA" ]] || { echo "falta $TABLA" >&2; exit 2; }

if [[ -x "$DIR/server" && -x "$DIR/client" ]]; then
  CMD_SRV=("$DIR/server"); CMD_CLI=("$DIR/client")
elif [[ -f "$DIR/server.py" && -f "$DIR/client.py" ]]; then
  CMD_SRV=(python3 "$DIR/server.py"); CMD_CLI=(python3 "$DIR/client.py")
else
  echo "error: $DIR no tiene ni (server|client) ni (server.py|client.py)" >&2; exit 2
fi
echo "ejecutable: ${CMD_SRV[*]}" | tee -a "$LOG"

"${CMD_SRV[@]}" --tabla "$TABLA" >>"$LOG" 2>&1 &
SRV=$!
# shellcheck disable=SC2064
trap "kill $SRV 2>/dev/null || true" EXIT

"${CMD_CLI[@]}" --tabla "$TABLA" --out "$OUT" "$@" 2>&1 | tee -a "$LOG"

{ kill "$SRV"; wait "$SRV"; } 2>/dev/null || true
trap - EXIT

echo
python3 "$AQUI/analyze.py" --histograma "$OUT" | tee -a "$LOG"
echo
echo "muestras -> $OUT"
echo "log      -> $LOG"
