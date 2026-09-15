# Reto de Latencia Mínima — Plan de trabajo del equipo (Group 2)

> Propuesta de arranque. **[RECOM]** = decisión mía como arquitecto, sujeta a discusión del equipo.
> Enunciado literal: `ENUNCIADO.md` · Fecha límite: **29/09/2026** (cierre del módulo).

---

## 1. El problema con el enfoque obvio

El enunciado pide latencia **< 1 ms**. El enfoque natural de un equipo de 4 es: elegir una
tecnología, implementarla entre todos, medir, entregar.

**Ese enfoque desperdicia el ejercicio y desperdicia al equipo.**

Dos razones:

- **El objetivo se cumple trivialmente.** Un socket TCP en loopback da 20–50 µs, es decir 20–50×
  por debajo del umbral. Cuatro personas trabajando para conseguir un número que se alcanza en
  40 líneas de código es sobreingeniería de esfuerzo.
- **Cuatro personas en un solo camino se estorban.** Un servidor de eco no se divide en cuatro.

## 2. Enfoque propuesto **[RECOM]**

**Convertir la entrega en un estudio comparativo de transportes, no en una implementación.**

Cada integrante implementa **una variante distinta** del mismo sistema (mismo estímulo, misma
respuesta, misma metodología de medición). El entregable no es "logramos 300 ns" sino:

> *"Medimos cuatro arquitecturas de comunicación bajo condiciones idénticas, obtuvimos un rango de
> 4 órdenes de magnitud, y estas son las razones arquitectónicas para elegir una u otra según los
> atributos de calidad que priorice el negocio."*

Por qué esto es mejor:

| Criterio | Implementación única | Estudio comparativo |
|---|---|---|
| Divide el trabajo en 4 | ✗ se estorban | ✓ paralelo real |
| Cumple el umbral de 1 ms | ✓ | ✓ (y muestra dónde falla) |
| Demuestra los conceptos del módulo | parcialmente | ✓ atributos medibles, restricciones, trade-offs, ADR |
| Aplica la 1.ª ley (*todo es un trade-off*) | no la evidencia | **es la tesis del trabajo** |
| Material para el video de 5 min | un número | una curva y una decisión |

Y encaja con el módulo: el temario del M1 es **atributos de calidad + restricciones + decisiones
+ trade-offs**. Este enfoque los ejercita todos; el enfoque obvio no ejercita ninguno.

## 3. Reparto de variantes

Cuatro niveles, del más "realista" al más extremo. Expectativas de orden de magnitud, no promesas.

> ⚠️ **Actualizado el 14/09: el equipo es de 3 personas.** Bryan Brack no participa.
> Reparto vigente en `../../../_Base-Conocimiento/EQUIPO.md`.

| Var. | Transporte | Responsable | RTT medido (p50) | Qué ilustra |
|---|---|---|---|---|
| **A** | HTTP/1.1 (REST) sobre TCP loopback | **Freddy** ⬜ | 50–200 µs *(esperado)* | La línea base «así se hace normalmente». **La más importante del informe** |
| **B** | TCP crudo, `TCP_NODELAY`, conexión persistente | Daniel ✅ | **13,4 µs** | Cuánto cuesta el protocolo de aplicación |
| **C** | Unix domain socket **o** UDP loopback | **Camilo** ⬜ | 8–20 µs *(esperado)* | Cuánto cuesta la pila de red. **Prescindible si no llega** |
| **D** | Memoria compartida + busy-spin | Daniel ✅ | **0,08 µs** | El límite físico, y todo lo que cuesta llegar ahí |
| **Bc** | *control:* TCP en C | Daniel ✅ | **11,5 µs** | Aísla lenguaje de transporte |
| **E** | *línea base:* ICMP (responde el kernel) | Daniel ✅ | **9,7 µs** / 17 ms a internet | Por qué `ping` no era un sistema; y el precio de la red real |

**[RECOM]** Asignar por comodidad de lenguaje, no por dificultad. La variante D es la más exótica
pero también la más corta en código; la A es la más fácil pero la que más piezas tiene.

