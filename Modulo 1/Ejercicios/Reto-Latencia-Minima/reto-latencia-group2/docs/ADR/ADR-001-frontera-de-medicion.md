# ADR-001 — Frontera de medición de la latencia

**Estado:** Propuesta *(pendiente de aceptación por Group 2)*
**Fecha:** 2026-09-10
**Decisores:** Daniel Mazo Serna — propuesta para Group 2 (Freddy Aparicio, Bryan Brack, Camilo Céspedes)
**Contexto del módulo / ejercicio:** Módulo 1 · Actividad M1 «Reto de Latencia Mínima»

## Contexto

El enunciado exige medir «el tiempo transcurrido desde el envío del estímulo hasta la recepción
de la respuesta» y pide como entregable explícito la *explicación de cómo se mide la latencia*.

El enunciado **no** define dónde empiezan y terminan las sondas, y esa indefinición no es un
detalle: el mismo binario, sin cambiar una línea, reporta entre ~5 µs y ~50 ms según dónde se
coloquen. Con un objetivo fijado en 1 ms, la elección de frontera decide por sí sola si el
sistema cumple o incumple.

Fuerzas en juego:

- Cuatro integrantes implementan cuatro transportes distintos. Si cada uno elige su frontera,
  los resultados no son comparables y el estudio comparativo pierde su tesis (atributo AC-3).
- Cada frontera es defendible ante alguien; solo algunas son honestas ante todos.
- No se conoce aún qué frontera espera el docente (se preguntará el 15/09). La decisión debe
  tomarse ahora igualmente: bloquea la implementación de las cuatro variantes.

## Problema

¿Entre qué dos instantes exactos se mide la latencia, y quién los observa?

## Opciones consideradas

### Opción F1 — RTT de aplicación en el cliente
`t0` inmediatamente antes de la llamada de escritura; `t1` inmediatamente después de que la
respuesta esté **completamente leída** en espacio de usuario del cliente.

- **Ventajas:** es lo que percibe un consumidor real del servicio. Un solo reloj, sin problema
  de sincronización. Incluye todo lo que el sistema hace realmente: serialización, transporte,
  cambios de contexto, despertar del planificador. Implementable idénticamente en las cuatro
  variantes y en cualquier lenguaje.
- **Desventajas:** incluye coste del lenguaje del cliente (en Python, varios µs de intérprete),
  lo que castiga a las variantes escritas en lenguajes de alto nivel. Da el número más alto de
  todas las opciones defendibles.

### Opción F2 — Solo la llamada al sistema
Cronometrar exclusivamente `send` + `recv`, excluyendo el bucle de lectura completa y el manejo
de resultados parciales.

- **Ventajas:** aísla mejor el coste del transporte. Menos ruido del lenguaje.
- **Desventajas:** **esconde el coste real de recibir.** TCP es un flujo: una respuesta puede
  llegar fragmentada, y esa fragmentación es parte de la latencia que sufre el consumidor.
  Además no tiene análogo limpio en la variante D, que no hace llamadas al sistema — lo que
  rompe AC-3.

### Opción F3 — Incluir el establecimiento de la conexión
Cronometrar desde el `connect` hasta la respuesta, por iteración.

- **Ventajas:** representa fielmente a un cliente sin conexión persistente (por ejemplo, HTTP
  sin `keep-alive`), que es un caso real y frecuente.
- **Desventajas:** mide mayoritariamente el handshake, no el servicio. Con conexión persistente
  —que es el diseño elegido— el coste se paga una sola vez y repartirlo por iteración es
  falsear. No tiene sentido en la variante D.

### Opción F4 — Incluir el arranque del proceso
Desde la ejecución del binario hasta la respuesta.

- **Ventajas:** ninguna relevante para este ejercicio. Sería válida si el requisito fuese sobre
  arranque en frío (*cold start*), que es un atributo real en serverless.
- **Desventajas:** el resultado lo domina la carga del runtime (~50 ms en Python). No mide el
  sistema que se diseñó.

### Opción F5 — Latencia de una sola dirección (*one-way*)
`t0` en el cliente al enviar; `t1` en el servidor al recibir.

- **Ventajas:** da el número más bajo y aísla la dirección de ida.
- **Desventajas:** **técnicamente inválida en este montaje.** Exige dos relojes sincronizados
  con precisión mejor que la magnitud medida; entre dos procesos, el desfase y la deriva del
  reloj son del mismo orden que la latencia que se pretende medir. Un número obtenido así no
  significa nada, aunque parezca preciso.

## Decisión

Se elige **F1 — RTT de aplicación medido en el cliente**, con esta definición operativa:

