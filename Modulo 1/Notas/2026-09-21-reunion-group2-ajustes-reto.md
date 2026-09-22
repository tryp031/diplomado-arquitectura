# Reunión Group 2 — 21/09/2026 · ajustes al Reto de Latencia Mínima

| Campo | Valor |
|---|---|
| Tipo | `notas-reunion` — **no** es material oficial ni consolidado |
| Fuente | notas crudas dictadas por Danny tras la reunión del 21/09/2026 + imagen de anotaciones sobre el CSV exportado |
| Transcribe y ordena | Danny (con Claude) · 21/09/2026 |
| Estado | **backlog acordado, sin ejecutar** — se trabaja el 22/09/2026 |
| Alcance | `Modulo 1/Ejercicios/Reto-Latencia-Minima/reto-latencia-group2/` |
| Entrega que condiciona | Reto de Latencia Mínima · cierre **29/09/2026** |

**Cómo leer este documento.** Cada punto trae la **nota literal** tal como salió de la
reunión y, debajo, la **lectura técnica**: qué archivos toca, qué se rompe, qué hay que
decidir antes. La lectura técnica es aporte de Danny/Claude, no acuerdo de la reunión: lo
acordado es únicamente la nota literal. Donde caben dos interpretaciones, están las dos y
**no se elige por cuenta propia**.

---

## Resumen: 13 notas en 4 bloques

```text
BLOQUE A · Nomenclatura          notas 1, 9, 6         cambia cómo se llama todo
BLOQUE B · Plano de control      notas 2, 3, 4, 5      cambia lo que ve el evaluador
BLOQUE C · Estructura del repo   notas 7, 8, 11        cambia qué se entrega
BLOQUE D · Documentación         notas 10, 12, 13      cambia qué se explica
```

Cuatro de las trece **no son trabajo mecánico**: tocan decisiones ya registradas en un ADR
y no se pueden hacer en silencio. Van marcadas ⚠ y se resumen al final.

---

## BLOQUE A · Nomenclatura

### Nota 1 — quitar la palabra «variante»

> *«Renombrar palabra variante y que quede solamente TCP Python y solamente Memoria
> compartida C.»*

**Lectura.** Hoy conviven dos cosas con el mismo nombre. Separarlas antes de tocar nada:

| | Qué es | Dónde vive | ¿Se renombra libre? |
|---|---|---|---|
| **Rótulo visible** | «B · TCP crudo (Python)» | UI, presentación, PDF | **Sí** — es solo texto |
| **Identificador de datos** | `B`, `D` | `resultados-B-1.csv`, `ejecucion-D-3.log`, `run.sh <VARIANTE>`, `analyze.py` | **No sin decidir qué pasa con la evidencia** |

La corrida oficial del 17/09 está archivada como `resultados-B-*.csv` / `resultados-D-*.csv`
y la presentación cita esas cifras. Si cambia el identificador, o se renombra la evidencia
—y deja de coincidir con lo ya citado— o queda un CSV llamado `B` para un sistema que ya
nadie llama `B`.

**Recomendación (Danny/Claude, no acordada):** cambiar el rótulo en toda la superficie
visible y **conservar `B`/`D` como identificador interno de los archivos de datos**, con
una línea en el README que fije la equivalencia. Eso es un día de trabajo; lo otro obliga a
tocar evidencia ya medida.

**Archivos del rótulo visible:** `app/servidor.py` (dict `VARIANTES`, campo `nombre`),
`app/index.html`, `sistema/README.md`, `README.md`.

---

### Nota 9 — renombrar las carpetas de variante

> *«Renombrar las carpetas variante-d-.. y variante-b-... por los nuevos nombres
> definidos.»*

**Lectura.** Mecánico, con más referencias de las que parece. `variante-B-tcp` y
`variante-D-shm` están citadas desde:

```text
doctor.py                        sistema/run.sh
README.md                        sistema/README.md
app/servidor.py  (campo "dir")   sistema/demo.py
docs/ADR/ADR-001, ADR-007        docs/archivo/*.md
```

