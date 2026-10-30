#!/usr/bin/env bash
# Despliega la misma plantilla en LocalStack o en AWS.
#   scripts/deploy.sh localstack                                  # v3 (Modo=histeresis, la oficial)
#   PARAMETROS="Modo=reloj" scripts/deploy.sh localstack           # v1, para comparar
#   AWS_PROFILE=diplomado CUENTA_ESPERADA=<id de 12 dígitos de Camilo> scripts/deploy.sh aws
# Guarda: en esta máquina el perfil `default` es corporativo. Para AWS se exige el
# perfil `diplomado` Y que la cuenta coincida con CUENTA_ESPERADA; si no, aborta.
set -euo pipefail
cd "$(dirname "$0")/.."
ENTORNO="${1:?uso: deploy.sh localstack|aws}"
STACK=reto3
mkdir -p .build

if [[ "$ENTORNO" == localstack ]]; then
  unset AWS_PROFILE
  export AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_REGION=us-east-2 AWS_DEFAULT_REGION=us-east-2
  # AWS_ENDPOINT_URL aplica a TODOS los servicios. `--endpoint-url` no sirve: `cloudformation package`
  # sube a S3 con su propio cliente, que ignora esa opción e iría a AWS real.
  # localhost.localstack.cloud resuelve a 127.0.0.1 y admite el estilo virtual-host de S3.
  export AWS_ENDPOINT_URL=http://localhost.localstack.cloud:4566
  # El AWS CLI 2.2x usa por defecto un checksum (CRC64NVME) que LocalStack 3.8 rechaza.
  export AWS_REQUEST_CHECKSUM_CALCULATION=when_required AWS_RESPONSE_CHECKSUM_VALIDATION=when_required
  AWS=(aws)
  BUCKET=reto3-artefactos-local
  "${AWS[@]}" s3 mb "s3://$BUCKET" >/dev/null 2>&1 || true
elif [[ "$ENTORNO" == aws ]]; then
  [[ "${AWS_PROFILE:-}" == diplomado ]] || { echo "ABORTO: usa AWS_PROFILE=diplomado" >&2; exit 1; }
  # Región fija ANTES de cualquier llamada: un AWS_REGION heredado ganaría al AWS_DEFAULT_REGION.
  export AWS_REGION=us-east-2 AWS_DEFAULT_REGION=us-east-2
  CUENTA=$(aws sts get-caller-identity --query Account --output text)
  [[ "$CUENTA" == "${CUENTA_ESPERADA:?define CUENTA_ESPERADA}" ]] || { echo "ABORTO: cuenta $CUENTA != $CUENTA_ESPERADA" >&2; exit 1; }
  AWS=(aws)
  BUCKET="reto3-artefactos-$CUENTA"
  aws s3api head-bucket --bucket "$BUCKET" 2>/dev/null || aws s3 mb "s3://$BUCKET"
else
  echo "entorno desconocido: $ENTORNO" >&2; exit 1
fi

"${AWS[@]}" cloudformation package --template-file template.yaml --s3-bucket "$BUCKET" \
  --output-template-file .build/packaged.yaml >/dev/null
"${AWS[@]}" cloudformation deploy --template-file .build/packaged.yaml --stack-name "$STACK" \
  --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND --parameter-overrides "Entorno=$ENTORNO" ${PARAMETROS:-} --no-fail-on-empty-changeset

API_ID=$("${AWS[@]}" cloudformation describe-stacks --stack-name "$STACK" \
  --query "Stacks[0].Outputs[?OutputKey=='ApiId'].OutputValue" --output text)
if [[ "$ENTORNO" == localstack ]]; then
  URL="http://localhost:4566/restapis/$API_ID/prod/_user_request_/service-api"
else
  URL="https://$API_ID.execute-api.us-east-2.amazonaws.com/prod/service-api"
fi
echo "$URL" | tee ".build/url-$ENTORNO.txt"
