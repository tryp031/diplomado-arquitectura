# Changelog

Historial de cambios de la base compartida del diplomado (Group 2). Sigue, de forma simplificada,
[Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/): cada entrada dice **qué cambió y por qué**;
el detalle línea por línea está en `git log`.

- El proyecto no tiene versiones, así que las entradas se agrupan por **fecha**, de la más reciente a la más antigua.
- Cada entrada indica quién la hizo y, cuando se conoce, el PR.
- Categorías: **Añadido** · **Cambiado** · **Corregido** · **Eliminado**.
- Convención propuesta: la entrada se escribe **en el mismo PR**, bajo la fecha del día en que se abre. La fecha es la
  del PR, no la del merge; así no hace falta un segundo cambio después de integrarlo.

---

## 2026-09-23

Cierra los PR #7 y #8 (Camilo): quedaron atrapados por el rename de ADR-008 — tocaban
`sistema/variante-D-shm/` y citaban «variante D», y esos nombres ya no existen desde el #13.
Lo que sigue es la misma sustancia, reabierta en tres PR contra el árbol actual: #14
(Makefile), #15 (limpieza del front-end) y esta documentación. Detalle completo en
`Modulo 1/Ejercicios/Reto-Latencia-Minima/comunicaciones/MENSAJE-EQUIPO-23-09.md`.

