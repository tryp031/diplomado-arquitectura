# ADR-008 — Nomenclatura: de «variantes B y D» a «TCP Python» y «Memoria compartida C»

- **Estado:** **Aceptada** el 2026-09-22. Acordada por Group 2 en la reunión del 21/09/2026
  (notas 1 y 9 del backlog) y ejecutada el 22/09.
- **Fecha:** 2026-09-22
- **Decide:** Group 2 — Freddy Aparicio · Camilo Céspedes · Daniel Mazo. Ejecuta Daniel Mazo.
- **Origen:** reunión del 21/09/2026 —
  `Modulo 1/Notas/2026-09-21-reunion-group2-ajustes-reto.md`, notas 1 y 9
- **Supersede parcialmente:** [ADR-007](ADR-007-reduccion-de-alcance.md) §Decisión, en lo
  relativo a los nombres de carpeta `sistema/variante-B-tcp/` y `sistema/variante-D-shm/`
- **No afecta:** [ADR-001](ADR-001-frontera-de-medicion.md) (frontera F1) ·
  [ADR-003](ADR-003-resolucion-del-reloj.md) (reloj) ·
  [ADR-004](ADR-004-dominio-listas-de-hosts.md) (dominio y payload) ·
  [ADR-005](ADR-005-comparabilidad-entre-maquinas.md) (comparabilidad).
  **Ningún dato medido cambió**: los CSV y los `.log` son los mismos bytes con otro nombre.

---

## Contexto

Hasta el 21/09 el proyecto arrastraba el vocabulario de cuando había **seis** puntos de
medición (A, B, C, D, Bc, E). ADR-007 redujo el alcance a dos, pero el nombre siguió
siendo el de un catálogo: «variante B», «variante D».

Eso dejó dos problemas distintos conviviendo bajo la misma palabra:

| | Qué es | Dónde vive |
|---|---|---|
| **Rótulo visible** | «B · TCP crudo (Python)» | UI, presentación, PDF |
| **Identificador de datos** | `B`, `D` | `resultados-B-1.csv`, `ejecucion-D-3.log`, `run.sh B 1` |

Y un problema de comunicación: ante un evaluador, «variante B» no dice nada. «TCP Python»
dice exactamente qué es.

## Problema

Renombrar el rótulo es texto. Renombrar el identificador toca la **evidencia del informe**,
que es justamente lo que ADR-005 protege. Había que decidir hasta dónde llega el cambio.

## Opciones consideradas

### Opción A — renombrar solo el rótulo visible, conservar `B`/`D` como ID de datos
Cero riesgo sobre la evidencia; los archivos del 17/09 quedan intactos. A cambio, el
proyecto sigue teniendo dos vocabularios y una línea de equivalencia en el README que
alguien tiene que leer.

### Opción B — renombrar también carpetas y archivos de datos
Un solo vocabulario en todo el árbol. Cuesta renombrar 30 archivos de evidencia, ajustar
los parsers que derivan la variante del nombre del archivo y revisar las cifras ya citadas.

### Opción C — no renombrar
Descartada en la reunión: el nombre es parte de lo que se entrega.

## Decisión

**Se adopta la opción B**, acordada por los tres integrantes.

```text
B  →  TCP Python            carpeta: sistema/tcp-python/
D  →  Memoria compartida C  carpeta: sistema/memoria-compartida-c/
```

Alcance ejecutado el 22/09:

- Carpetas `sistema/variante-B-tcp/` y `sistema/variante-D-shm/` renombradas (`git mv`).
- 30 archivos de evidencia renombrados: 15 CSV + 9 `.log` vigentes y 6 pares archivados.
  **Ningún archivo se borró, se sobrescribió ni cambió de contenido.**
- `run.sh` ahora se invoca `./run.sh tcp-python 1` / `./run.sh memoria-compartida-c 1`.
- Claves de `VARIANTES` en `app/servidor.py`, `doctor.py`, `graficas.py` y
  `visor/generar-datos.py` alineadas con los nombres nuevos.
- **La palabra «variante» se conserva.** La nota pedía cambiar «variante B» por «TCP
  Python», es decir sustituir el **identificador**, no el sustantivo. En un primer intento
  se reemplazó además «variante» por «sistema» en toda la interfaz; eso no lo pedía nadie
  y se revirtió el mismo día. «Variante» es cada implementación; «sistema» es lo que el
  reto mide. No son sinónimos y mezclarlos confunde los dos planos.

**Lo que NO cambia, deliberadamente:** el campo `variante` del JSON interno y de la columna
del CSV exportado. La nota 4.1 del backlog pide que esa columna **escriba el nombre**, lo
que presupone que la columna sigue llamándose así. Renombrar la columna además del
contenido rompería a quien ya tenga exportaciones previas sin ganar nada.

## Justificación

El renombrado de la evidencia es seguro **porque el CSV y su `.log` se renombraron en
pareja**. ADR-005 exige que toda corrida tenga su log con la plataforma; la comprobación 8
de `verificar.py` lo valida y sigue encontrando los 9 pares.

## Riesgos

| Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|
| Un parser derive mal la variante del nombre nuevo | **Alta** | **Alto** — figuras vacías sin error | Detectado y corregido: ver abajo |
| Presentación e informe citen «variante B» | Alta | Medio | Barrido pendiente — no está hecho en este ADR |
| Alguien mezcle una copia vieja de los CSV con los nuevos | Baja | Alto | Los CSV **no están versionados**: solo existen en la máquina que midió |

**El riesgo 1 se materializó y se corrigió en el mismo cambio.** `graficas.py` extraía la
variante con `resultados-([A-Za-z]+)-(\d+)\.csv$`. Ese `[A-Za-z]+` no acepta guiones: con
`resultados-tcp-python-1.csv` el match falla, el archivo se ignora y **las figuras salen
vacías sin lanzar un solo error**. Es exactamente el modo de fallo del bug del 16/09.

El patrón nuevo es `resultados-([A-Za-z][A-Za-z0-9-]*)-(\d)\.csv$`: la ronda es **un solo
dígito**, lo que además mantiene excluidos los archivados del tipo
`resultados-tcp-python-1--20260914-122152.csv`, que con un `(\d+)` codicioso habrían
empezado a colarse en las figuras del informe.

## Consecuencias

- Los comandos de la memoria del proyecto y de cualquier documento anterior al 22/09
  (`./run.sh B 1`) **ya no funcionan**. El nombre nuevo es el único válido.
- Los ADR-001 a 007 **no se editaron**: siguen diciendo «variante B» y «variante D», y es
  correcto *en su fecha*. Este documento es el que dice qué cambió después.
- Queda pendiente el barrido de la presentación y el informe, que citan los nombres viejos.

### Acciones derivadas

- [ ] Barrer «variante B/D» en la presentación y en `docs/DISENO-ARQUITECTURA.md`
      (nota 6 del backlog, barrido final).
- [ ] Freddy y Camilo: usar los nombres nuevos en los manuales técnicos.
- [x] `python3 verificar.py` en verde tras el cambio (9/9).

---

> **Nota de método.** Renombrar evidencia ya medida es la clase de cambio que parece
> cosmético y no lo es. Se hizo con `git mv` donde había historial, en pareja CSV+log, y
> sin tocar un solo byte de contenido. Si alguna cifra del informe dejara de cuadrar, la
> causa **no** está aquí: está en quién la citó.
