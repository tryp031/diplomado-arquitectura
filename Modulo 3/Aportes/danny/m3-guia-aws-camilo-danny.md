# Guía para Camilo: acceso AWS para el Reto 3

> **Para:** Camilo (dueño de la cuenta AWS del equipo). **De:** Danny. **Fecha:** 2026-10-18.
> **Tiempo estimado:** 20 minutos. **Región:** `us-east-2`, la misma del Reto 2.
> **Qué necesitamos:** un usuario IAM **solo para desplegar el Reto 3**, que no pueda tocar nada fuera de los recursos
> `reto3-*`, y una alarma de presupuesto. El usuario se borra después del cierre del módulo (03/11).

## Por qué lo pedimos así

- **El usuario `user-boto3-solo-lectura` del Reto 2 no alcanza:** solo lee logs y colas. Para el Reto 3 hay que crear
  Lambdas, un API Gateway, una tabla de DynamoDB y roles.
- **Todo se despliega con una plantilla** (`template.yaml`, CloudFormation/SAM). No hay nada que configurar a mano en la
  consola, y lo que se despliega es lo mismo que va en el ZIP.
- **Todos los recursos se llaman `reto3-*`**, así que los permisos se pueden limitar a ese prefijo.

## Paso 1: Crear la política `Reto3-Despliegue`

Consola → **IAM** → **Policies** → **Create policy** → pestaña **JSON**. Pega esto y reemplaza **`<CUENTA>`** (en las
9 apariciones) por el ID de 12 dígitos de tu cuenta (arriba a la derecha en la consola):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {"Sid": "Identidad", "Effect": "Allow", "Action": "sts:GetCallerIdentity", "Resource": "*"},
    {"Sid": "CloudFormationStack", "Effect": "Allow", "Action": "cloudformation:*",
     "Resource": "arn:aws:cloudformation:us-east-2:<CUENTA>:stack/reto3/*"},
    {"Sid": "TransformSAM", "Effect": "Allow", "Action": "cloudformation:CreateChangeSet",
     "Resource": "arn:aws:cloudformation:us-east-2:aws:transform/Serverless-2016-10-31"},
    {"Sid": "CloudFormationLectura", "Effect": "Allow",
     "Action": ["cloudformation:ValidateTemplate", "cloudformation:ListStacks"], "Resource": "*"},
    {"Sid": "BucketArtefactos", "Effect": "Allow", "Action": "s3:*",
     "Resource": ["arn:aws:s3:::reto3-artefactos-<CUENTA>", "arn:aws:s3:::reto3-artefactos-<CUENTA>/*"]},
    {"Sid": "Lambdas", "Effect": "Allow", "Action": "lambda:*",
     "Resource": "arn:aws:lambda:us-east-2:<CUENTA>:function:reto3-*"},
    {"Sid": "ApiGateway", "Effect": "Allow",
     "Action": ["apigateway:GET", "apigateway:POST", "apigateway:PUT", "apigateway:PATCH", "apigateway:DELETE"],
     "Resource": ["arn:aws:apigateway:us-east-2::/restapis", "arn:aws:apigateway:us-east-2::/restapis/*",
                  "arn:aws:apigateway:us-east-2::/tags/*"]},
    {"Sid": "Tabla", "Effect": "Allow", "Action": "dynamodb:*",
     "Resource": "arn:aws:dynamodb:us-east-2:<CUENTA>:table/reto3-*"},
    {"Sid": "Logs", "Effect": "Allow", "Action": "logs:*",
     "Resource": ["arn:aws:logs:us-east-2:<CUENTA>:log-group:/aws/lambda/reto3-*",
                  "arn:aws:logs:us-east-2:<CUENTA>:log-group:/aws/lambda/reto3-*:*"]},
    {"Sid": "LogsConsultas", "Effect": "Allow",
     "Action": ["logs:DescribeLogGroups", "logs:StartQuery", "logs:GetQueryResults", "logs:StopQuery"], "Resource": "*"},
    {"Sid": "Dashboard", "Effect": "Allow",
     "Action": ["cloudwatch:PutDashboard", "cloudwatch:GetDashboard", "cloudwatch:DeleteDashboards"],
     "Resource": "arn:aws:cloudwatch::<CUENTA>:dashboard/reto3-*"},
    {"Sid": "Metricas", "Effect": "Allow",
     "Action": ["cloudwatch:GetMetricData", "cloudwatch:ListMetrics", "cloudwatch:ListDashboards"], "Resource": "*"},
    {"Sid": "RolesDeLasLambdas", "Effect": "Allow",
     "Action": ["iam:CreateRole", "iam:DeleteRole", "iam:GetRole", "iam:PassRole", "iam:TagRole", "iam:UntagRole",
                "iam:AttachRolePolicy", "iam:DetachRolePolicy", "iam:PutRolePolicy", "iam:DeleteRolePolicy",
                "iam:GetRolePolicy"],
     "Resource": "arn:aws:iam::<CUENTA>:role/reto3-*"}
  ]
}
```

Nombre de la política: **`Reto3-Despliegue`**. Descripción: «Despliegue del Reto 3 (diplomado). Borrar después del 03/11/2026».

## Paso 2: Crear el usuario `reto3-deployer`

IAM → **Users** → **Create user** → nombre **`reto3-deployer`** → **sin** acceso a la consola → **Attach policies
directly** → marca **`Reto3-Despliegue`** → **Create user**.

Después: abre el usuario → **Security credentials** → **Create access key** → caso de uso **Command Line Interface
(CLI)** → **Create**. Copia el *Access key ID* y el *Secret access key*.

## Paso 3: Alarma de presupuesto (recomendado)

**Billing → Budgets → Create budget → Zero spend budget** o **Monthly cost budget** de **USD 5**, con aviso a tu correo.
El Reto 3 debería costar centavos: unas 140 peticiones por corrida, dentro de la capa gratuita de Lambda, DynamoDB y API
Gateway. La alarma es por si alguien deja algo corriendo.

## Paso 4: Mandarme las llaves por un medio seguro

**Por favor, no las mandes por WhatsApp en texto plano.** Algunas opciones: un enlace de un solo uso (por ejemplo,
onetimesecret.com) o un gestor de contraseñas compartido. Mándame además el **ID de la cuenta**: los scripts lo usan
para no desplegar nunca en otra cuenta por error.

## Paso 4b (opcional): Lectura para el panel de control

El panel (`scripts/panel.sh`) **solo lee**: el estado por minuto de la tabla y los logs de las Lambdas. Si prefieres no
usar `reto3-deployer` para la demo, crea un usuario **`reto3-panel-lectura`** con esta política
(**`Reto3-PanelLectura`**):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {"Sid": "EstadoPorMinuto", "Effect": "Allow", "Action": ["dynamodb:BatchGetItem", "dynamodb:GetItem"],
     "Resource": "arn:aws:dynamodb:us-east-2:<CUENTA>:table/reto3-estado"},
    {"Sid": "LogsDeLasLambdas", "Effect": "Allow", "Action": "logs:FilterLogEvents",
     "Resource": "arn:aws:logs:us-east-2:<CUENTA>:log-group:/aws/lambda/reto3-*:*"}
  ]
}
```