### Corregido
- **`sistema/memoria-compartida-c/Makefile` y `sistema/control-dominio/Makefile`:** añaden
  `-D_GNU_SOURCE`. Sin él, bajo `-std=c11`, la biblioteca C deja sin declarar `clock_gettime`
  (que usa `reloj.h`), `ftruncate` y `usleep`, y ninguna de las dos carpetas compila en
  Linux/WSL2. Es el mismo arreglo que ya había aprobado @dmazo-koronet en el PR #7 (cerrado):
  el `git mv` del rename de ADR-008 partió de la copia sin el fix, así que el bug volvió con
  el nombre nuevo. Verificado con un clon limpio de `main`: sin este cambio, `memoria-compartida-c`
  y `control-dominio` no compilan en WSL2/Ubuntu; con él, compilan y el plano de control arranca
  y clasifica un estímulo suelto contra `memoria-compartida-c` (`LOCAL`, correcto).
  - De paso, `memoria-compartida-c/Makefile` declara ahora `../reloj.h` como dependencia de
    `server` y `client` — sin eso, editar el reloj compartido no disparaba recompilación
    (el otro punto pedido en el PR #7). Verificado: `touch reloj.h && make` ahora sí recompila
    los dos binarios; antes no recompilaba nada.
  - Revalidado con `python3 verificar.py` → «Todo en orden» (9/9). (Camilo, PR #14)
- **`app/index.html` y `app/servidor.py`:** retiran las citas a `ADR-001` y `ADR-006` del
  texto que se renderiza en pantalla (el recuadro de «la separación en dos planos» y el aviso
  de por qué `memoria-compartida-c` no admite clientes concurrentes). Son documentación interna
  del equipo, no parte de la entrega. Se conservan las citas a ADR en comentarios de código, que
  no se renderizan. (Camilo, PR #15)

### Añadido
- **`Modulo 1/Aportes/camilo/m1-arquitectura-memoria-compartida-c-camilo.html`:** arquitectura,
  justificación de las decisiones y criterios de cuándo usar memoria compartida. Reemplaza al
  documento de la PR #8 (cerrada): nomenclatura actual, sin sección de medición (se documenta
  arquitectura, no una corrida concreta) y sin citas a ADR en el cuerpo, mismo criterio que el
  front-end. (Camilo)
- **`Modulo 1/Aportes/camilo/m1-codigo-memoria-compartida-c-camilo.html`:** guía del código,
  archivo por archivo y bloque por bloque, incluido el modo de estímulo suelto `--clasificar`.
  Reemplaza al documento de la PR #8. (Camilo)
- **`Modulo 1/Aportes/camilo/m1-manual-instalacion-camilo.html`:** manual de instalación
  reescrito contra el árbol actual (nomenclatura de ADR-008, el fix de esta misma PR ya
  documentado como vigente). Reemplaza al documento de la PR #8. (Camilo)
- **`Modulo 1/Aportes/camilo/m1-manual-uso-camilo.html`:** manual de uso de la interfaz web,
  documento nuevo — la PR #8 nunca llegó a producir uno. Cubre el estado actual: sin editor de
  tabla (ADR-009/011), con estímulo suelto para `memoria-compartida-c`, sin columna de veredicto
  en el historial. (Camilo)
- **`Modulo 1/Aportes/camilo/FUENTES.md`:** fichas de los cuatro documentos anteriores. (Camilo)

---

## 2026-09-21

### Decidido
- **ADR-007 pasa a «Aceptada»** (Group 2). Se ratifican las dos preguntas que quedaban
  abiertas desde el 16/09: **no** se usan las cifras archivadas del control `Bc` y **no** se
  usa la línea base de internet (`E`). El alcance del reto queda definitivamente en B y D.
  - **Consecuencia inmediata:** la §3.4 del documento de arquitectura de Camilo (PR #8)
    sostiene la descomposición 9,2 % / 90,8 % sobre `Bc`. Con el ADR ratificado deja de ser
    una contradicción «a resolver en el consolidado» y pasa a ser **corrección obligatoria**
    antes de integrar ese PR.

### Cambiado
- **Presentación del reto reestructurada** (Daniel): de 13 láminas sin apéndice a **11 de
  línea principal, cronometradas en 4:50**, más **5 de apéndice técnico** que no se presentan
  y la lámina interna de estado. La narrativa pasa a ser problema → qué construimos →
  arquitectura → medición → resultados → optimización → trade-offs → cumplimiento →
  aprendizaje. Al apéndice bajan las colas, el suelo del instrumento, la justificación
  tecnológica, el C4 y los límites del experimento.
  - Lámina nueva **«Un portero con una lista»**: qué hace el sistema sin tecnicismos, para
    público no técnico.
  - **Rigor:** se retira de la tabla de trade-offs la afirmación «peor caso acotado por
    diseño: SÍ» para D. El experimento no la sostiene —su máximo fue 37 µs, 447× su mediana,
    impuesto por el planificador y el hardware—. Se sustituye por la variabilidad observada
    (máx/p50) y por «no se observaron muestras sobre 1 ms», que es lo que la evidencia dice.
  - Las once cifras del deck se contrastaron una por una contra `INFORME.md`.
  - Las referencias a láminas **por número** se sustituyen por referencias **por nombre**:
    reordenar el deck las dejaba apuntando a láminas equivocadas, que es justo lo que pasó.

### Añadido
- **Cuadernillo de repaso del Módulo 1** (Daniel · PR #9): la autoevaluación de 10 preguntas
  convertida en material de estudio, con la respuesta razonada de cada una.
- **Este CHANGELOG** (Camilo · PR #6) y su convención.
- **Presentación del reto** (Daniel): las dos gráficas SVG del informe, incrustadas sin
  modificar —percentiles en la lámina 7, histograma en la lámina 11—, y una **lámina 14 de
  reserva con la vista C4** (contexto y contenedores), que solo se presenta si la piden.
  La lámina corrige dos errores de `DISENO-ARQUITECTURA.md` §4.2: dibuja cuatro variantes
  cuando A y C nunca se implementaron (ADR-007), y dibuja D con «núcleo fijado» cuando el
  código no fija afinidad y en macOS/arm64 no podría.
- **`INDICE.html`:** acceso directo a la presentación desde «Empieza aquí». Va en
  `generar-indice.py`, no en el HTML generado, que se sobrescribe en cada regeneración.
  El generador admite ahora un título propio por destacado: el `<title>` de la presentación
  es «Reto de Latencia Mínima — Group 2», igual que el del informe, y desde el índice no se
  distinguían.

### Corregido
- **`INDICE.html` llevaba desde el 16/09 sin regenerar** (Daniel): el PR #9 añadió un
  documento y no ejecutó `generar-indice.py`. El índice decía 14 documentos y le faltaba la
  autoevaluación. Es el mismo punto de la checklist de `CONTRIBUIR.md` que se le exige a
  cualquier aporte.
- **Referencia colgante en la presentación** (Daniel): la lámina 4 remitía a «la lámina 7»
  para explicar cómo se separaron las causas del factor 162×. Esa lámina se eliminó el 17/09
  junto con `Bc`. Ahora dice lo que la 7 hace de verdad: **declarar la limitación**, no
  resolverla. El sello de estado pasa de «DRAFT · 16 SEP» a «DRAFT · 21 SEP».
- **`.gitattributes` no cubría `html` ni `md`** (Daniel). Medido el 21/09: `generar-indice.py`
  calcula el peso con `st_size // 1024`, así que con CRLF cada archivo pesa ~1 KB más y el
  índice generado en WSL2 difiere del generado en macOS **en los 39 tamaños**, sin que cambie
  ningún documento. Conflicto permanente y falso en cada PR. Se añade `text eol=lf` para
  `html` y `md`, con **excepción explícita del material recibido**: `**/Material-Clase/**` y
  los HTML del Módulo 0, que vienen de Brightspace con BOM y CRLF y se conservan byte a byte.

### Revisado
- **PR #6 aprobado.** El historial del 15 al 17/09 se contrastó contra `git log`: los PR #1 a
  #5 mapean uno a uno con sus commits y la entrada del 17/09 describe exactamente los 26
  archivos que toca `8c0b035`.
- **PR #7, cambios pedidos.** Verificado en el equipo de referencia que `-D_GNU_SOURCE` **no
  altera el binario en macOS**: mismo ensamblador y objetos idénticos byte a byte con y sin el
  flag, así que no hay que volver a medir. Se pide extender el arreglo a
  `sistema/control-dominio/`, que incluye `reloj.h` y falla igual en Linux, y declarar
  `../reloj.h` como dependencia del `Makefile` de D —hoy editar el reloj compartido no
  dispara recompilación—.
- **PR #8, cambios pedidos.** La ficha de fuentes y las siete contradicciones declaradas se
  comprobaron y son reales. Se pide fechar §3.4 y decir que el control `Bc` lo retiró el
  ADR-007: el documento presenta la descomposición 9,2 % / 90,8 % como dato medido vigente,
  y el README y el `INFORME.md` declaran lo contrario.

---

## 2026-09-17

### Cambiado
- **Vuelve a medir el reto** (Daniel · PR #5): B y D, 3 rondas × 1 M. Toda la documentación pasa a salir de esa
  corrida, con su CSV y su log. Las cifras anteriores (10/09) no las respaldaba ningún CSV ni log versionado.
  - Hallazgo: B superó 1 ms en 136 de 3 M de muestras el 17/09 y en 0 el 14/09, con el mismo código y la misma
    máquina; D dio 0 en las dos. El cumplimiento de B depende del estado del sistema operativo.
  - El informe ahora **declara** que el factor de 162× entre B y D mezcla transporte y lenguaje.
  - Sincronizados con las cifras nuevas: `INFORME.md`, `GUION-VIDEO.md`, la presentación (láminas 7 a 14), los README
    del proyecto y de la variante D, el de `control-dominio`, `DISENO-ARQUITECTURA.md`, y una enmienda en ADR-002 y
    ADR-004 (los ADR no se reescriben, se enmiendan).

### Añadido
- Al informe: el clasificador cuesta 1,9 ns (0,014 % del RTT de B) y no hay canal lateral temporal entre veredictos.
  Era material ya medido que no se había recogido.

### Corregido
- `graficas.py` incluía la ronda 9 (una prueba de 20 000 iteraciones): las figuras decían n = 3 020 000 y la tabla
  del informe 3 000 000. Ahora filtra por ronda y lee la columna por nombre.
- `.gitignore` excluía los CSV solo un nivel por debajo de `resultados/`; al archivar la corrida anterior quedaron
  68 MB fuera de la regla. Los `.log` archivados sí se versionan: son la evidencia del 14/09 que cita el informe.

---

## 2026-09-16

### Eliminado
- **Alcance reducido a las variantes B y D** (Daniel · PR #1, ADR-007). Se retiran del árbol `variante-A-http/` y
  `variante-C-ipc/` (solo un `TODO.md`, cero mediciones), `control-Bc-tcp-c/` y `variante-E-icmp/`, más los 18
  archivos de resultados de Bc y E que quedaban sin código que los reprodujera. Sus hallazgos pasan a
  `docs/archivo/`; el código se recupera del historial de git. La descomposición 9 % lenguaje / 91 % transporte
  sigue siendo cierta pero deja de ser reproducible desde el árbol.
- Peso muerto: un `.zip` regenerable y un PDF generado (32,5 MB), tres documentos duplicados y siete binarios
  compilados que estaban versionados por error.
- **ADR duplicados** (Daniel · PR #4): las cuatro copias de los ADR 001 a 004 en `_Base-Conocimiento/ADR/`, que ya
  habían divergido de los originales (los 005 a 007 nunca se copiaron). Se conserva `ADR-000-plantilla.md`.

### Corregido
- **`analyze.py` devolvía ceros sin avisar** (Daniel · PR #1). Leía la latencia de la **última** columna; cuando la
  concurrencia añadió la columna `hilo` (15/09), esa pasó a valer 0. El análisis salía con p50, máximo y percentiles
  en cero, sin ningún error, y decía «p99.9 < 1 ms: SÍ» sobre datos inexistentes. Invalidaba cualquier medición tomada
  desde el 15/09. Ahora localiza la columna por nombre y se detiene si no reconoce el formato.
- `.gitignore` apuntaba a `harness/`, carpeta renombrada a `sistema/`: la regla nunca se activó.
- Ocho enlaces rotos a `_Base-Conocimiento/ADR/`, reapuntados al `docs/ADR/` del proyecto. `INFORME.md` listaba a
  un integrante que ya no estaba en el equipo.

### Cambiado
- **CSV del plano de control rediseñado para Excel** (Daniel · PR #1): de 17 columnas a 11, con la unidad en el
  nombre de la columna y las horas como texto para que Excel no las reformatee. Se quita el botón NDJSON.
- `CONTRIBUIR.md` y los índices distinguen decisión de ejercicio (`docs/ADR/` del ejercicio) de decisión
  transversal (`_Base-Conocimiento/ADR/`) (Daniel · PR #4).

### Añadido
- **Draft de la presentación del reto** (Daniel · PR #2): 13 láminas más una interna. Es un borrador sin revisar por
  Freddy ni Camilo, con decisiones abiertas para la reunión del 21/09.
- **Documento de avance del 16/09** para el equipo (Daniel · PR #3), con el aviso del fallo de `analyze.py` y lo que
  hay que resolver el 21/09: ratificar o revertir el ADR-007, repartir los tres manuales y decidir qué corrida es la
  oficial.
- `_Base-Conocimiento/ADR/LEEME.md`: la regla «un ADR viaja con lo que documenta». `generar-indice.py` recoge los ADR
  de ambos sitios sin duplicar archivos (Daniel · PR #4).

---

## 2026-09-15

Commits directos a `main`, anteriores a la regla de ramas y PR.

### Añadido
- **Commit inicial: base compartida del diplomado** (Daniel): contrato operativo (`CLAUDE.md`, `PROMPT-MAESTRO.md`,
  `CONTRIBUIR.md`), `_Base-Conocimiento/`, `_Plantillas/`, Módulos 0 y 1 con el flujo
  Material-Clase → Aportes → Consolidado → Entregables, y el Reto de Latencia Mínima (código, harness y plano de
  control web). No se versionan los CSV crudos de medición (~108 MB, regenerables con `./run.sh`).
- **README raíz, «Obtener el proyecto»** (Daniel): requisitos por sistema operativo, `git clone`, la ruta al reto entre
  comillas porque tiene espacios, y que Windows nativo ve y demuestra el sistema pero no mide (ADR-005).
- **`.gitattributes`** (Daniel): fuerza LF en `sh`, `py`, `c` y `h`, y CRLF en `cmd` y `ps1`, para evitar
  «bad interpreter: /bin/bash^M» bajo WSL2.
- **Flujo de ramas y PR como regla del equipo** (Daniel): `CONTRIBUIR.md` (sección 2),
  `.github/pull_request_template.md` y `.github/CODEOWNERS` (faltan los usuarios de GitHub de Camilo y Freddy).
  Aún no se impone técnicamente: es disciplina, no un candado.
- **Sección «Trabajar con IA» en el README** (Daniel): qué skill compartida invocar en cada caso.
