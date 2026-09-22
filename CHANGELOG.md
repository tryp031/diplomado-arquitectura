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

## 2026-09-21

### Añadido
- **README general:** pasos para ejecutar todo el sistema en Windows con WSL2
  (`wsl -l -v`, `sudo apt update && sudo apt install -y build-essential make`, `./iniciar.sh`). (Camilo)
- **README de la variante D:** secciones «Otras plataformas» y «Límites conocidos». La primera documenta una
  corrida de D en Linux x86-64 sobre WSL2 (20/09, 3 × 1 M, 0 muestras sobre 1 ms); es una corrida propia y no
  se mezcla con la del equipo de referencia (ADR-005). (Camilo)

### Cambiado
- **README general, «Arrancar»:** distingue Windows nativo (interfaz y variantes en Python) de WSL2 (todo el
  sistema) y aclara que `iniciar.cmd` **no** arranca la variante D. (Camilo)
- **README de la variante D:** tabla de archivos actualizada (`server.c` clasifica, `common.h` ya no contiene el
  reloj, se listan `clasificador.h` y `reloj.h`), y la granularidad del reloj se presenta como dependiente de la
  plataforma. (Camilo)
- **`sistema/variante-D-shm/Makefile`:** añade `-D_GNU_SOURCE`. Es necesario para compilar en Linux/WSL2: sin él
  falla (`clock_gettime`, `ftruncate` y `usleep` quedan sin declarar bajo `-std=c11`). El README de D ya lo
  documenta, así que entran juntos. (Camilo)

### Corregido
- **`sistema/control-dominio/Makefile`** (revisión de @dmazo-koronet, PR #7): mismo fallo que el de D — sin
  `-D_GNU_SOURCE` no compila en Linux/WSL2 (`clock_gettime`, que usa `reloj.h`, queda sin declarar bajo
  `-std=c11`). `iniciar.sh` lo silenciaba (`make ... || true`) en vez de fallar visiblemente. Verificado:
  compila limpio en WSL2/Ubuntu tras el cambio. (Camilo)
- **`sistema/variante-D-shm/Makefile`:** `server` y `client` no declaraban `../reloj.h` como dependencia, aunque
  `common.h` lo incluye — editar el reloj compartido (el instrumento común de ADR-003) no disparaba
  recompilación, y un binario desactualizado habría dado números que ya no significan lo que dicen, sin ningún
  error visible. Verificado en WSL2: antes de este cambio, tocar `reloj.h` y volver a hacer `make` no
  recompilaba nada; después, recompila los dos binarios. (Camilo)

### Detectado, sin corregir
- `reloj_verificar()` (`reloj.h`) no se invoca y el cliente de D imprime siempre «granularidad ~41.67 ns»; el ADR-003
  pide verificar y reportar la granularidad real. (Camilo)
- `analyze.py` (`plataforma_de`) identifica una plataforma Linux por la línea «Architecture» de `lscpu`, no por el
  modelo de CPU: dos equipos Linux distintos tendrían la misma identidad y el ADR-005 no los distinguiría. (Camilo)

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