```text
t0 = reloj monótono, inmediatamente ANTES de la llamada de escritura del estímulo
t1 = reloj monótono, inmediatamente DESPUÉS de que los N bytes de la respuesta
     estén completamente leídos en el buffer del cliente
latencia = t1 - t0
```

**Incluye:** serialización, escritura, transporte, procesamiento en el servidor, escritura de
la respuesta, transporte de vuelta, lectura completa, cambios de contexto y despertares del
planificador ocurridos en medio.

**Excluye:** establecimiento de la conexión (se paga una sola vez, durante el warmup), arranque
del proceso, y el warmup mismo.

**Vinculante para las cuatro variantes.** Ninguna puede redefinirla por su cuenta.

## Justificación

Pesaron tres cosas, en este orden:

1. **AC-3 · Comparabilidad.** F1 es la única frontera con significado idéntico en los cuatro
   transportes. F2 y F3 no tienen análogo en la variante D, que no hace llamadas al sistema ni
   abre conexiones: adoptarlas obligaría a que D midiera «otra cosa», y el estudio comparativo
   —que es la tesis del trabajo— se caería.
2. **AC-1 · Validez del atributo.** El atributo de calidad se define desde el punto de vista de
   quien lo sufre. Un consumidor no experimenta «el tiempo de la syscall»: experimenta el tiempo
   hasta tener la respuesta utilizable. Medir menos que eso es medir una abstracción interna.
3. **Honestidad del reporte (D5, D6).** F1 es la frontera más **desfavorable** entre las
   defendibles. Elegir deliberadamente la medida que nos perjudica es lo que da credibilidad a
   la afirmación de cumplimiento. Reportar 5 µs con F2 sería igualmente «cierto» y notablemente
   menos honesto.

**[REC]** La segunda ley del módulo —*el «por qué» importa más que el «cómo»*— se cumple aquí
literalmente: el valor del entregable no está en el número, está en poder explicar que se
eligió la frontera que produce el peor número y por qué.

## Ventajas

- Un solo reloj: elimina por completo el problema de sincronización entre procesos.
- Definición idéntica y verificable en las cuatro variantes y en cualquier lenguaje.
- Reproducible por un tercero: la frontera está escrita, no implícita en el código.
- Corresponde con lo que se presentaría a un cliente real como «latencia del servicio».

## Desventajas

- Incluye el sobrecoste del lenguaje del cliente. En Python son varios µs de intérprete que no
  son atribuibles al transporte, y penalizan comparativamente a las variantes escritas en
  lenguajes de alto nivel.
- Produce el número más alto de las opciones defendibles.
- No separa el coste de ida del de vuelta, ni el tiempo de servidor del de transporte.

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| El docente esperaba otra frontera | Media | Medio | Preguntarlo el 15/09. Los CSV crudos permiten recalcular; la frontera está documentada, no enterrada en el código |
| Una variante la implementa mal en silencio | Media | **Alto** — invalida la comparación | Bucle de medición copiado de `variante-B-tcp/client.py`, no reescrito. Revisión cruzada antes de la ronda final |
| El sobrecoste del lenguaje domina en variantes rápidas | **Alta** en la variante D | Medio | Medir el coste del bucle vacío (*overhead* del reloj) y reportarlo como piso de la medición |
| Comparar variantes en lenguajes distintos se lee como comparar lenguajes | Alta | Medio | Declararlo explícitamente en el informe: se compara **transporte + lenguaje**, no transporte puro |

## Consecuencias

**Queda habilitado**

- Implementar las cuatro variantes en paralelo sin coordinación adicional: la frontera es el
  contrato.
- Un único `analyze.py` sobre CSV homogéneos (AC-3).
- Afirmar cumplimiento o incumplimiento del objetivo de 1 ms sin ambigüedad.

**Queda bloqueado**

- Reportar cualquier cifra medida con otra frontera sin marcarla explícitamente como tal.
- Comparar los resultados de este estudio con *benchmarks* publicados de terceros: casi ninguno
  declara su frontera, y por eso casi ninguno es comparable. **Esa observación merece un párrafo
  en el informe.**

**Deuda aceptada**

- No se mide el desglose interno (tiempo de servidor vs. tiempo de transporte). Requeriría
  instrumentación adicional dentro del servidor, que alteraría la ruta caliente. Se acepta medir
  la caja negra.

**Revisar si**

- El docente indica el 15/09 que espera otra frontera → nuevo ADR que supersede a este.
- Se decide medir entre dos máquinas físicas → F1 sigue siendo válida, pero el informe debe
  separar latencia de red de latencia de proceso.
- El sobrecoste del reloj resulta ser una fracción significativa del p50 de la variante D →
  hay que reportar el piso de medición junto a cada cifra, no solo una vez.
