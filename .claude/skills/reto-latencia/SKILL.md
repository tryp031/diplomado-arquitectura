---
name: reto-latencia
description: Use al trabajar sobre el proyecto del Reto de Latencia Mínima (Módulo 1) — ejecutarlo, implementar una variante, medir, o cambiar el dominio de hosts. Carga los invariantes que sostienen la validez del experimento y que se rompen en silencio. Invócala con /reto-latencia o cuando el usuario pida "arranca el reto", "implementa la variante A/C", "medí la variante X", "agrega un host a la tabla" o toque cualquier archivo bajo Reto-Latencia-Minima/.
---

# Reto de Latencia Mínima — criterio de trabajo

Proyecto: `Modulo 1/Ejercicios/Reto-Latencia-Minima/reto-latencia-group2/`
Equipo: Freddy Aparicio · Camilo Céspedes · Daniel Mazo.

El README explica **qué es** el proyecto y **cómo se arranca**. Esta skill explica
**qué no se puede tocar sin invalidar algo**, que es lo que el README no puede hacer
cumplir por sí solo.

## Lo único que hay que entender antes de tocar nada

Este proyecto no es una aplicación: es un **experimento de medición** con una
aplicación encima. La diferencia es práctica, no filosófica:

> Un cambio puede dejar el sistema funcionando perfectamente y a la vez destruir la
> validez de las conclusiones del informe. Sin error, sin caída, sin que nadie se
> entere hasta la sustentación.

Por eso las reglas de abajo no son estilo ni preferencia. Cada una protege una
afirmación concreta del informe.

## Hay dos planos y el cronómetro vive en uno solo

```text
app/       PLANO DE CONTROL   milisegundos   enciende y muestra.  NO se mide.
sistema/   PLANO DE DATOS     microsegundos  cliente ⇄ servidor.  SÍ se mide.
```

**Nunca medir desde el plano de control.** Un navegador y un servidor HTTP viven en
milisegundos; el sistema responde en microsegundos. Medir desde ahí daría números del
navegador, mil veces peores, que no dicen nada del sistema.

Si alguien pide «mostrar la latencia en la web»: la web **muestra** lo que midió el
plano de datos. No cronometra.

## Invariantes — qué se rompe y qué afirmación cae

| No toques… | Porque si cambia… | ADR |
|---|---|---|
| `sistema/reloj.h` | las variantes dejan de compartir instrumento: la diferencia entre dos resultados pasa a incluir la diferencia entre dos relojes | ADR-003 |
| el límite de 16 hosts | 16 × 4 B = 64 B = una línea de caché. Pasarse saca la tabla de L1 y «clasificar no contamina la medición» deja de ser cierto | ADR-004 |
| el payload de 32 bytes | las mediciones anteriores dejan de ser comparables en forma con las nuevas | ADR-004 |
| la tabla como **archivo** leído en ejecución | si las IPs pasan a ser literales en el código, el compilador pliega el bucle entero y el clasificador **desaparece del binario**: la corrida de control mediría cero y «clasificar es despreciable» sería un artefacto del optimizador | ADR-004 |
| la frontera de medición F1 | se estaría midiendo otra cosa | ADR-001 |
| mezclar corridas de máquinas distintas | la diferencia entre los números incluye la diferencia entre las computadoras | ADR-005 |
| mezclar corridas con distinta concurrencia | `--hilos 4` y `--hilos 1` no miden lo mismo: el histórico del informe es N=1 | ADR-006 |
| contadores o `print` dentro del bucle medido | la medición pagaría por su propia barra de progreso. El progreso se reporta ENTRE lotes | ADR-006 |

Ninguno de estos es intocable para siempre. Son **decisiones registradas**: cambiarlas
exige un ADR nuevo que diga por qué, y volver a medir lo que haga falta. Lo prohibido
es cambiarlas en silencio.

## Dos cosas distintas se llaman «harness»

