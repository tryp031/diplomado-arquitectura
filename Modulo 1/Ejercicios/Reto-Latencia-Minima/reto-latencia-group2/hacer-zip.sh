#!/usr/bin/env bash
# hacer-zip.sh — arma el ZIP del ENTREGABLE 1 (codigo fuente).
#
#   ./hacer-zip.sh [destino.zip]
#
# POR QUE ESTE SCRIPT Y NO MOVER docs/ FUERA DEL PROYECTO
#
# La nota 8 de la reunion del 21/09 pedia sacar docs/ del proyecto porque no es
# parte del entregable de codigo. El objetivo es correcto; hacerlo moviendo la
# carpeta no lo es: el codigo fuente CITA los ADR por numero —en comentarios de
# reloj.h, clasificador.h, server.c y verificar.py, entre otros, y analyze.py
# imprime "Ver docs/ADR/ADR-005" al negarse a mezclar plataformas—. Si docs/ se muda, el ZIP entregado
# queda lleno de punteros a documentos que el evaluador no recibio.
#
# La separacion correcta no es DONDE VIVE sino QUE SE EMPAQUETA. docs/ se queda en
# el repositorio, que es de donde sale el PDF del entregable 2, y este script decide
# que entra en el ZIP. Ver ADR-010.
#
# QUE NO ENTRA, Y POR QUE
#
#   docs/               justificacion y ADR -> son el ENTREGABLE 2 (PDF), no el 1
#   docs/graficas/      figuras del informe: producto del analisis (nota 7)
#   sistema/resultados/ ~143 MB de evidencia -> es el ENTREGABLE 3 (logs), aparte
#   binarios            server, client, micro, veredicto: se compilan con make
#   __pycache__/        artefactos de Python
#   comunicaciones/     correspondencia del equipo, citada en ADR-005
#   README.md (todos)   decision del equipo del 28/09: el ZIP lleva solo codigo
#   hacer-zip.sh        herramienta de empaquetado, no parte del sistema
#   contrato/coherencia binario compilado; viaja coherencia.c
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESTINO="${1:-$AQUI/reto-latencia-group2-codigo.zip}"

command -v zip >/dev/null || { echo "falta el comando 'zip'" >&2; exit 2; }

STAGING="$(mktemp -d)"
trap 'rm -rf "$STAGING"' EXIT
RAIZ="$STAGING/reto-latencia-group2"
mkdir -p "$RAIZ"

# Se copia por lista blanca: lo que no este nombrado aqui, no viaja. Es mas seguro
# que una lista negra, donde un archivo nuevo se cuela solo.
for item in app contrato sistema verificar.py doctor.py \
            doctor.cmd iniciar.sh iniciar.cmd iniciar.ps1; do
  [[ -e "$AQUI/$item" ]] || { echo "aviso: falta $item" >&2; continue; }
  cp -R "$AQUI/$item" "$RAIZ/"
done

# Podado de lo que no debe viajar aunque este dentro de lo copiado.
rm -rf "$RAIZ/sistema/resultados"
find "$RAIZ" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$RAIZ" \( -name '.DS_Store' -o -name '*.pyc' -o -name '*.o' \) -delete 2>/dev/null || true
rm -f "$RAIZ/sistema/memoria-compartida-c/server" "$RAIZ/sistema/memoria-compartida-c/client"
rm -f "$RAIZ/sistema/control-dominio/micro" "$RAIZ/sistema/control-dominio/veredicto"
rm -f "$RAIZ/contrato/coherencia"
find "$RAIZ" -name 'README.md' -delete

rm -f "$DESTINO"
( cd "$STAGING" && zip -q -r "$DESTINO" reto-latencia-group2 -x '*.git*' )

echo "ZIP listo: $DESTINO"
echo "  peso:     $(du -h "$DESTINO" | cut -f1)"
echo "  archivos: $(unzip -l "$DESTINO" | tail -1 | awk '{print $2}')"
echo
echo "Comprobacion — nada de esto deberia aparecer:"
if unzip -l "$DESTINO" | grep -E 'docs/|resultados/|__pycache__|\.pyc|README\.md|LEEME-ENTREGABLE|hacer-zip\.sh|contrato/coherencia$'; then
  echo "  !! el ZIP trae algo que no deberia" >&2; exit 1
else
  echo "  ok: sin docs/, sin resultados/, sin README, sin artefactos"
fi