Yo lo configuro como perfil `diplomado-lectura` y lo uso con `PANEL_AWS_PERFIL=diplomado-lectura scripts/panel.sh`.

## Paso 5: Al cerrar el módulo (después del 03/11)

1. Borrar el stack: CloudFormation → `reto3` → **Delete**. Esto borra las Lambdas, el API, la tabla, los logs y el dashboard.
2. Vaciar y borrar el bucket `reto3-artefactos-<CUENTA>`.
3. Borrar los usuarios `reto3-deployer` y `reto3-panel-lectura` y las políticas `Reto3-Despliegue` y `Reto3-PanelLectura`.

## Lo que hago yo con eso

```bash
aws configure --profile diplomado          # pego las llaves; región us-east-2
AWS_PROFILE=diplomado CUENTA_ESPERADA=<CUENTA> scripts/deploy.sh aws
```

El script **aborta** si el perfil no es `diplomado` o si la cuenta no coincide con `CUENTA_ESPERADA`.

## Riesgo que hay que conocer (para decidir con información)

Un usuario que puede crear roles y ponerles políticas inline (`iam:PutRolePolicy`) puede, en teoría, **darle a un rol
`reto3-*` más permisos de los necesarios**. SAM necesita esos permisos para crear los roles de las Lambdas. Lo
mitigamos con el prefijo `reto3-*`, una llave que vive 2 semanas y la alarma de presupuesto.

**Alternativa sin ese riesgo:** tú corres el despliegue con tu propio usuario (un solo comando, te paso todo listo) y a
mí me das solo lectura de los logs y el dashboard del Reto 3. Cuesta más coordinación: cada ajuste depende de que
estés disponible. Tú decides. Las dos opciones nos sirven.