- `sistema/run.sh` + `analyze.py` → **harness de medición**: orquesta una corrida.
- `verificar.py` → **contrato de trabajo**: cuida que el experimento siga valiendo.

No se tocan entre sí. Si el usuario dice «harness», preguntá cuál si no es obvio.

## Rutas de trabajo

### «Quiero verlo funcionando»
`./iniciar.sh` (macOS/Linux) · `iniciar.cmd` (Windows).
Si algo falla, **no diagnostiques a mano**: `python3 doctor.py` ya sabe qué falta en
esa máquina y con qué comando se consigue. Leé su salida antes de proponer nada.

### «Voy a implementar mi variante» (A de Freddy, C de Camilo)
1. Leé `sistema/README.md`: ahí está el contrato de variante.
2. Respetá: 32 bytes en ambos sentidos, la tabla se carga **una vez** al arrancar
   —nunca dentro del bucle—, sin asignar memoria ni hacer E/S en la ruta caliente.
3. El clasificador no se reimplementa: se usa `clasificador.py` o `clasificador.h`.
4. Se puede desarrollar en cualquier máquina, Windows nativo incluido. El contrato es
   de **correctitud**, no de velocidad.
5. En cuanto exista `server.py`, el plano de control la detecta sola. No hay que
   registrarla en ningún sitio.

### «Voy a medir»
1. Solo en macOS, Linux o WSL2.
2. `cd sistema && ./run.sh <VARIANTE> <RONDA> --iters N`
   Concurrencia (solo variante B): añadí `--hilos 4`. **N=1 es el histórico del informe**;
   una corrida con hilos no se compara contra una sin hilos. Ver ADR-006.
3. Nunca borres ni sobrescribas un CSV de `resultados/`: es la evidencia del informe.
   `run.sh` ya archiva lo anterior con su fecha. El `.log` hermano no es basura —es
   lo único que dice en qué máquina se tomó la corrida—.
4. `./analyze.py --md resultados/*.csv`. Si se niega por mezclar plataformas,
   **no pases `--mezclar-plataformas` para que pase**: esa es la señal de que la tabla
   estaría comparando computadoras, no arquitecturas (ADR-005).
5. Las cifras del informe salen del equipo de referencia declarado: Apple M4, macOS
   26.6, arm64.

### «Voy a cambiar la tabla de hosts»
1. Máximo 16 hosts. No es un tope de implementación, es una decisión de diseño.
2. Solo direcciones de rangos reservados: RFC 1918 para la lista blanca, RFC 5737
   (`198.51.100.0/24`) para la negra. **Nunca una IP real.** Una IP real en una lista
   negra convierte un ejemplo en una afirmación sobre un tercero.
3. Los comentarios del CSV son parte del dominio: explican el escenario y por qué esas
   direcciones. No los borres. El plano de control es *editor de las filas*, no autor
   del dominio.
4. Los servidores releen la tabla solo al arrancar: hay que reiniciarlos.

## Cómo cerrar cualquier trabajo

```bash
python3 verificar.py
```

No es opcional y no es un test de que el código funcione: comprueba que el
experimento sigue midiendo lo que dice medir. Si falla, la salida ya dice qué
conclusión del informe deja de sostenerse y en qué ADR está la decisión.

Si el cambio fue deliberado y sí modifica el método: escribí el ADR primero, después
`python3 verificar.py --registrar`.

## Trazabilidad

El proyecto es de tres personas y las tres usan IA sobre él. Aplican las reglas de
`CONTRIBUIR.md`: el trabajo individual va firmado en `Aportes/<autor>/`, nunca se
edita el aporte firmado por otro, y las contradicciones se resuelven en el consolidado
registrando cuál se adoptó y por qué.

Al terminar algo que cambie una decisión, preguntá si corresponde un ADR nuevo. Es
barato escribirlo el mismo día y caro reconstruirlo en noviembre.