Los ADR **no se editan para que cuadren**: un ADR registra lo que se decidió cuando se
decidió. Si las carpetas se renombran va una nota de enmienda, no un buscar-y-reemplazar
sobre el ADR.

**Depende de la nota 1.** No se renombra hasta que el nombre esté acordado.

---

### Nota 6 — ajustar textos

> *«Ajustar textos necesarios.»*

**Lectura.** Es el barrido final del bloque A, no una tarea propia. **Se hace al final**,
con 1, 2, 3, 4, 5 y 9 ya cerradas; antes hay que rehacerlo.

---

## BLOQUE B · Plano de control (lo que ve el evaluador)

### Nota 2 — quitar listas blancas y negras de la interfaz ⚠

> *«Remover la sección de listas blancas y negras, solo dejar un dropdown con las ips de
> ejemplo sin clasificar.»*

**Lectura — dos interpretaciones muy distintas:**

1. **Quitar el *editor* de listas de la UI** y dejar el dropdown de hosts.
   `sistema/tabla-hosts.csv` sigue siendo la fuente del dominio y el clasificador sigue
   clasificando. → **Simplificación sana.** El plano de control es *editor de las filas*,
   no autor del dominio; dejar de ser editor no le quita nada al experimento.
2. **Quitar el dominio de listas** y volver a un dropdown de IPs sin semántica. → Esto
   **deshace ADR-004** y revierte el sistema a eco puro. Todo lo medido el 17/09 mide un
   clasificador.

La nota dice *«sin clasificar»*, que se lee como (2), pero el resto de las notas asume que
el sistema sigue clasificando. **Confirmar mañana antes de tocar código.** Si es (2): ADR
nuevo y volver a medir.

---

### Nota 3 — que «Probar clasificación» funcione con memoria compartida ⚠

> *«Probar clasificación no muestra la variante de memoria compartida, ponerla a
> funcionar.»*

**Lectura. No es un bug: es una exclusión deliberada.** En `app/servidor.py` la variante D
está marcada `socket: False`, y el propio código explica por qué:

> «D no tiene conexiones que aceptar: cliente y servidor comparten UNA región de memoria
> con una sola ranura por sentido. Dos clientes se pisarían el payload y podrían leer la
> respuesta del otro.»

Es decir: **los 83 ns se pagan con exclusividad.** Para que el formulario le hable a D, el
plano de control deja de hablar TCP y se vuelve cliente de memoria compartida. Dos caminos,
no equivalentes:

| Camino | Cómo | Costo | Riesgo |
|---|---|---|---|
| **(a) Lanzar `./client` una vez por estímulo** | el plano de control ejecuta el cliente en C como subproceso | arranque de proceso (ms) — latencia *del plano de control*, que la UI ya reporta aparte | bajo · **recomendado** |
| **(b) Cliente shm residente** | el plano de control mantiene la ranura tomada | ninguno aparente | **alto** — ocupa la única ranura; si corre el medidor a la vez se pisan y la medición queda sucia sin avisar |

**Recomendación:** (a), **bloqueada mientras haya una corrida en curso**. Aun así toca
ADR-002, así que va nota de enmienda. Con (b) se puede corromper una medición sin que nadie
lo note hasta la sustentación.

---

### Nota 4 — mejorar el CSV exportado ✅ desbloqueada por la imagen

> *«Mejorar CVS con las observaciones de la siguiente imagen.»*

**De qué CSV se trata.** No es `tabla-hosts.csv` ni los `resultados-*.csv` del informe: es
el **CSV que descarga el plano de control desde el historial**, generado en
`app/index.html` (preámbulo ~líneas 605-625, lista de columnas ~565-585).

**Cabecera actual y anotaciones de la imagen:**

