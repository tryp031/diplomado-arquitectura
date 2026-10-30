#!/usr/bin/env bash
# Chequeo previo a la corrida oficial en AWS. Solo lee: no invoca ni modifica nada.
#   scripts/verificar-aws.sh                                  # usa .env.aws (como el Reto 2)
#   AWS_PROFILE=<perfil-solo-lectura> scripts/verificar-aws.sh  # o un perfil de ~/.aws
# Verifica que el despliegue a mano (consola) quedó con el código y la regla de este repo:
#   1. reto3-router está en MODO=histeresis (v3, ADR-002) con RACHA_N2/RACHA_N1 y los umbrales esperados.
#   2. Las cuatro Lambdas tienen el código de ESTE checkout: su CodeSha256 es el del .zip de
#      scripts/empaquetar.py (determinista), que es el que se sube a mano en la consola.
#   3. La tabla reto3-estado está activa.
# Sale con 1 si algo no cuadra: en ese caso NO se corre el k6 oficial.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -z "${AWS_PROFILE:-}" && -f .env.aws ]]; then
  # Solo las tres variables del archivo; cualquier llave ya exportada en el shell se descarta.
  unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
  set -a; source .env.aws; set +a
  [[ -n "${AWS_ACCESS_KEY_ID:-}" && -n "${AWS_SECRET_ACCESS_KEY:-}" ]] || {
    echo "ABORTO: .env.aws incompleto (faltan AWS_ACCESS_KEY_ID o AWS_SECRET_ACCESS_KEY)" >&2; exit 1; }
elif [[ -z "${AWS_PROFILE:-}" || "$AWS_PROFILE" == "default" ]]; then
  echo "ABORTO: cree .env.aws (copie .env.aws.example) o use AWS_PROFILE con un perfil de solo lectura (nunca default)" >&2
  exit 1
fi
export AWS_REGION=us-east-2
MODO_ESPERADO="${MODO_ESPERADO:-histeresis}"
PERMANENCIA="${PERMANENCIA_ESPERADA:-2}"
fallas=0
mal() { echo "  ✗ $*"; fallas=$((fallas + 1)); }
bien() { echo "  ✓ $*"; }

echo "Cuenta: $(aws sts get-caller-identity --query Arn --output text)"

echo "Router (variables)"
read -r modo r2 r1 perm deg mini mod < <(aws lambda get-function-configuration --function-name reto3-router \
  --query '[Environment.Variables.MODO, Environment.Variables.RACHA_N2, Environment.Variables.RACHA_N1, Environment.Variables.PERMANENCIA_MINUTOS, Environment.Variables.UMBRAL_DEGRADADO, Environment.Variables.UMBRAL_MINIMO, LastModified]' \
  --output text)
# Sin la variable, el código asume histeresis; igual se exige explícita para que la evidencia no dependa de un default.
[[ "$modo" == "$MODO_ESPERADO" ]] && bien "MODO=$modo" || mal "MODO=$modo (se espera $MODO_ESPERADO)"
if [[ "$MODO_ESPERADO" == histeresis ]]; then
  [[ "$r2" == "30" ]] && bien "RACHA_N2=30" || mal "RACHA_N2=$r2 (se espera 30)"
  [[ "$r1" == "40" ]] && bien "RACHA_N1=40" || mal "RACHA_N1=$r1 (se espera 40)"
else
  [[ "$perm" == "$PERMANENCIA" ]] && bien "PERMANENCIA_MINUTOS=$perm" || mal "PERMANENCIA_MINUTOS=$perm (se espera $PERMANENCIA)"
fi
[[ "$deg" == "5" ]] && bien "UMBRAL_DEGRADADO=5" || mal "UMBRAL_DEGRADADO=$deg (se espera 5)"
[[ "$mini" == "10" ]] && bien "UMBRAL_MINIMO=10" || mal "UMBRAL_MINIMO=$mini (se espera 10)"
echo "  · última modificación: $mod"

echo "Código de las cuatro Lambdas"
declare -a hashes=()
for fn in reto3-router reto3-nivel1 reto3-nivel2 reto3-nivel3; do
  read -r sha mod < <(aws lambda get-function-configuration --function-name "$fn" \
    --query '[CodeSha256, LastModified]' --output text)
  echo "  · $fn  ${sha:0:12}…  $mod"
  hashes+=("$sha")
done
[[ $(printf '%s\n' "${hashes[@]}" | sort -u | wc -l) -eq 1 ]] && bien "las cuatro tienen el mismo código" \
  || mal "el código difiere entre funciones: falta subir el mismo .zip a las cuatro"
# El código viejo ignora MODO: sin esta comparación, una variable bien puesta sobre un .zip viejo pasaría.
SHA_ESPERADO=$(python3 scripts/empaquetar.py --sha)
[[ "${hashes[0]}" == "$SHA_ESPERADO" ]] && bien "es el código de este checkout (${SHA_ESPERADO:0:12}…)" \
  || mal "no es el código de este checkout (se espera ${SHA_ESPERADO:0:12}…): subir .build/reto3-src.zip de scripts/empaquetar.py"

echo "DynamoDB"
estado=$(aws dynamodb describe-table --table-name reto3-estado --query Table.TableStatus --output text)
[[ "$estado" == "ACTIVE" ]] && bien "reto3-estado $estado" || mal "reto3-estado $estado"

if (( fallas )); then echo "RESULTADO: $fallas problema(s). No correr el k6 oficial todavía." >&2; exit 1; fi
echo "RESULTADO: listo para calentar y correr el k6 oficial."
