# ADR-007 — Reducción del alcance a las variantes B y D

- **Estado:** Propuesta · pendiente de aceptación del equipo en la reunión del 21/09
- **Fecha:** 2026-09-16
- **Decide:** Daniel Mazo (tarea asignada en la reunión del 15/09) · ratifica Group 2
- **Origen:** división de trabajo acordada el 15/09 tras la asesoría con el docente —
  Freddy documenta la variante B (TCP/Python), Camilo documenta la variante D (memoria
  compartida/C), Daniel limpia el código y prepara la presentación
- **Supersede parcialmente:** [ADR-004](ADR-004-dominio-listas-de-hosts.md) §Entregables
  (ICMP como línea base) · [ADR-006](ADR-006-concurrencia-y-hilos.md) §Pendientes (medir `Bc` con hilos)
- **Depende de:** [ADR-001](ADR-001-frontera-de-medicion.md) (frontera F1) ·
  [ADR-005](ADR-005-comparabilidad-entre-maquinas.md) (comparabilidad)

---

## Contexto

Al 15/09 el árbol contenía seis puntos de medición:

| | Qué era | Estado |
|---|---|---|
| **A** HTTP/1.1 | variante | solo un `TODO.md`. Nunca implementada, cero muestras |
| **B** TCP/Python | variante | implementada, 3 M de muestras. **Documenta Freddy** |
| **C** socket Unix | variante | solo un `TODO.md`. Nunca implementada, cero muestras |
| **D** memoria compartida/C | variante | implementada, 3 M de muestras. **Documenta Camilo** |
| **Bc** TCP/C | *control* | implementado, 3 M de muestras (10/09) |
| **E** ICMP | *línea base* | implementada, 200 k muestras + 300 contra internet |

La división de documentación acordada asigna **una variante a cada persona**. Los cuatro
puntos restantes no tienen dueño, y dos de ellos —A y C— no tienen siquiera código.

## Problema

¿Qué se conserva en el árbol de la entrega?

## Opciones consideradas

### Opción A — Conservar todo

- **A favor:** `Bc` descompone el factor 159× en lenguaje (9,2 %) y transporte (90,8 %),
  que es la conclusión más fuerte del informe. `E` aporta la línea base de red real
  (17 ms contra internet) que impide presumir de 83 ns sin decir que se midió sin red.
- **En contra:** seis puntos de medición y tres documentadores. A y C ocupan espacio sin
  aportar un solo dato. El lector tiene que entender la diferencia entre *variante*,
  *control* y *línea base* antes de leer la primera cifra.

### Opción B — Conservar solo lo que tiene dueño y datos: B y D

- **A favor:** el árbol coincide con la división de trabajo. Dos carpetas, dos
  responsables, dos documentos técnicos. La estructura se explica sola.
- **En contra:** **la comparación B vs D mezcla dos variables** —cambia el transporte
  *y* el lenguaje a la vez—. Sin `Bc` no hay forma de atribuir el 159× a ninguna de las
  dos causas. Es exactamente la objeción que el README de `Bc` anticipaba.

### Opción C — Conservar B, D y Bc; borrar A, C y E

- **A favor:** conserva la descomposición lenguaje/transporte, que es lo único
  irremplazable, a cambio de una sola carpeta extra.
- **En contra:** `Bc` sigue sin documentador asignado y se pierde la línea base de red.

## Decisión

**Se adopta la opción B.** Quedan en el árbol `sistema/variante-B-tcp/` y
`sistema/variante-D-shm/`. Se eliminan `variante-A-http/`, `variante-C-ipc/`,
`control-Bc-tcp-c/` y `variante-E-icmp/`, junto con los 18 archivos de resultados de
`Bc` y `E` que quedaban sin código que los reprodujera.

La decisión se toma con la objeción de la opción B **explícitamente sobre la mesa y
aceptada**. Queda registrada aquí y no en una conversación, que es justamente el
propósito de un ADR.

### Qué se conserva pese al borrado

| Se conserva | Dónde | Por qué |
|---|---|---|
| Hallazgos de `Bc` | `docs/archivo/control-Bc-tcp-c.md` | las mediciones son reales y están tomadas; el código se borró, el hallazgo no |
| Hallazgos de `E` | `docs/archivo/variante-E-icmp.md` | ídem, incluida la línea base de internet |
| El código de los cuatro | historial de git | `git log --all -- <ruta>` y `git checkout <sha> -- <ruta>` |
| `control-dominio/` | en su sitio | no es una variante: mide que clasificar cuesta 1,9 ns y que no hay canal lateral temporal. Sostiene ADR-004 y no compite con B ni D |

## Consecuencias

### Lo que deja de poder afirmarse

1. **La descomposición del 159× en «9 % lenguaje / 91 % transporte» ya no es
   reproducible desde el árbol.** Sigue siendo cierta y sigue documentada en
   `docs/archivo/`, pero quien clone el repositorio hoy no puede recalcularla.
2. **La comparación B vs D mezcla transporte y lenguaje.** Si el informe la presenta,
   tiene que decirlo, y citar `docs/archivo/control-Bc-tcp-c.md` como el trabajo que ya
   separó las dos causas. Presentarla sin ese matiz sería sostener una conclusión que el
   árbol ya no respalda.
3. **No queda línea base de red real en el árbol.** Todas las cifras vivas son de
   loopback. El supuesto S3 —«sin red física»— pasa a ser una limitación declarada y no
   una comparación medida.

### Lo que no cambia

- Frontera F1, reloj compartido, payload de 32 bytes y el límite de 16 hosts siguen
  intactos: ADR-001, ADR-003 y ADR-004 no se ven afectados.
- `contrato/coherencia.c` y la comprobación 4 de `verificar.py` conservan su valor: ya
  no protegen la comparación B vs `Bc` sino la comparación **B vs D**, que es la única
  que queda. Su redacción se actualizó en consecuencia.

### Acciones derivadas

- [ ] Ratificar esta decisión en la reunión del **21/09**.
- [ ] Al redactar el informe, incluir el matiz del punto 2 allí donde se compare B con D.
- [ ] Decidir si la presentación usa las cifras archivadas de `Bc` y `E` —son válidas y
      están fechadas— o si se limita a lo reproducible desde el árbol.

---

> **Nota de método.** Los ADR anteriores **no se editaron** para borrar las menciones a
> `Bc`, `E`, `A` y `C`. Un ADR registra lo que se decidió en su momento y con qué
> información; reescribirlo a posteriori destruye justamente lo que lo hace útil. Las
> menciones que quedan en ADR-002, 004, 005 y 006 son correctas *en su fecha*, y este
> documento es el que dice qué cambió después.