Cada responsable entrega: código de su variante + su archivo de resultados crudos + media página
justificando sus decisiones técnicas (el "por qué", segunda ley de la arquitectura).

## 4. La pieza crítica: una sola metodología de medición

**Si cada uno mide a su manera, el estudio no vale nada.** Antes de escribir una línea de código
de las variantes hay que **congelar la especificación de medición** — ver `ESPEC-MEDICION.md`.

Esto no es burocracia: es la decisión arquitectónica central del ejercicio. El enunciado pide
*"explicación de cómo se mide la latencia"* como entregable explícito, y el mismo sistema puede
reportar 200 ns o 20 ms según dónde se pongan las sondas.

## 5. Cronograma contra las dos fechas que importan

```text
08/09 (hoy) ─┬─ Acordar enfoque con el equipo
             ├─ Escribir a la facilitadora: ¿entrega grupal o individual?
             └─ Congelar ESPEC-MEDICION.md  ← bloquea todo lo demás
09–10/09    ─── Asignar variantes · montar repo · harness común funcionando
11–14/09    ─── Cada uno implementa su variante y produce resultados crudos
15/09 (mar) ─── ENCUENTRO SINCRÓNICO
                 · llevar resultados preliminares
                 · preguntar al docente: alcance grupal, frontera de medición esperada
16–21/09    ─── Consolidar: tabla comparativa, histogramas, ADR
22–24/09    ─── Escribir PDF (arquitectura · justificación · metodología · resultados · ADR)
25–26/09    ─── Grabar video ≤ 5 min · revisión cruzada del equipo
27/09       ─── ENTREGA (2 días de colchón)
29/09 (mar) ─── ENCUENTRO SINCRÓNICO + demo en vivo · CIERRE DEL MÓDULO
```

⚠️ **El segundo encuentro cae el mismo día del cierre.** No dejar la entrega para el 29:
si algo falla ese día, no hay margen (Art. 5 — después del cierre no se califica).

## 6. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| La entrega es individual, no grupal | Medio | El estudio comparativo funciona igual: cada uno entrega el trabajo completo citando su variante como aporte propio. Confirmar el 15/09. |
| Cada integrante mide distinto | **Alto** — invalida el estudio | Congelar `ESPEC-MEDICION.md` **antes** de implementar. Harness compartido, no replicado. |
| Hardware distinto entre integrantes | Alto — resultados no comparables | Ejecutar la ronda final **en una sola máquina**. Registrar CPU/OS/kernel en el informe. |
| Un integrante no entrega su variante | Medio | 4 variantes con 3 sigue siendo un estudio válido. Definir hoy cuál es prescindible (la C). |
| Reportar promedios en vez de percentiles | **Alto** — error clásico que hunde la nota | Obligatorio p50/p99/p99.9/max. Está en la espec. |
| Confundir latencia bajo carga con latencia en vacío | Medio | Declararlo explícitamente en el informe: *closed-loop, una petición en vuelo*. |

## 7. Lo que NO hay que hacer

- **No sobreingeniar.** El sistema es un eco. No necesita base de datos, ni Docker, ni Kubernetes,
  ni un framework. Cualquier pieza que no reduzca latencia ni sirva a la medición, sobra —
  y el módulo penaliza conceptualmente la sobreingeniería.
- **No perseguir el número más bajo posible.** Perseguir el número es el error del ejercicio.
  La nota está en la metodología y en el análisis del trade-off.
- **No ocultar la cola.** Si el p99.9 se dispara, eso **es** el hallazgo interesante. Reportarlo
  vale más que esconderlo.

## 8. Primeras tres acciones

1. **Compartir este plan con el equipo** y acordar el enfoque (comparativo vs. implementación única).
2. **Escribir a la facilitadora** para resolver si la entrega es grupal o individual.
3. **Congelar `ESPEC-MEDICION.md`** y asignar variantes. Hasta que esto no esté, nadie codifica.
