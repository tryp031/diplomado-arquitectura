# Plan de trabajo — Reto de Latencia Mínima (Group 2)

> **Este es el documento maestro del reto.** Si algo no está aquí, no está planificado.
> Derivado del enunciado literal (`ENUNCIADO.md`), no de lo que ya hicimos.
> Creado 10/09/2026 · **Cierre inamovible: 29/09/2026** · Entrega objetivo: **27/09/2026**

---

## 1. Qué pide el enunciado, literalmente

### Requisitos del sistema

| # | Requisito | Cita | Estado |
|---|---|---|---|
| R1 | Escuchar permanentemente | «debe escuchar permanentemente peticiones o estímulos» | ✅ cumplido |
| R2 | Retornar una respuesta específica | «retornar una respuesta específica» | ✅ cumplido |
| R3 | Medir el tiempo transcurrido | «desde el envío del estímulo hasta la recepción» | ✅ cumplido |
| R4 | Latencia < 1 ms | «preferiblemente menor a un milisegundo» | ✅ cumplido (matizado) |

### Los cinco entregables

| # | Entregable | Formato | Estado real hoy |
|---|---|---|---|
| **E1** | Código fuente completo | **ZIP** | 🟡 el código existe, **no está empaquetado ni probado en limpio** |
| **E2** | Documentación técnica: arquitectura · justificación de herramientas · cómo se mide | **PDF** | 🟡 borrador de 14 páginas, **le faltan 2 de 4 variantes** |
| **E3** | Logs de ejecución del tiempo transcurrido | `.txt` `.log` `.png` | 🟡 existen 9 logs crudos, **sin curar ni seleccionar** |
| **E4** | Informe de resultados con comparación explícita contra 1 ms | **PDF** (puede fusionarse con E2) | 🟡 fusionado en el mismo PDF, mismo faltante |
| **E5** | Video ≤ 5 min **o** demo en vivo el 15/09 o 29/09 | **MP4** / presencial | 🔴 guion escrito, **nada grabado ni ensayado** |

### Aparte del reto

| | | |
|---|---|---|
| **Autoevaluación M1** | Cuestionario en Brightspace | 🔴 **un solo intento**, sin hacer |

> ⚠️ **Nada de lo que está en 🟡 se puede entregar tal cual.** Un borrador sin dos variantes
> no satisface E2 ni E4, y un directorio de código no es un ZIP probado.

---

## 2. Lista de tareas

Columnas: **ID · tarea · entregable que satisface · responsable · depende de · límite**

### Bloque 0 — Desbloqueo del equipo · *límite: 12/09*

| ID | Tarea | Para | Responsable | Depende de | Límite |
|---|---|---|---|---|---|
| **T01** | Enviar correo a la facilitadora: ¿entrega grupal o individual? | todos | Daniel | — | **11/09** |
| **T02** | **Cerrar en el grupo el reparto de A y C** con nombre y fecha | E1 E2 | todos | — | **12/09** |
| **T03** | Decidir enfoque: estudio comparativo vs implementación única | todos | todos | — | **12/09** |
| **T04** | Crear repositorio Git y subir el harness | E1 | *por asignar* | T03 | **12/09** |
| **T05** | Definir la máquina única de la ronda final | E4 | todos | — | **12/09** |
| **T06** | Congelar `ESPEC-MEDICION.md` con las enmiendas de ADR-001 y ADR-003 | E2 | Daniel + equipo | T03 | **12/09** |

> **T02 es la tarea crítica de todo el proyecto.** Sin ella no arranca el bloque 1, y el bloque 1
> es el más largo. Cada día de retraso aquí se paga entero al final.

### Bloque 1 — Implementación y medición · *límite: 20/09*

| ID | Tarea | Para | Responsable | Depende de | Límite |
|---|---|---|---|---|---|
| **T07** | Variante **A** — HTTP/1.1 (REST) sobre TCP, puerto 9100 | E1 | *por asignar* | T02 T06 | 17/09 |
| **T08** | Variante **C** — Unix domain socket o UDP, puerto 9102 | E1 | *por asignar* | T02 T06 | 17/09 |
| **T09** | Media página de justificación técnica de A (el «por qué», exigido por el enunciado) | E2 | resp. de A | T07 | 18/09 |
| **T10** | Media página de justificación técnica de C | E2 | resp. de C | T08 | 18/09 |
| **T11** | Revisión cruzada: que A y C respeten la frontera F1 y el contrato del CSV | E4 | Daniel | T07 T08 | 18/09 |
| **T12** | **Ronda final: 3 × 1 M de las 4 variantes en la máquina única** | E3 E4 | resp. de la máquina | T05 T11 | **20/09** |
| **T13** | Regenerar gráficas con las 4 series (`harness/graficas.py`) | E2 E4 | Daniel | T12 | 20/09 |

