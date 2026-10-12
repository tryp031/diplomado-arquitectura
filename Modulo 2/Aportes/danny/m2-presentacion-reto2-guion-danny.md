# Reto 2 — Guion de la presentación (borrador)

> **Tipo:** `investigacion` — elaborado con IA para revisión del equipo. **No** es material oficial.
> **Deck:** `m2-presentacion-reto2-danny.html` (16 láminas, flechas para navegar, `N` muestra estas mismas notas, `T` cambia el tema).
> **Duración objetivo:** ~18 min de exposición + demo en vivo (el enunciado pide presentación y demo a quienes asisten al encuentro).
> **Estado:** borrador. Antes de exponer hay que cerrar tres decisiones (ver «Antes de exponer»).

## Antes de exponer

1. **Atributo priorizado.** El diseño local dice *desempeño* (latencia de la alerta); Camilo dice *disponibilidad/confiabilidad*. El deck asume desempeño con «no perder un Emergency» como restricción. El equipo elige uno y ajusta las láminas 3 y 16.
2. **Reparto de instancias en AWS.** Hoy es 10 + 2 = hasta 12 contra un límite de 10. Elegir (a) 8 + 2, (b) 9 + 1 o (c) API Gateway → SQS directo, y reemplazar el aviso de la lámina 12 por la decisión.
3. **Datos pendientes.** Una corrida local nueva desde el panel para llenar p95, duración y recepción → envío (lámina 10), y un «Mostrar original» de Gmail para medir la llegada real en los dos entornos.

## Guion por lámina

| # | Lámina | Quién (sugerido) | Tiempo | Qué decir |
|---|---|---|---|---|
| 1 | Portada | Danny | 40 s | El equipo y el reto en una frase. Anunciar el hilo conductor: un atributo priorizado, su costo, y todo lo demás deriva de ahí. |
| 2 | El problema | Danny | 1 min | 1000 eventos/30 s ≈ 35 r/s contra un rate de 15: lo que salva el 100 % es el burst de 2000. Hay dos criterios de tiempo (PDF: < 15 s desde la última petición; 06/10: < 16 s desde el Emergency hasta la llegada). Medimos los dos tramos que controlamos. |
| 3 | Atributo priorizado | Danny | 1 min 15 s | «Priorizamos la latencia de la alerta, porque es lo que se gradúa y lo que necesita el conductor, a costa de un posible duplicado y una pieza más.» No perder un Emergency es restricción dura (503 antes que un 200 mentiroso). |
| 4 | Diagrama | Danny | 1 min 15 s | Leer por columnas: cada rol tiene su equivalente local y AWS. Funciona porque el código local usa puertos y adaptadores. |
| 5 | Local | Danny | 1 min | Por qué local primero y a qué costo (demostrar cada equivalencia). El bug de nginx que no limitaba se encontró midiendo. |
| 6 | AWS | Camilo | 1 min 15 s | Despliegue paso a paso y validado. Región elegida con k6 en 4 regiones (una sola muestra con curl había dado lo contrario). Reintentos de ~39 s a ≤ 12 s. Calentador solo en la ventana de medición. |
| 7 | Decisiones | Freddy | 1 min 15 s | Leer la columna «a costa de». Responder 200 ya es lo que protege la latencia. |
| 8 | Tácticas | Freddy | 1 min 30 s | Por fila: táctica → componente → atributo → cómo ayuda al reto. Nombres del deck oficial (Control Resource Demand, Manage Resources, Retry, Exception detection). Pesa 1,0. |
| 9 | 200 vs 429 | Danny | 1 min 15 s | 200 = guardado, no enviado. La prueba negativa con burst 100 demuestra que el limitador funciona (102/898 y 522/478 ≈ 100 + 15 × 28). El 429 sigue abierto en los dos entornos. |
| 10 | Evidencias k6 | Camilo y Danny | 1 min 30 s | 1000/1000 en ambos; 1,33 s local y 1,642 s AWS contra 15 s. Aclarar qué mide cada número y que ninguno llega al buzón de Gmail. |
| 11 | Trazabilidad | Danny | 1 min | Contar `event_id` únicos, no peticiones. «Procesado» para Position = validado y registrado; para Emergency = `EMAIL_SENT`. El k6 del profesor genera 0, 1 o varios Emergency. |
| 12 | Instancias y HTTPS | Camilo | 1 min 30 s | Local cumple ≤ 10 (3) pero sin HTTPS; AWS tiene HTTPS pero 10 + 2 = 12. Decirlo nosotros, con las opciones (a)/(b)/(c) o con la decisión ya tomada. |
| 13 | Fallas | Danny | 1 min | Qué pasa si se cae el correo, la cola o el notifier, y cómo se recupera cada uno. Si hay tiempo, demostrarlo en la demo local. |
| 14 | Panel | Danny | 1 min + demo | Plano de control fuera del camino medido. Switch Local / AWS (en implementación). Demo: k6 local → medida y correo; switch a AWS → repetir; abrir Gmail. Plan B: local. |
| 15 | Riesgos | Freddy | 1 min 15 s | Cada riesgo con su acción: SES en spam (DMARC), AWS hecho a mano en la consola, 10 + 2, k6 del profesor, medida que no llega a Gmail, HTTPS local y 429, lógica duplicada. |
| 16 | Cierre | Danny | 40 s | Repetir la frase del atributo. Abrir preguntas. Las 16 respuestas preparadas están en `Aportes/camilo/m2-respuestas-exposicion-12.1-12.2.md`. |

## Datos usados y de dónde salen

| Dato | Valor | Fuente |
|---|---|---|
| Medida local (k6 del profesor, Gmail, 06/10) | 1000/1000 · 1,33 s | `m2-revision-aws-opcion-b-danny.md` §1 |
| Prueba del limitador local (burst 100) | 102/898 ráfaga · 522/478 ritmo | `Ejercicios/Reto2-Alerta-Flota/README.md` |
| AWS, carga completa (11/10) | 1000/1000 · 0 % fallos · avg 119,65 ms · p95 129,09 ms | `Aportes/camilo/m2-aws-opcion-b-camilo/arquitectura-aws-opcion-b.md` §9 paso 5 |
| AWS, duración y tasa | ~22,5 s · 44,7 r/s | `m2-respuestas-exposicion-12.1-12.2.md` preguntas 4 y 11 |
| AWS, medida tipo rúbrica | 1,642 s (última petición en ingesta → `EMAIL_SENT`) | idem, pregunta 12 (script `medir-aws.py`, no versionado) |
| AWS, un Emergency | 1,66 s de recepción a `EMAIL_SENT`, con arranque en frío | `arquitectura-aws-opcion-b.md` §9 paso 4 |
| AWS, reparto de concurrencia | 10 ingesta + 2 notifier | idem, «Corrección del reparto» |
| Región | us-east-2 (avg 186,4 ms con k6 contra STS) | idem §8 |

**Pendientes (no inventados):** p95, duración y recepción → envío de la corrida local; la llegada real a Gmail en ambos entornos.
Los números de AWS los reporta Camilo y nadie más del equipo los ha verificado de forma independiente.
