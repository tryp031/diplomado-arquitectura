# Mapa conceptual acumulativo

> Actualizado: 2026-09-08 (tras Módulo 1).
> **[CURSO]** = confirmado en el material · **[HIPÓTESIS]** = predicción para preparar terreno.

## Confirmado — Módulo 0 + Módulo 1

```mermaid
graph TD
    M0[Módulo 0: Inducción] --> P[Brightspace · reglamento · 70% para certificar]

    M1[Módulo 1: Fundamentos de<br/>Arquitectura de Software]
    M1 --> EST[Papel estratégico:<br/>negocio ↔ tecnología]
    M1 --> ROL[Responsabilidades del arquitecto]
    M1 --> DIM[Tres dimensiones]
    DIM --> D1[Estructuración de la complejidad]
    DIM --> D2[Análisis temprano de<br/>atributos de calidad]
    DIM --> D3[Decisiones técnicas informadas]
    M1 --> LEY[Leyes y alcance de la arquitectura]
    M1 --> RES[Restricciones:<br/>negocio · tecnología · equipo]
    M1 --> AQ[Atributos de calidad]
    AQ --> OP[Operacionales]
    AQ --> ESR[Estructurales]
    AQ --> TR[Transversales]
    AQ --> ISO[ISO/IEC 25010]
    RES --> DEC[Decisiones arquitectónicas]
    D2 --> DEC
    DEC --> EVO[Evolución del sistema]
```

## Conceptos recurrentes (aparecen en ≥2 lugares)

| Concepto | Dónde aparece |
|---|---|
| **Latencia / rendimiento** | M1 temario (atributos operacionales) · M1 actividad (reto < 1 ms) |
| **Seguridad** | M1 temario (transversales) · M1 complementarios (OWASP, CWE, SAFECode, SAST/DAST) |
| **Mantenibilidad** | M1 temario (estructurales) · M1 conclusiones |
| **Disponibilidad / resiliencia** | M1 conclusiones · M1 complementarios (DR en AWS ×4, Netflix HA, Circuit Breaker) |
| **Trade-offs** | Prompt maestro · primera ley de la arquitectura (M1) |

## Hipótesis de recorrido — módulos 2 a 4 **[HIPÓTESIS]**

Los 14 recursos complementarios del M1 son la mejor pista disponible: se agrupan en
**resiliencia/DR (AWS)**, **estrategias de despliegue** y **seguridad**. Sumado al perfil del
docente (AWS, Kafka, Kubernetes, event-driven, banca):

```mermaid
graph LR
    M1[M1: Fundamentos<br/>atributos de calidad] --> M2[M2 ?: Estilos y patrones<br/>monolito modular · microservicios<br/>event-driven · Kafka]
    M2 --> M3[M3 ?: Cloud<br/>AWS · contenedores · Kubernetes<br/>serverless · IaC · CI/CD]
    M3 --> M4[M4 ?: Resiliencia · DR<br/>observabilidad · seguridad · FinOps]
```

**No confirmado.** Los temarios de los módulos 2–4 no están publicados.