**Ya hecho en este bloque:** variante B (Python/TCP), variante D (memoria compartida/C), control
Bc (TCP/C), harness común, script de análisis, generador de gráficas, tres ADR.

### Bloque 2 — Documentación · *límite: 24/09*

| ID | Tarea | Para | Responsable | Depende de | Límite |
|---|---|---|---|---|---|
| **T14** | Completar `INFORME.md` §3.2, §6.3, §7 y §8.1 con los datos de A y C | E2 E4 | Daniel | T12 T13 | 22/09 |
| **T15** | Integrar las justificaciones técnicas de T09 y T10 en §4 | E2 | Daniel | T09 T10 | 22/09 |
| **T16** | **Corregir §8.1**: hoy afirma que A cumple el umbral, y eso aún no está medido | E4 | Daniel | T12 | **22/09** |
| **T17** | Revisión cruzada del informe completo por los 4 integrantes | E2 E4 | todos | T14 | 24/09 |
| **T18** | Generar el PDF final (`python3 informe-a-pdf.py`) | E2 E4 | Daniel | T17 | 24/09 |

### Bloque 3 — Empaquetado · *límite: 26/09*

| ID | Tarea | Para | Responsable | Depende de | Límite |
|---|---|---|---|---|---|
| **T19** | Curar los logs: elegir cuáles entran, verificar que muestran el tiempo medido | E3 | *por asignar* | T12 | 25/09 |
| **T20** | Armar el ZIP del código fuente con un README de cómo ejecutarlo | E1 | *por asignar* | T12 | 25/09 |
| **T21** | **Probar el ZIP en limpio**: descomprimir en otra carpeta y que compile y corra | E1 | otro integrante | T20 | **26/09** |

> **T21 no es burocracia.** Un ZIP que no corre en una máquina limpia es un entregable fallido,
> y no se descubre hasta que lo abre quien califica. Lo prueba alguien distinto de quien lo armó.

### Bloque 4 — Video o demo · *límite: 26/09*

| ID | Tarea | Para | Responsable | Depende de | Límite |
|---|---|---|---|---|---|
| **T22** | Decidir quién asiste al encuentro del 29/09 → define video o demo en vivo | E5 | todos | — | 20/09 |
| **T23** | Actualizar `GUION-VIDEO.md` con los datos de A y C | E5 | Daniel | T12 | 24/09 |
| **T24** | Ensayo cronometrado (el primero siempre se pasa de 5 min) | E5 | quien presente | T23 | 25/09 |
| **T25** | Grabar el video MP4 ≤ 5 min **o** preparar la demo en vivo | E5 | quien presente | T24 | **26/09** |

### Bloque 5 — Autoevaluación · *independiente, límite 29/09*

| ID | Tarea | Para | Responsable | Depende de | Límite |
|---|---|---|---|---|---|
| **T26** | Bajar del aula los 4 Genially y el video de YouTube | — | cada uno | — | 15/09 |
| **T27** | Estudiar: leyes de la arquitectura + taxonomía de atributos de calidad | — | cada uno | T26 | 20/09 |
| **T28** | **Hacer la autoevaluación M1 — UN SOLO INTENTO** | — | cada uno | T27 | **25/09** |

> **T28 con colchón deliberado de 4 días.** Si Brightspace falla el 29, no hay segunda
> oportunidad y se pierde la nota entera del cuestionario.

### Bloque 6 — Entrega · *límite: 27/09*

| ID | Tarea | Para | Responsable | Depende de | Límite |
|---|---|---|---|---|---|
| **T29** | Subir E1, E2, E3, E4, E5 a Brightspace | todos | *por asignar* | T18 T19 T21 T25 | **27/09** |
| **T30** | Verificar que la plataforma registró la entrega (captura de pantalla) | — | mismo | T29 | 27/09 |

---

## 3. Ruta crítica

```text
T02 ──▶ T07/T08 ──▶ T11 ──▶ T12 ──▶ T14 ──▶ T17 ──▶ T18 ──▶ T29
reparto  variantes  revisión  ronda   informe  revisión  PDF    entrega
12/09     17/09      18/09   20/09    22/09    24/09    24/09   27/09
```

