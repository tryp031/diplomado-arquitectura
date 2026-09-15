# ADR-005 — Correr en cualquier máquina, medir en una sola

- **Estado:** Propuesta · pendiente de aceptación del equipo
- **Fecha:** 2026-09-15
- **Decide:** Group 2 (Freddy Aparicio · Camilo Céspedes · Daniel Mazo)
- **Depende de:** [ADR-001](ADR-001-frontera-de-medicion.md) (frontera F1) ·
  [ADR-003](ADR-003-resolucion-del-reloj.md) (el reloj como instrumento compartido)

---

## Contexto

Hasta el 14/09 el proyecto se ejecutaba en una sola máquina, la de Daniel: Apple M4,
macOS 26.6, arm64. Todas las cifras del informe salieron de ahí.

Desde el 15/09 el equipo necesita que los tres puedan ejecutar el proyecto. Freddy y
Camilo trabajan en Windows, y les toca implementar las variantes A y C. Eso plantea
dos preguntas que parecen una sola y no lo son:

1. ¿Puede cada uno **ejecutar** el sistema en su máquina?
2. ¿Pueden las mediciones de cada uno **entrar en la misma tabla** del informe?

### Por qué no son la misma pregunta

`reloj.h` ya defiende el principio, a escala de instrumento:

> El atributo AC-3 (comparabilidad) exige que las variantes usen el MISMO instrumento,
> no uno equivalente. Si cada una define su propio reloj, la diferencia entre dos
> resultados incluye la diferencia entre dos relojes.

El argumento no depende de que se trate de un reloj. Se extiende, palabra por palabra,
a la máquina: **si dos corridas ocurren en computadoras distintas, la diferencia entre
sus resultados incluye la diferencia entre las dos computadoras.** Y una tabla que
compara «memoria compartida» contra «TCP» invita a leer la diferencia como si fuera
entre arquitecturas.

Las magnitudes en juego no son de segundo orden. Entre un M4 y un portátil x86 con
WSL2 cambian la frecuencia base, la jerarquía de caché, el planificador, la latencia
de las llamadas al sistema y el comportamiento térmico. Una variante puede parecer
2× mejor que otra solo por dónde se ejecutó.

### La tentación que hay que nombrar

Lo cómodo sería pedir que los tres midan y juntarlo todo: más muestras, más máquinas,
parece más robusto. **Es exactamente al revés.** Más muestras de poblaciones distintas
no reducen el error: introducen una variable oculta —la máquina— que el informe no
declara y el lector no puede descontar.

---

## Decisión

Se separan dos derechos que hasta ahora venían juntos:

| | Quién | Dónde |
|---|---|---|
| **Ejecutar, desarrollar, depurar, demostrar** | los tres | cualquier máquina |
| **Medir para el informe** | equipo de referencia declarado | Apple M4 · macOS 26.6 · arm64 |

Y tres reglas derivadas:

1. **Toda corrida queda atada a su plataforma.** El `.log` que escribe `run.sh` ya
   registra `host:`, `cpu:` y compilador. Ese log es parte de la evidencia, no un
   subproducto: un CSV sin su log no puede atribuirse a ninguna máquina y no sirve
   como respaldo de una cifra.
2. **No se comparan corridas de máquinas distintas.** `analyze.py` lo impide: si los
   CSV que recibe vienen de plataformas diferentes, se niega a producir la tabla y
   explica por qué. Quien realmente necesite la mezcla la pide con
   `--mezclar-plataformas`, y entonces el informe debe decir que la tabla mezcla.
3. **Medir en otra máquina es válido y es útil** — como corrida propia, con su equipo
   declarado y su propia tabla. Lo que no es válido es fundirla con las demás.

### Por qué la regla vive en `analyze.py` y no en el README

Una regla escrita en un README se ignora sin querer, sobre todo a las dos de la
mañana antes de una entrega. Una regla que vive en la herramienta por donde pasa
*toda* cifra que llega al informe no se puede ignorar sin querer: hay que teclear
una bandera que dice lo que estás haciendo.

Es el mismo criterio que ya aplica `run.sh` al archivar los resultados en vez de
sobrescribirlos, después de que el 14/09 se perdieran las corridas del 10/09.

---

## Los tres caminos de ejecución

| Camino | Quién | Qué corre | Sirve para |
|---|---|---|---|
| **macOS / Linux nativo** | Daniel | todo | las mediciones del informe |
| **WSL2 sobre Windows** | Freddy, Camilo | todo | desarrollar variantes en C, medir su plataforma |
| **Windows nativo** | cualquiera | plano de control + variantes en Python | ver el sistema, desarrollar A y C, demostrar |

Windows nativo no es un camino de segunda por descuido: el plano de datos usa memoria
compartida POSIX, sockets ICMP crudos y un compilador de C. Portarlo a Win32
significaría **una segunda implementación del sistema medido** — es decir, duplicar
justo aquello cuya unicidad sostiene la comparación. El costo no es de esfuerzo: es
de validez.

---

## Consecuencias

**A favor**

- Los tres ejecutan el proyecto; nadie queda fuera del trabajo diario.
- Las cifras del informe conservan una sola población y un equipo declarado.
- La regla se hace cumplir sola, en la herramienta, no en la memoria de nadie.

**En contra, y hay que decirlo**

- Freddy y Camilo dependen de la máquina de Daniel para las cifras finales. Es un
  cuello de botella real en la última semana.
- En Windows nativo no pueden ejecutar D, E ni Bc. Para verlas necesitan WSL2.
- Una corrida hecha en WSL2 no entra en la tabla principal aunque haya costado
  trabajo. Conviene saberlo antes de invertir la noche, no después.

**Mitigación:** las variantes se desarrollan y validan en cualquier máquina —el
contrato es de correctitud, no de velocidad—. Solo la corrida final de medición
necesita el equipo de referencia, y toma minutos.

---

## Alternativas descartadas

| Alternativa | Por qué no |
|---|---|
| **Docker para los tres** | Reproducibilidad máxima del entorno, pero el contenedor añade capas de red y en macOS corre dentro de una VM. Mediría la latencia de Docker, no la del sistema. En un reto cuyo objeto de estudio *es* la latencia, contamina justo lo que se mide. |
| **Portar el plano de datos a Win32** | Una segunda implementación del sistema medido. Cualquier diferencia entre las dos sería indistinguible de una diferencia entre arquitecturas. |
| **Medir todos y promediar** | Mezcla poblaciones distintas bajo una media que no describe a ninguna. Más muestras no arreglan una variable oculta. |
| **Medir todos y publicar tablas separadas** | Es exactamente lo que esta decisión permite. No está descartada: está incluida en la regla 3. |
