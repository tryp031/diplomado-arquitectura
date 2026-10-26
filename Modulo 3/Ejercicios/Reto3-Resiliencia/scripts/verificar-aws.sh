#!/usr/bin/env bash
# Chequeo previo a la corrida oficial en AWS. Solo lee: no invoca ni modifica nada.
#   scripts/verificar-aws.sh                                  # usa .env.aws (como el Reto 2)
#   AWS_PROFILE=<perfil-solo-lectura> scripts/verificar-aws.sh  # o un perfil de ~/.aws
# Verifica que el despliegue a mano (consola) quedó con el código y la regla de este repo:
#   1. reto3-router tiene PERMANENCIA_MINUTOS, UMBRAL_DEGRADADO y UMBRAL_MINIMO esperados.
#   2. Las cuatro Lambdas tienen el mismo código (CodeSha256): comparten src/.
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
PERMANENCIA="${PERMANENCIA_ESPERADA:-2}"
fallas=0
mal() { echo "  ✗ $*"; fallas=$((fallas + 1)); }
bien() { echo "  ✓ $*"; }

echo "Cuenta: $(aws sts get-caller-identity --query Arn --output text)"

echo "Router (variables)"
read -r perm deg mini mod < <(aws lambda get-function-configuration --function-name reto3-router \
  --query '[Environment.Variables.PERMANENCIA_MINUTOS, Environment.Variables.UMBRAL_DEGRADADO, Environment.Variables.UMBRAL_MINIMO, LastModified]' \
  --output text)
[[ "$perm" == "$PERMANENCIA" ]] && bien "PERMANENCIA_MINUTOS=$perm" || mal "PERMANENCIA_MINUTOS=$perm (se espera $PERMANENCIA)"
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
# Código desplegado a mano el 22/10, antes de la permanencia (ADR-001). Si sigue ahí, no se redesplegó.
SHA_REGLA_ANTERIOR="sfv7EsQ5BHMPAoW3MjbsoYuwWTwh6ues9d/rILwDr4w="
[[ "${hashes[0]}" != "$SHA_REGLA_ANTERIOR" ]] && bien "el código ya no es el del 22/10" \
  || mal "el código sigue siendo el del 22/10 (regla anterior): falta subir el .zip nuevo"

echo "DynamoDB"
estado=$(aws dynamodb describe-table --table-name reto3-estado --query Table.TableStatus --output text)
[[ "$estado" == "ACTIVE" ]] && bien "reto3-estado $estado" || mal "reto3-estado $estado"

if (( fallas )); then echo "RESULTADO: $fallas problema(s). No correr el k6 oficial todavía." >&2; exit 1; fi
echo "RESULTADO: listo para calentar y correr el k6 oficial."