```text
n, fecha, hora_inicio, hora_fin, variante, sistema_us, web_ms, host, ip, veredicto, resultado, detalle
                                    ▲          └── «nuevo orden» ──┘        └──── quitar las tres ────┘
                                    └── «cambiar B o D por el nombre correspondiente»
```

| # | Cambio pedido | Dónde |
|---|---|---|
| 4.1 | Columna `variante`: escribir el nombre, no `B`/`D` | lista de columnas del export |
| 4.2 | `sistema_us` y `web_ms`: **nuevo orden** | ídem |
| 4.3 | Quitar las columnas `veredicto`, `resultado`, `detalle` | ídem |
| 4.4 | Quitar del preámbulo las líneas de leyenda `veredicto` y `detalle` | bloque `COLUMNAS` |

**Lo que se queda tal cual** (no está marcado y conviene que siga): el bloque `UNIDADES`,
la línea «`sistema_us` — lo que tarda el SISTEMA, frontera F1, es la ÚNICA medición del
reto», la referencia «el objetivo del enunciado es 1 ms = 1000 us» y el aviso de decimales
con punto. Ese preámbulo es lo que evita que alguien lea `web_ms` como si fuera el
resultado del reto.

**Ambigüedad a resolver (4.2).** «Nuevo orden» está escrito sobre las dos columnas pero no
dice *cuál* orden. Las dos lecturas posibles: intercambiar `sistema_us` ↔ `web_ms`, o
moverlas ambas a otra posición de la fila. **Preguntar mañana y anotar el orden exacto.**

**⚠ Observación crítica — 4.3 no es cosmética.** Sumada a las notas 2 y 5, hay **tres
eliminaciones que convergen en lo mismo**:

```text
nota 2  →  quita las listas blanca/negra de la pantalla
nota 5  →  quita la columna VEREDICTO de la grilla del historial
nota 4  →  quita veredicto, resultado y detalle del CSV exportado
────────────────────────────────────────────────────────────────
resultado: no queda ni un artefacto donde se vea que el sistema clasifica
```

El reto dejó de ser eco puro el 14/09 precisamente para tener algo que demostrar. Si el
evaluador abre la pantalla, la grilla y el CSV, en los tres ve un eco con un tiempo.

Y hay un segundo efecto, más silencioso: quitar `resultado` **y** `detalle` deja el CSV sin
manera de distinguir una fila correcta de una fila con error. Hoy una fila fallida se
reconoce porque `resultado` dice `ERROR` y `detalle` explica; sin esas dos columnas, un
error queda como una fila normal con los números vacíos. **Si se quitan igual, que sea una
decisión tomada a la vista de esto, no un efecto lateral.**

---

### Nota 5 — ajustar la grilla del historial

> *«Ajustar la grid de historial: remover el veredicto: VEREDICTO, y el VAR poner el
> nombre concreto de la variante usada TCP Python o Memoria compartida C.»*

**Lectura.** La segunda mitad es clara y mecánica: la columna `VAR` muestra hoy `B`/`D` y
debe mostrar el nombre. Está en `app/index.html`, tabla `.history`.

La primera mitad es ambigua — confirmar cuál:

- ¿quitar **la columna** VEREDICTO (`LOCAL` / `EXTERNO` / `DESCONOCIDO`)?
- ¿o quitar solo **el rótulo duplicado**, conservando el dato?

**Decidir junto con las notas 2 y 4**, por lo dicho arriba. Son la misma decisión repartida
en tres lugares.

---

## BLOQUE C · Estructura del repositorio y del entregable

### Nota 7 — mover la carpeta `graficas`

> *«En el proyecto tenemos una carpeta llamada graficas, ¿este lo podemos cambiar de lugar?
> Esto no haría parte del proyecto entregable, dentro de docs.»*

**Lectura.** Son dos cosas de nombre parecido y solo una se mueve:

```text
sistema/graficas/      histograma.svg, percentiles.svg   SALIDA  → se mueve
sistema/graficas.py    el script que las genera          CÓDIGO  → se queda
```