**Holgura real: 2 días** (27/09 → 29/09). No es mucho. Cualquier tarea de la ruta crítica que
se retrase un día empuja todo lo demás.

Las tareas **fuera** de la ruta crítica (T19, T20, T25, T26–T28) pueden avanzar en paralelo y
**conviene adelantarlas**, porque son las que se olvidan.

---

## 4. Fechas que gobiernan

| Fecha | Qué pasa |
|---|---|
| **11/09** | Correo a la facilitadora |
| **12/09** | Reparto cerrado. **Si no, el plan se retrasa entero** |
| **15/09 18:00** | Encuentro sincrónico. Llevar resultados y preguntar por la frontera de medición |
| **20/09** | Ronda final medida |
| **25/09** | Autoevaluación hecha (colchón de 4 días) |
| **27/09** | **Entrega** |
| **29/09** | Cierre del módulo + segundo encuentro. Después **no se califica** |

> ⚠️ El segundo encuentro cae **el mismo día del cierre**. Quien elija demo en vivo el 29/09
> está apostando la nota de E5 a que ese día no falle nada. **Recomendación: grabar el video
> igualmente**, aunque se piense asistir. Cuesta 30 minutos y elimina el riesgo.

---

## 5. Preguntas para el docente el 15/09

Llevarlas escritas. Son las tres que cambian el trabajo según la respuesta:

1. **¿Qué frontera de medición espera?** ¿RTT de aplicación completo, o acepta medidas parciales?
2. **Un sistema con mediana de 13 µs y máximo de 44 ms, ¿cumple el objetivo de 1 ms o no?**
   Es la pregunta que decide cómo se redacta el informe de resultados.
3. **¿Espera medición con red física entre dos máquinas, o acepta loopback?**

Y la administrativa, si no respondió la facilitadora: ¿la entrega es grupal o individual?

---

## 6. Contingencias

| Si pasa esto | Entonces |
|---|---|
| **El equipo no responde antes del 12/09** | Daniel sigue solo. Con B, Bc y D ya hay un estudio válido; se ajusta el informe para no prometer cuatro variantes. **Decidirlo el 12, no el 25** |
| Un integrante no entrega su variante | Se entrega con tres. La prescindible es la **C** (su resultado es el más predecible) |
| La entrega resulta ser individual | Cada uno entrega el estudio completo citando su variante como aporte propio. No cambia el trabajo, cambia el empaquetado |
| No hay máquina común para la ronda final | Se corre todo en la de Daniel (Apple M4, ya caracterizada) y se declara en el informe |
| El docente pide otra frontera de medición | Los CSV crudos permiten recalcular. Nuevo ADR que supersede a ADR-001 |

---

## 7. Reglas de trabajo del equipo

Tres, no más. Los equipos de estudio mueren por exceso de proceso o por ausencia total de él.

1. **Lo acordado va al mensaje fijado del grupo de WhatsApp.** Lo que no está fijado, no se
   acordó.
2. **El código va al repositorio, nunca por WhatsApp.** Los archivos por chat se pierden y no
   tienen versión.
3. **Nadie cambia la metodología de medición por su cuenta.** Si algo de `ESPEC-MEDICION.md`
   no sirve para tu variante, se discute y se escribe un ADR. Cambiarla en silencio invalida la
   comparación de los cuatro.

---

## 8. Dónde está cada cosa

| Documento | Para qué sirve |
|---|---|
| **`PLAN-DE-TRABAJO.md`** | **este archivo — la lista de tareas. El maestro** |
| `ENUNCIADO.md` | transcripción literal del enunciado |
| `INFORME.md` / `INFORME.pdf` | entregables E2 y E4 |
| `GUION-VIDEO.md` | entregable E5: guion del video y de la demo |
| `DISENO-ARQUITECTURA.md` | drivers, atributos de calidad, trade-offs. Alimenta el informe |
| `ESPEC-MEDICION.md` | metodología de medición común. **Pendiente de congelar (T06)** |
| `PLAN-EQUIPO.md` | propuesta original del enfoque comparativo |
| `harness/README.md` | **el contrato: qué debe cumplir cada variante.** Es lo que necesita quien implemente A o C |
| `comunicaciones/` | mensajes al equipo, correo a la facilitadora, kit de WhatsApp, guion de reunión |
| `_Base-Conocimiento/ADR/` | ADR-001 frontera · ADR-002 variante D · ADR-003 reloj |
