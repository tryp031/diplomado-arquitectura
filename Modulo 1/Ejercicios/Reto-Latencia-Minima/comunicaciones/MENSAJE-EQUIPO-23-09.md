# Mensaje al equipo — 23/09/2026

> **Para:** Daniel Mazo · (cc Freddy Aparicio)
> **De:** Camilo Céspedes
> **Contexto:** cierre de mis dos PR viejas (#7 y #8), que quedaron obsoletas por el rename de
> ADR-008, y el orden en que salen las tres que las reemplazan.

---

## 1 · Para pegar en el chat (versión corta)

```text
Equipo 👋 Cerré mis PR #7 y #8 — quedaron atrapadas por el rename de ADR-008: los paths que
tocan (variante-D-shm/, "variante D") ya no existen desde que se mergeó el #13.

Las reemplazo con TRES PR nuevas, contra los nombres actuales:

  1. Fix del Makefile (memoria-compartida-c y control-dominio no compilan en Linux/WSL2
     sin -D_GNU_SOURCE — es el mismo fix que ya me habías aprobado en el #7, el git mv
     del rename se lo llevó por delante)
  2. Limpieza del front-end (index.html y servidor.py todavía citaban ADR-001 y ADR-006
     en texto que ve el usuario final — eso no va en la entrega)
  3. Documentación (arquitectura, guía del código, manual de instalación y manual de uso,
     los cuatro reescritos contra el estado actual — sin el editor de tabla que se retiró,
     con el estímulo suelto que se agregó, etc.)

ORDEN: 1 y 2 son independientes entre sí (no comparten ni un archivo) y pueden ir en
cualquier orden. La 3 va SIEMPRE AL FINAL, porque los documentos describen el sistema
YA con el fix del Makefile y YA sin las referencias a ADR — si la mergeamos antes,
quedan describiendo algo que main todavía no hace.

Y una sola de las tres toca CHANGELOG.md: la 3, al final, con una entrada que resume
las tres. Así evitamos que las tres PR se pisen tratando de escribir en el mismo lugar
del changelog el mismo día — eso sí lo íbamos a tener si cada una agregaba la suya.

Avisen si ven algún cruce que no contemplé antes de que abra la primera.
```

---

## 2 · Por qué se cerraron el #7 y el #8, en detalle

Las dos ramas (`reto/camilo-d-linux-wsl2` y `aporte/camilo-variante-d-documentacion`) salieron
de `main` **antes** de que el #13 (tu rename de ADR-008) se mergeara. El rename cambió:

- `sistema/variante-B-tcp/` → `sistema/tcp-python/`
- `sistema/variante-D-shm/` → `sistema/memoria-compartida-c/`
- y con eso, el vocabulario completo: «variante B/D» → «TCP Python» / «Memoria compartida C».

El `#7` tocaba `sistema/variante-D-shm/Makefile` y `sistema/variante-D-shm/README.md` — carpetas
que ya no existen. El `#8` documentaba «la variante D» con ese nombre en el título de cada
archivo. Ninguna de las dos se puede mergear tal cual sin reintroducir el nombre viejo.

Aparte del rename, entre el 21 y el 22/09 la interfaz web también cambió (ADR-009/010/011):
se retiró el editor de la tabla de hosts, se agregó un modo de estímulo suelto
(`--clasificar`) para que memoria-compartida-c también responda desde la web, el historial
perdió la columna de veredicto. El `#8` documentaba la versión de antes de esos cambios.

**Nada de esto invalida el trabajo de fondo** — el diagnóstico del Makefile y la estructura de
los documentos siguen sirviendo. Por eso no se descarta, se reabre contra el código actual.

## 3 · El orden de las tres PR nuevas, y por qué

| # | PR | Depende de | Por qué |
|---|---|---|---|
| 1 | Fix del Makefile | — | Cambia solo `sistema/memoria-compartida-c/Makefile` y `sistema/control-dominio/Makefile`. No comparte archivo con ninguna otra. |
| 2 | Limpieza del front-end | — | Cambia solo `app/index.html` y `app/servidor.py` (una línea cada uno). Tampoco comparte archivo con la 1. |
| 3 | Documentación | **1 y 2, mergeadas** | Los cuatro documentos (`Aportes/camilo/`) describen el Makefile ya arreglado y el front-end ya sin citas a ADR. Si el #3 se mergea primero, el repositorio queda con documentación que se adelanta a lo que el código todavía hace. |

La 1 y la 2 pueden salir en paralelo o en cualquier orden — no hay ninguna razón técnica para
preferir una sobre la otra. La 3 sale de un `main` ya actualizado con las dos, para que no
necesite rebase y para que el CHANGELOG que agrega (la única entrada de las tres) describa
algo que ya es cierto en `main`.

## 4 · Por qué un solo CHANGELOG y no uno por PR

La convención del propio `CHANGELOG.md` dice que la entrada se escribe en la misma PR que
trae el cambio, bajo la fecha en que se abre. Si las tres se abren el mismo día, las tres
intentan insertar un bloque en el mismo punto del archivo (justo debajo del primer `---`), y
la segunda y la tercera muestran conflicto al mergear — no es grave, pero es evitable.

Se evita dejando que **solo la PR de Documentación** toque `CHANGELOG.md`, con una entrada
que resume las tres. Las de Makefile y Web no lo tocan. Es la única excepción a la
convención, y es deliberada: mejor una entrada completa al final que tres que se pisan.
