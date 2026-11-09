# Foro M4 — publicación de Danny

> PUBLICADO en Brightspace el 09/11/2026 por Danny, redactado por él a partir del borrador v2 (3 secciones).
> Texto tal cual se publicó. Fuentes en `FUENTES.md`.

---

**1. Aprendizajes y retos del workshop**

Durante el workshop trabajamos en grupo dos implementaciones con AWS SAM: una API utilizando API Gateway, Lambda y DynamoDB, y otra incorporando trazabilidad con X-Ray y notificaciones mediante SNS. Mi compañero Camilo realizó el despliegue en AWS, mientras yo analicé el código, los videos y los resultados, relacionándolos con nuestros retos anteriores.

Mi principal aprendizaje fue que la observabilidad no consiste únicamente en recopilar métricas, logs y trazas, sino en interpretarlos correctamente para tomar decisiones.

Esto quedó claro al revisar dos problemas: las métricas EMF parecían no existir porque estaban agrupadas bajo dimensiones diferentes, y algunos contadores mostraban valores incorrectos porque utilizábamos Average en lugar de Sum.

También identifiqué que el código enviaba siempre el mismo identificador en las notificaciones SNS. Esto demuestra que un proceso puede ejecutarse correctamente y aun así generar información equivocada.

**2. Experiencia previa y oportunidades de mejora**

En el Reto 3 utilizamos logs estructurados y un panel conectado a CloudWatch para analizar las transiciones del sistema. Gracias a esto descubrimos que AWS seguía ejecutando una versión anterior de nuestra lógica.

En mi experiencia laboral utilizamos Grafana para centralizar métricas, logs y trazas, con instrumentación basada en OpenTelemetry. Esto me permitió comparar el enfoque nativo de AWS del workshop con una solución que integra múltiples servicios y proveedores.

Como oportunidades de mejora, incorporaría correlación mediante traceId, alertas sobre errores y latencia, y automatización de dashboards y alarmas como infraestructura en código. También reforzaría la protección de datos sensibles y el principio de mínimo privilegio.

**3. Análisis del dashboard SquaredUp**

El dashboard CTO Application Overview presenta una visión ejecutiva del estado de los servicios en AWS y Azure, integrando métricas de errores, latencia, disponibilidad, dependencias externas y costos.

Considero que permite identificar rápidamente si existe un problema, pero no necesariamente explicar su causa, ya que no muestra directamente los logs ni las trazas.

Como mejora, agregaría indicadores de negocio, como transacciones exitosas por minuto, y acceso directo a las trazas para investigar incidentes.

Mi conclusión: la observabilidad aporta verdadero valor cuando permite pasar de detectar un problema a comprender su origen y tomar acciones oportunas para solucionarlo.