Los SVG son producto del análisis, no parte del sistema. Al moverlos hay que actualizar la
ruta de salida en `sistema/graficas.py` y las menciones en `sistema/README.md` y
`app/servidor.py`.

---

### Nota 8 — sacar `docs/` fuera del proyecto ⚠

> *«Quitar la carpeta docs del proyecto y ponerla por fuera del reto-latencia-grupo2.»*

**Lectura. El objetivo es correcto; la ejecución literal rompe algo.** El enunciado pide
como entregable 1 un **ZIP con el código fuente**: los ADR y el enunciado no van ahí.

El problema, medido: **el código fuente cita los ADR por ruta.**

```text
sistema/reloj.h                  4 menciones a ADR-0xx
sistema/clasificador.h           4
sistema/variante-D-shm/server.c  4
verificar.py                     8
sistema/analyze.py               imprime "Ver docs/ADR/ADR-005" al negarse a mezclar plataformas
```

más los enlaces relativos de `README.md`, `sistema/README.md` y
`sistema/variante-D-shm/README.md` (`../docs/ADR/...`). Si `docs/` sale, el ZIP entregado
queda lleno de punteros hacia documentos que el evaluador no recibió.

**Recomendación:** separar **dónde vive** de **qué se empaqueta**. `docs/` se queda en el
repositorio —es la justificación que alimenta el PDF del entregable 2— y lo que se crea es
una **regla de empaquetado** que excluya `docs/`, `resultados/` y `graficas/`. Un
`hacer-zip.sh` de diez líneas cumple la nota sin romper una sola referencia. Si aun así se
decide mover la carpeta, hay que reescribir los punteros del código, y eso ya no es mover
una carpeta.

---

### Nota 11 — revisar `resultados` ⚠

> *«Revisar archivo resultados y pulirlo o removerlo, validarlo.»*

**Estado real hoy:**

| Contenido | Qué es |
|---|---|
| `resultados-B-1/2/3.csv` + `.log` (17/09) | **corrida oficial del informe** |
| `resultados-D-1/2/3.csv` + `.log` (17/09) | **corrida oficial del informe** |
| `resultados-B-0.csv` (08/09), `-9` (14/09) | corridas viejas |
| `resultados/archivo/` — 12 archivos (14/09) | lo que `run.sh` archivó automáticamente |
| Peso total | ~**150 MB** |

**Invariante en juego:** nunca se borra ni se sobrescribe un CSV de `resultados/` — es la
evidencia del informe, y el `.log` hermano es lo único que dice en qué máquina se tomó la
corrida (ADR-005). «Removerlo» choca de frente con eso.

**Recomendación:** no borrar nada. Lo que la nota pide de verdad es **que no viajen 150 MB
en el ZIP**, y eso lo resuelve la regla de empaquetado de la nota 8. Aparte sí vale
**rotular** cuál es la corrida oficial (17/09) y cuáles son histórico, para que nadie cite
la equivocada.

---

## BLOQUE D · Documentación

### Nota 10 — README por variante, sin las descartadas

> *«Readme de cada variante, no realice variantes descartadas.»*

| Carpeta | README |
|---|---|
| `sistema/variante-D-shm/` | ✅ existe |
| `sistema/control-dominio/` | ✅ existe |
| `sistema/variante-B-tcp/` | ❌ **falta** |

Trabajo real: **escribir el README de B**, al mismo nivel que el de D. Y no escribir README
para lo descartado por ADR-007 (`A`, `C`, `Bc`, `E`): eso ya vive, y bien, en
`docs/archivo/`.

---

### Nota 12 — logs `.txt` o `.log` ✅ ya cumple

> *«Revisar logs, piden .txt o .log, revisar notas del reto.»*

**Verificado contra el enunciado** (`docs/ENUNCIADO.md`, entregable 3):

> «**Logs de ejecución** — `.txt` / `.log` o capturas `.png` / `.jpg` con los registros del
> tiempo transcurrido entre envío del estímulo y recepción de la respuesta.»

