# Guion de la reunión con Group 2 — mostrar avances y cerrar el reparto

> Preparado el 10/09/2026, para la primera reunión del equipo.
> **Objetivo real de la reunión: salir con A y C asignadas.** Todo lo demás es contexto.

---

## Cómo abrir — no te saltes esto

> «Hice unas mediciones para entender el problema antes de proponerles cómo repartirnos.
> Me salió algo que no esperaba y quiero ver qué opinan, porque cambia el enfoque del trabajo.»

Llegas con el harness montado, tres mediciones y los ADR escritos. Eso ahorra días de trabajo
al equipo, pero también puede leerse como «ya está todo decidido, ejecuten». Si suena así, se
desenganchan y terminas haciéndolo solo.

**Pregunta el enfoque antes de mostrar resultados.** Y si alguien propone implementación única
en vez de estudio comparativo, escúchalo en serio: su argumento —que se parece más al enunciado
literal, que está redactado en singular— no es malo.

---

## Secuencia (12–15 min, dejando aire para discusión)

### 1 · El anticlímax — 30 s

Un eco en Python sobre TCP: **mediana 13 µs**, 76 veces por debajo del objetivo, 40 líneas de
código.

> *El reto no era alcanzar el número. El número estaba alcanzado desde el principio.*

### 2 · Demo en vivo — 1 min

Dos terminales, fuente grande, **corridas cortas**:

```bash
cd harness
./run.sh D 1 --iters 100000     # memoria compartida en C
./run.sh B 1 --iters 100000     # TCP en Python
```

No corras un millón de iteraciones en vivo: tarda y pierdes a la audiencia.
Señala tres cosas de la salida: la verificación del reloj, la integridad 100 % y el p50.

### 3 · La gráfica de percentiles — 2 min

Abre `harness/graficas/percentiles.svg` en el navegador. **Es la imagen del trabajo.**

Líneas planas hasta el p99 que se disparan después, con la raya roja del milisegundo cruzando
las dos curvas de TCP y quedando muy por encima de la de memoria compartida.

> *Por mediana las tres cumplen de sobra. Por la cola, dos incumplen. Y eso solo se ve si
> reportas percentiles en vez de promedios.*

### 4 · La descomposición — 1 min

Los dos números, grandes: **1,1× contra 144,6×**.

> *Cambiar de lenguaje compró un 9 %. Cambiar de capa compró 144 veces. El 91 % del coste
> estaba en una decisión de arquitectura, no de implementación.*

Matiz que hay que decir: este servicio no hace trabajo útil. Con lógica de negocio de por
medio, la proporción cambia.

---

## Los cinco números

| Número | Qué dice |
|---|---|
| **13 µs** | El objetivo ya estaba cumplido con la primera implementación ingenua |
| **1,1× vs 144,6×** | Lenguaje frente a arquitectura |
| **363 vs 0** | Muestras por encima de 1 ms, de 3 millones (Python/TCP vs memoria compartida) |
| **420×** | La cola que queda cuando ya no hay software que quitar |
| **2,2 ms → 44 ms** | El mismo sistema medido 100 k veces vs 3 M veces: el máximo depende de la ventana |

---

## Las cuatro decisiones que hay que cerrar antes de colgar

La reunión se puede ir entera en admirar los números. No lo permitas: lo que necesitas son
estos cuatro sí o no.

- [ ] **1. ¿Estudio comparativo o implementación única?** Está a discusión de verdad.
- [ ] **2. ¿Quién toma A (HTTP/REST) y quién C (Unix socket o UDP)?** B y D ya están.
      Pídelo con nombre y fecha, no con «¿alguien se anima?».
- [ ] **3. ¿Repositorio Git, dónde?** Si alguien ya tiene uno, mejor que montar otro.
- [ ] **4. ¿En qué máquina corre la ronda final?** Si cada uno mide en su equipo, los números
      no son comparables y el estudio se cae. Es la decisión menos vistosa y la más crítica.
- [ ] 5. *(si da tiempo)* ¿Quiénes van al encuentro del 15/09 a las 6 pm?

**Escribe las respuestas en el mensaje fijado del grupo antes de que se acabe el día.**
Lo que no queda fijado, no se acordó.

---

## Tres cosas que no conviene hacer

1. **No presumas del 83 ns.** Impresiona treinta segundos, y presumir del número es exactamente
   el error que el trabajo denuncia. El valor está en el trade-off.
2. **No enseñes código.** Si preguntan por las barreras de memoria o el false sharing,
   contéstalo hablando.
3. **No des por hecho que la entrega es grupal.** Sigue sin respuesta de la facilitadora.
   Dilo explícitamente: el plan funciona en los dos escenarios.

---

## Preguntas que van a salir

| Pregunta | Respuesta corta |
|---|---|
| ¿Esto sirve en producción? | **No, y esa es la conclusión.** No funciona entre máquinas, quema dos núcleos al 100 % y no se puede depurar. |
| ¿Por qué en loopback y no en red? | Con red, la red domina y no se vería la diferencia entre transportes, que es lo que el estudio mide. Declarado como supuesto S3. |
| ¿El máximo de 44 ms no invalida todo? | Al contrario: **es** el resultado. Y con 100 k muestras era 2,2 ms — por eso se especifica en percentiles. |
| ¿Por qué C y no Rust o Go? | No están instalados y añadir un toolchain era riesgo sin beneficio. El resultado no depende del lenguaje: lo demostramos con el control. |
| ¿Y si no llegamos con las cuatro? | Con tres el estudio sigue siendo válido. La prescindible es la C. |
| ¿Cuánto trabajo es una variante? | ~40 líneas: se copia el cliente de referencia y se cambia el transporte. El harness, la medición y el análisis ya están. |

---

## Lo que puedes repartir después de la reunión

Solo si aceptaron el enfoque. En este orden:

1. `harness/README.md` — el contrato: qué tiene que cumplir cada variante. **Es lo único que
   necesitan para empezar.**
2. `ESPEC-MEDICION.md` — la metodología, para congelarla entre todos.
3. `PLAN-EQUIPO.md` y los ADR — solo si alguien pide el detalle.

**No mandes los tres de golpe.** Un chat con ocho documentos adjuntos no lo lee nadie.
