# Mensaje al equipo — 16/09/2026

> **Para:** Freddy Aparicio · Camilo Céspedes
> **De:** Daniel Mazo
> **Contexto:** avance de las tareas que me tocaron en la reunión del 15/09, antes de
> vernos el **lunes 21**.
> **Hay una cosa urgente**: un bug que invalida cualquier medición tomada desde el 15/09.

---

## 1 · Para pegar en el chat (versión corta)

```text
Equipo 👋 Avancé lo mío del lunes. Dejé dos PR para revisar:

  PR #1 — limpieza del proyecto + un bug importante
  PR #2 — draft de la presentación

⚠️ LO URGENTE PRIMERO: encontré un bug en analyze.py que hacía que CUALQUIER
medición nueva saliera en CEROS. p50 = 0.00, máximo = 0.00, y encima decía
"cumple el objetivo". Sin lanzar ningún error, o sea que no había forma de
darse cuenta mirando la salida.

Venía del 15/09, de cuando se agregó la concurrencia. Si alguno midió algo
desde entonces, hay que repetirlo. Ya está arreglado en el PR #1.

QUÉ MÁS HICE (era mi tarea del lunes):

1) LIMPIEZA. El árbol tenía 6 puntos de medición y somos 3 documentando.
   Quedaron solo las 2 variantes que tienen dueño: B (Freddy) y D (Camilo).
   Se fueron A y C (nunca se implementaron) y los experimentos Bc y E.

   OJO CON ESTO: Bc y E SÍ estaban medidos de verdad. Sus números siguen
   guardados en docs/archivo/, pero ya no se pueden recalcular desde el
   código. Lo dejé escrito en el ADR-007 con lo que eso nos cuesta, y es
   lo primero que quiero que discutamos el lunes.

2) EL CSV. Pasó de 17 columnas a 11 y ahora se abre bien en Excel: los
   tiempos ya vienen en microsegundos en vez de nanosegundos, las horas se
   ven completas y la unidad está en el nombre de cada columna.

3) PRESENTACIÓN. Es un BORRADOR, no está revisado por ustedes. Son 13
   láminas, se abre en el navegador, tecla N para ver mis notas del orador.

QUÉ NECESITO DE CADA UNO PARA EL LUNES:
 · Freddy → doc técnica de la variante B
 · Camilo → doc técnica de la variante D
 · Los dos → los 3 manuales (instalación / uso / técnico) SIGUEN SIN DUEÑO.
   Es lo primero que hay que repartir.
```

---

## 2 · El bug, en detalle — esto es lo que no puede esperar

`analyze.py` leía la latencia de la **última columna** del CSV. El 15/09, al añadir la
concurrencia (ADR-006), el cliente empezó a escribir una columna `hilo` al final. La
última columna pasó a ser el número de hilo, que vale **0** en una corrida normal.

Resultado de una corrida real de la variante B, que debería dar ~13 µs:

```
  p50              0.00 µs
  máx              0.00 µs
  ¿p99.9 < 1 ms?     SÍ
```

**Los datos estaban perfectos.** El CSV crudo tenía `14459 ns`, `13708 ns`… La media real
era 13 156 ns. Lo roto era el analizador.

Lo peor no es el cero: es que **no falla**. Produce una tabla impecable que afirma que se
cumple el objetivo, sobre datos que no existen. Es exactamente la clase de error que nadie
detecta desde fuera.

Detalle incómodo: `client.py:38` ya decía *«analyze.py lee la latencia de la columna 1»*.
Nunca lo hizo. La documentación y el código llevaban un día diciendo cosas distintas.

**Qué hacer:** si alguno corrió una medición entre el 15/09 y hoy, hay que repetirla.
Ya está arreglado — ahora la columna se busca por nombre y, si el formato no se reconoce,
el análisis se detiene en vez de adivinar.

---

## 3 · La reducción de alcance — lo que hay que ratificar el lunes

Después del reparto del 15/09 el árbol tenía esto:

