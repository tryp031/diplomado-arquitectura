# Nota para el profesor — envío del Reto 2 en Brightspace

> Texto que acompaña `Entregable Reto 2.zip` en «Evidencia de aprendizaje: actividad M2».
> El envío es **individual**: cada integrante sube el mismo ZIP con esta nota antes del **20/10/2026**.
> El ZIP contiene los 4 archivos generados el 18/10 (ver PR #53).

---

**Actividad M2 — Reto 2: Alerta temprana para flota vehicular · Group 2**
Integrantes: Daniel Mazo Serna · Freddy Aparicio Marín · Camilo Céspedes Leguizamón

Profesor Diego, adjuntamos la evidencia del Reto 2 en `Entregable Reto 2.zip`, que contiene:

1. **`Entregable-1-Codigo-Fuente-Group2.zip`**: código fuente. `aws/` tiene las dos Lambdas desplegadas en AWS (solución oficial, us-east-2) y `local/` tiene la misma arquitectura en Docker, con pruebas, scripts de k6 y el panel de control usado en la demo. El `README.md` de la raíz explica la estructura.
2. **`Entregable-2-Documentacion-Tecnica-Group2.pdf`**: documentación técnica con el atributo de calidad priorizado (desempeño y escalabilidad, sin perder un Emergency), las decisiones de arquitectura, las tácticas y el modelo C4.
3. **`Entregable-3-Logs-Ejecucion-Group2.zip`**: logs de la corrida oficial en AWS del 13/10 (`.log` y `.csv`) con la recepción del Emergency (`EMERGENCY_RECEIVED`) y el envío del correo (`EMAIL_SENT`), más la captura del correo recibido en Gmail. Resultado: 1000/1000 peticiones aceptadas y correo enviado 0,644 s después de la última petición de k6 (llegada al buzón en ≤ 1,35 s).
4. **`Entregable-4-Presentacion-Group2.pdf`**: la presentación expuesta con demo en vivo en el encuentro del 13/10.

**Cómo ejecutar el proyecto en local** (requiere Docker Desktop y k6):

```
cd local
cp .env.example .env          # en Windows: copy .env.example .env
docker compose --profile dev --profile panel up -d --build
k6 run k6/profesor.js         # su script; solo se cambió la URL al endpoint local
```

- Con el `.env` de ejemplo **no hace falta ninguna credencial**: los correos llegan a Mailpit (`http://localhost:8025`) y el panel de control queda en `http://localhost:8090`.
- **Para recibir el correo en Gmail:** en `.env`, active el bloque de Gmail que trae `.env.example` (`SMTP_USER`, `SMTP_PASSWORD` con una App Password de Google, `MAIL_FROM` y `MAIL_TO`).
- **`.env.aws` (opcional):** solo sirve para que el panel observe la versión en AWS. Requiere la URL del API y credenciales IAM de solo lectura de nuestra cuenta, que por seguridad no se incluyen. La versión en AWS se verifica con los logs y la captura del Entregable 3; si desea verla en vivo, podemos hacer la demostración.

Las brechas que conocemos están declaradas en `aws/README.md` y en la presentación.

Quedamos atentos. — Group 2
