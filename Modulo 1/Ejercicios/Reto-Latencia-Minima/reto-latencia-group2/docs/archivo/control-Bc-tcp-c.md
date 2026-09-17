> **DOCUMENTO ARCHIVADO.** El código que produjo estas mediciones fue eliminado del
> árbol el 16/09/2026 al reducir el alcance de la entrega a las variantes B y D
> (ver `docs/ADR/ADR-007-reduccion-de-alcance.md`).
>
> - **Qué era:** Control Bc — TCP crudo en C, en `sistema/control-Bc-tcp-c/`.
> - **Por qué se conserva este texto:** las mediciones son reales, fueron tomadas el
>   10/09/2026 sobre el equipo de referencia y sostienen conclusiones del informe.
>   El código se borró; el hallazgo no.
> - **Cómo recuperar el código:** `git log --all -- "sistema/control-Bc-tcp-c/"` y `git checkout <sha> -- "sistema/control-Bc-tcp-c/"`.
>
---

# Control Bc — TCP crudo en C

**No es una quinta variante del estudio. Es un experimento de control.**
Responsable: Daniel Mazo Serna · medido el 10/09/2026 · 3 rondas × 1 000 000

---

## Por qué existe

La comparación B (TCP/Python) contra D (memoria compartida/C) **mezcla dos variables**:
cambia el transporte *y* el lenguaje a la vez. Con esos dos datos solos, el factor de 159×
no se puede atribuir a ninguna de las dos causas. Un revisor con criterio lo detecta de
inmediato, y con razón: la conclusión no se sostendría.

Este binario mantiene **el transporte de B** y cambia **solo el lenguaje**. Con tres puntos
en vez de dos, el efecto se descompone:

```text
   B  (Python + TCP) ──── cambia el LENGUAJE ────▶ Bc (C + TCP)
   Bc (C      + TCP) ──── cambia el TRANSPORTE ──▶ D  (C + shm)
```

Es el mismo transporte, el mismo payload, la misma frontera F1, el mismo reloj
(`../reloj.h`) y la misma metodología. La única diferencia con `variante-B-tcp/` es que
esto es C y aquello es Python. Traducción literal, decisión por decisión: `TCP_NODELAY`,
conexión persistente, buffer preasignado, sin lógica en la ruta caliente.

## Uso

```bash
../run.sh Bc 1 --port 9111 --warmup 100000 --iters 1000000
```

---

## El resultado, y por qué contradice la intuición

Agregado de 3 rondas × 1 M = 3 000 000 de muestras por fila. Todo en nanosegundos.

| | p50 | p99 | p99.9 | máx | media |
|---|---|---|---|---|---|
| **B** · Python + TCP | 13 209 | 57 625 | 184 083 | 44 020 084 | 15 579 |
| **Bc** · C + TCP | 12 000 | 45 459 | 107 458 | 29 423 042 | 13 556 |
| **D** · C + memoria compartida | **83** | **125** | **167** | **34 833** | **70** |

### Descomposición del factor total

| Salto | Diferencia p50 | Factor | Peso |
|---|---|---|---|
| **Lenguaje** (B → Bc): Python → C | 1 209 ns | **1,1×** | **9,2 %** |
| **Transporte** (Bc → D): TCP → memoria compartida | 11 917 ns | **144,6×** | **90,8 %** |
| Total (B → D) | 13 126 ns | 159,1× | 100 % |

> **Reescribir el servicio en C habría comprado un 9 % de mejora. Cambiar de capa de
> comunicación compró 144×.**

Esta es la conclusión más valiosa de todo el trabajo, y es contraintuitiva: ante un
requisito de latencia, el reflejo habitual es «cambiemos a un lenguaje más rápido». Aquí
los datos muestran que el lenguaje era **ruido** frente a la decisión arquitectónica.

El intérprete de Python añade ~1,2 µs por intercambio. Es real y es medible. Pero está
sepultado bajo los ~12 µs que cuestan las dos llamadas al sistema, las copias del kernel,
la pila TCP/IP y el despertar del planificador — y esos ~12 µs los paga igual C.

**[REC] El titular del informe:** *optimizar en la capa equivocada. El 91 % del coste
estaba en una decisión de arquitectura, no en una decisión de implementación.* Ese es
exactamente el contenido del Módulo 1: decisiones estructurales frente a detalles de
implementación, y por qué el arquitecto se ocupa de las primeras.

### Matiz obligatorio, para no exagerar la conclusión

El efecto del lenguaje es pequeño **en este servicio**, que no hace nada: recibe 32 bytes
y devuelve 32 bytes. En cuanto haya lógica de negocio, serialización o acceso a datos, el
peso del lenguaje crece y esta proporción cambia. **Lo que el experimento demuestra es que
el transporte domina cuando el trabajo útil es despreciable**, no que el lenguaje nunca
importe. Decirlo así es lo que separa un hallazgo de una consigna.

---

## Segundo hallazgo: la cola que se mide depende de cuánto se mire

La primera corrida de B (08/09) fue de **100 000** iteraciones y dio un máximo de
**2,2 ms**. Estas rondas son de **1 000 000** cada una, y el máximo subió a **44 ms**.

| Muestras observadas | Máximo de B |
|---|---|
| 100 000 | 2 202 000 ns |
| 3 000 000 | **44 020 084 ns** — **20× peor** |

No cambió el sistema: cambió cuánto se miró. **El máximo no es una propiedad del sistema,
es una propiedad de la ventana de observación.** Cuanto más se mide, peores colas
aparecen, porque se capturan eventos más raros: planificación, interrupciones, presión de
memoria, termorregulación.

Consecuencias que van al informe:

1. **Reportar un máximo sin decir sobre cuántas muestras es una cifra sin significado.**
   ESPEC §3 debería exigir `n` junto a cada máximo — y lo exige, por eso `n` está en la tabla.
2. Por eso los sistemas serios se especifican con **percentiles**, no con máximos: el p99.9
   es estable entre rondas (97–114 µs en Bc), mientras el máximo salta de 13 a 29 ms.
3. **B y Bc incumplen el objetivo**: 363 y 141 muestras por encima de 1 ms respectivamente,
   de 3 millones. D no lo incumple ni una sola vez.

---

## Cumplimiento del objetivo de 1 ms — 3 000 000 de muestras por fila

| | máx | muestras > 1 ms | veredicto |
|---|---|---|---|
| B · Python + TCP | 44 020 084 ns | **363** | ❌ incumple |
| Bc · C + TCP | 29 423 042 ns | **141** | ❌ incumple |
| D · C + shm | 34 833 ns | **0** | ✅ cumple |

**Pasar a C no arregla el incumplimiento: lo reduce de 363 a 141 casos.** El problema no
era el lenguaje. Era atravesar el kernel.