| | Qué era | ¿Datos? | ¿Dueño? |
|---|---|---|---|
| **B** TCP/Python | variante | ✅ 3 M | **Freddy** |
| **D** memoria compartida | variante | ✅ 3 M | **Camilo** |
| A HTTP | variante | ❌ | — |
| C socket Unix | variante | ❌ | — |
| `Bc` TCP en C | control | ✅ 3 M | — |
| `E` ICMP | línea base | ✅ 200 k | — |

Seis puntos de medición, tres personas. Se reduce a los dos que tienen dueño y datos.

### Lo que esto nos cuesta, y por eso quiero que lo ratifiquéis

`Bc` era el experimento que **separaba el efecto del lenguaje del efecto del transporte**:
9 % el lenguaje, 91 % el transporte. Sin él, comparar B contra D mezcla las dos cosas —
cambia el transporte *y* el lenguaje a la vez—, y un revisor con criterio lo va a señalar.

Las cifras **siguen siendo válidas** y están en `docs/archivo/`. Lo que se pierde es poder
recalcularlas desde el código. Si el informe usa ese dato, tiene que decir de dónde sale.

Está todo en el **ADR-007**, con las tres opciones que había y por qué se eligió esta.
Si el lunes decidimos que fue un error, se revierte: el código está en el historial de git.

---

## 4 · El CSV del plano de control

De 17 columnas a 11. La idea: **lo que ves en la pantalla es lo que se abre en Excel**.

```
n,fecha,hora_inicio,hora_fin,variante,host,ip,veredicto,sistema_us,web_ms,resultado,detalle
12,2026-09-16,="21:06:27.692",="21:06:27.708",B,core-bancario,10.20.0.11,LOCAL,78.29,15.6,OK,
```

- `sistema_us` en **microsegundos**, no en nanosegundos. Es la cifra del reto (frontera F1)
- `web_ms` en milisegundos: lo que añade el navegador. Es contraste, no medición
- El encabezado explica qué significa cada sufijo y recuerda que el objetivo es 1 ms = 1000 µs
- `detalle` solo se llena cuando la fila necesita explicación: un DESCONOCIDO o un ERROR

Se quitó el botón NDJSON. Las marcas de la frontera F1 no son evidencia del plano de
control: lo son de `sistema/resultados/`, que es la medición oficial.

---

## 5 · Higiene del repositorio

Cosas que encontré de paso y que estaban rotas desde antes:

- **7 binarios compilados estaban versionados.** El `.gitignore` los excluía bajo
  `harness/`, carpeta que se renombró a `sistema/` hace tiempo: la regla nunca se activó
- **8 enlaces rotos** en la documentación, a ADR que estaban en otra ruta
- **3 documentos duplicados** byte a byte dentro y fuera del proyecto
- **32,5 MB de peso muerto**: un `.zip` y un PDF que se regeneran solos
- `INFORME.md` **todavía listaba a Bryan como autor**, y salió del equipo el 13/09

---

## 6 · Qué necesito para el lunes 21

| Quién | Qué |
|---|---|
| **Freddy** | documentación técnica de la variante B (`sistema/variante-B-tcp/`) |
| **Camilo** | documentación técnica de la variante D (`sistema/variante-D-shm/`) |
| **Los tres** | repartir los **3 manuales**: instalación, uso y técnico. **Siguen sin dueño** |
| **Los tres** | ratificar o revertir el ADR-007 |
| **Los tres** | decidir qué corrida es la oficial: la del 10/09 o la del 14/09. Cambia una tabla del informe y una lámina de la presentación |

### Cómo poneros al día en 5 minutos

```bash
git fetch origin
git checkout reto/danny-limpieza-alcance
cd "Modulo 1/Ejercicios/Reto-Latencia-Minima/reto-latencia-group2"
python3 doctor.py      # qué puede correr tu máquina
./iniciar.sh           # levanta el plano de control
python3 verificar.py   # comprueba que el experimento sigue siendo válido
```

El README del proyecto está actualizado. La presentación se abre directamente:
`Modulo 1/Aportes/danny/m1-presentacion-reto-latencia-danny.html`, tecla `N` para mis notas.