Lo que hay son `ejecucion-B-*.log` / `ejecucion-D-*.log`: **formato correcto, requisito
cumplido.** No hay que convertir nada. Pendiente único: **elegir cuáles se entregan** — la
recomendación son los seis del 17/09, que son la corrida oficial.

---

### Nota 13 — explicar el código fuente

> *«Fuentes del servidor, cómo funciona cada sistema, cómo funciona el servidor, medidor,
> explicar código fuente. Notas para conocer cómo funciona el sistema.»*

**Lectura.** Esto **es** el entregable 2 del enunciado (documentación técnica en PDF:
arquitectura + justificación + cómo se mide). No se arranca de cero; ya existen:

```text
docs/DISENO-ARQUITECTURA.md
docs/ESPEC-MEDICION.md
sistema/README.md          (contrato de variante)
```

**Primer paso mañana: leer esos tres y ver qué falta**, no redactar de nuevo. Lo que con
seguridad falta es el recorrido del código archivo por archivo (`reloj.h`,
`clasificador.h/.py`, `server.c`, `client.c`, `run.sh`, `analyze.py`) y el papel de
`verificar.py`, que no es un test sino el contrato del experimento.

---

## ⚠ Las cuatro que no son trabajo mecánico

Cada una toca una decisión registrada. Cambiar una decisión registrada **exige un ADR o una
enmienda**, escrita el mismo día: es barata hoy y cara de reconstruir en noviembre.

| Nota | Decisión que toca | Qué hay que producir |
|---|---|---|
| **2** (quitar listas) | ADR-004 — dominio de listas de hosts | si es la lectura (2): ADR nuevo **y volver a medir** |
| **3** (D en el formulario) | ADR-002 — D es memoria compartida sin sockets | enmienda a ADR-002 con el camino elegido |
| **4 + 5** (quitar veredicto del CSV y de la grilla) | ADR-004 — lo que el sistema demuestra | decisión escrita: qué prueba la demo si la clasificación no se ve |
| **8 + 11** (sacar docs, tocar resultados) | ADR-005 — trazabilidad de la evidencia | regla de empaquetado; **no borrar evidencia** |

---

## Orden propuesto para el 22/09

Primero lo que desbloquea, después lo mecánico, y `verificar.py` al cierre.

```text
1.  DECIDIR (20 min, los tres)   notas 2, 3, 4.2, 5 y 8 · sin esto lo demás se rehace
2.  Acordar el nombre            nota 1 · rótulo visible vs identificador de datos
3.  Ejecutar nomenclatura        notas 1 → 9
4.  Ejecutar interfaz            notas 2 → 3 → 5 → 4
5.  Ejecutar estructura          notas 7 → 8 → 11 (regla de empaquetado)
6.  Documentación                notas 10 → 13   (12 solo confirmar)
7.  Barrido de textos            nota 6
8.  python3 verificar.py         ← obligatorio antes de dar nada por cerrado
```

`verificar.py` no comprueba que el código funcione: comprueba que el experimento siga
midiendo lo que dice medir. Si falla, su salida dice qué conclusión del informe deja de
sostenerse y en qué ADR está la decisión.

---

## Pendientes que no salieron de la reunión

- **El orden exacto de la nota 4.2** — la imagen dice «nuevo orden» pero no cuál.
- **Asignación:** las notas no dicen quién hace qué. Repartir entre Freddy, Camilo y Danny
  al abrir la sesión del 22/09.
- **Fecha:** el reto cierra el **29/09/2026**; después de la fecha de cierre no se califica.
  Quedan 7 días para todo esto más el video o la demo en vivo.
- **Trazabilidad:** lo que cada quien produzca va firmado en `Aportes/<autor>/`, nadie edita
  el aporte firmado por otro, y las contradicciones se resuelven en el consolidado
  registrando cuál se adoptó y por qué (`CONTRIBUIR.md`).
