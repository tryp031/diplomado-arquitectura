# Diplomado en Arquitectura de Software y Cloud Computing

**Pontificia Universidad Javeriana Cali** · Educación Continua · Modalidad virtual asincrónica
**Ventana:** 02/09/2026 → 10/11/2026 · 5 módulos (0 a 4) · **Group 2**

Este repositorio es la **memoria compartida del equipo**. Cada módulo debe aumentar el
conocimiento acumulado, no empezar de cero.

---

## Empieza aquí

> **⭐ Abre `INDICE.html` en el navegador.** Es la portada navegable de todos los documentos del
> proyecto, agrupados por módulo y por tipo. Se regenera con
> `_Base-Conocimiento/generar-indice.py` cada vez que alguien añade algo.

| Si eres… | Lee esto primero |
|---|---|
| **Acabas de entrar al repo** | La sección *Obtener el proyecto*, aquí abajo — clonar, requisitos por sistema operativo y arrancar |
| **Nuevo en el proyecto** | `INDICE.html`, luego este README y `CONTRIBUIR.md` |
| **Vas a aportar algo** | `CONTRIBUIR.md` — **nadie commitea directo a `main`**: rama + PR. Además nombres, fichas de autoría y dónde va cada cosa |
| **Buscas el estado de todo** | `_Base-Conocimiento/INDICE.md` |
| **Buscas fechas y entregas** | `_Base-Conocimiento/CRONOGRAMA.md` |
| **Quieres estudiar un módulo** | `Modulo N/Consolidado/mN-consolidado.html` — ábrelo en el navegador |
| **Vas a trabajar el reto del M1** | `Modulo 1/Aportes/danny/m1-clasificador-hosts-danny.html` (ábrelo en el navegador) |
| **Vas a usar IA sobre el proyecto** | La sección *Trabajar con IA* de este README — hay skills que debes invocar |
| **Eres un agente de IA** | `CLAUDE.md` y `PROMPT-MAESTRO.md` — el contrato de trabajo |

---

## Obtener el proyecto

El repositorio es **privado**. Si puedes abrir
[github.com/tryp031/diplomado-arquitectura](https://github.com/tryp031/diplomado-arquitectura)
ya tienes acceso; si no, pídeselo a Danny.

### 1. Requisitos

| Sistema | Qué necesitas | Cómo |
|---|---|---|
| **macOS** | git · Python 3.9+ | `xcode-select --install` (trae git y compilador). Python ya viene |
| **Linux** | git · Python 3.9+ · compilador | `sudo apt install git python3 build-essential` |
| **Windows** | [Git for Windows](https://git-scm.com/download/win) · [Python 3.9+](https://python.org/downloads) | Al instalar Python marca **«Add Python to PATH»** |
| **WSL2** *(recomendado en Windows)* | `wsl --install` en PowerShell como administrador | Después, dentro de WSL, lo mismo que Linux |

### 2. Clonar

```bash
git clone https://github.com/tryp031/diplomado-arquitectura.git
cd diplomado-arquitectura
```

> **GitHub ya no acepta tu contraseña** al clonar por HTTPS: pide un *token*. Lo más simple es
> instalar [GitHub CLI](https://cli.github.com) y ejecutar `gh auth login` una vez — después
> `git clone` funciona solo. Si prefieres SSH, usa
> `git clone git@github.com:tryp031/diplomado-arquitectura.git`.

### 3. Arrancar el reto de latencia

La ruta tiene espacios, así que **va entre comillas**:

```bash
cd "Modulo 1/Ejercicios/Reto-Latencia-Minima/reto-latencia-group2"
```

```bash
./iniciar.sh     # macOS, Linux, WSL2
```
```powershell
.\iniciar.ps1    # Windows (o doble clic en iniciar.cmd)
```

Abre `http://127.0.0.1:8080`. **No hace falta `chmod`** — los permisos de ejecución viajan en git.
**No hace falta instalar dependencias:** ni `pip`, ni `npm`, ni entornos virtuales.

**¿Algo falla?** No preguntes por chat, pregúntale a la máquina:

```bash
python3 doctor.py      # macOS / Linux / WSL
doctor.cmd             # Windows (doble clic)
```

Te dice qué tienes, qué falta y el comando exacto para conseguirlo.

### 4. Antes de medir, lee esto

> ⚠️ **En Windows nativo puedes ver y demostrar el sistema, pero no medirlo.** El plano de datos
> usa memoria compartida POSIX y sockets ICMP crudos, que ahí no existen. Las mediciones exigen
> **macOS, Linux o WSL2**, y las cifras del informe salen de **un solo equipo declarado**.

Esto no es un detalle de instalación: es una decisión de validez razonada en `ADR-005`. El detalle
completo —los tres caminos, qué corre en cada uno y por qué— está en el
[`README.md` del reto](Modulo%201/Ejercicios/Reto-Latencia-Minima/reto-latencia-group2/README.md).

**Si vas a tocar cualquier archivo del reto, invoca antes `/reto-latencia`** (ver más abajo).

---

## Cómo está organizado

```text
.
├── INDICE.html                ← portada navegable de todos los documentos. Generada
├── README.md                  ← estás aquí
├── CONTRIBUIR.md              ← reglas para aportar. Léelo antes de subir nada
├── CLAUDE.md                  ← contrato operativo para IA (resumen ejecutable)
├── PROMPT-MAESTRO.md          ← contrato completo, fuente de verdad
│
├── _Base-Conocimiento/        ← conocimiento TRANSVERSAL, vive fuera de los módulos
│   ├── INDICE.md              ← estado del diplomado + índice maestro
│   ├── CRONOGRAMA.md          ← fechas, sesiones y entregas
│   ├── EQUIPO.md              ← quién es quién y quién hace qué
│   ├── MAPA-CONCEPTUAL.md     ← grafo de conceptos entre módulos
│   ├── GLOSARIO.md            ← términos con definición contextual
│   ├── ADR/                   ← decisiones arquitectónicas registradas
│   └── Aprendizajes/          ← lo reutilizable que sale de cada módulo cerrado
│
├── _Plantillas/               ← plantillas para aportes, ADR, consolidados, entregables
├── .claude/skills/            ← skills compartidas. Se invocan con /nombre
│   ├── reto-latencia/         ← invariantes del reto M1: qué rompe el experimento
│   └── consolidar-conocimiento/  ← fusión de aportes en la nota del módulo
│
└── Modulo N/
    ├── README.md              ← estado del módulo: qué hay, quién lo hizo, qué falta
    ├── Temario/               ← temario procesado
    ├── Material-Clase/        ← material OFICIAL de Brightspace. Nunca se edita
    ├── Aportes/               ← trabajo individual, una carpeta por persona
    │   ├── danny/ camilo/ freddy/
    ├── Consolidado/           ← la fusión de todos los aportes. Una sola verdad por módulo
    │     ├── mN-consolidado.md    ← se edita aquí
    │     └── mN-consolidado.html  ← se lee aquí. Generado, no se edita
    ├── Notas/                 ← notas en crudo de los encuentros sincrónicos
    ├── Ejercicios/            ← retos y actividades
    ├── Laboratorios/
    └── Entregables/           ← lo que efectivamente se sube a Brightspace
```

### La distinción que sostiene todo

```text
Material-Clase/   →  fuente primaria. Se recibe. NO se edita.
Aportes/<autor>/  →  lo que cada uno produce. Se firma. Puede contradecir a otro.
Consolidado/      →  la fusión. Una sola verdad, con las contradicciones registradas.
Entregables/      →  lo que se entrega. Sale del consolidado, no de los aportes sueltos.
```

Si algo no encaja en ninguna de las cuatro, probablemente no debería estar en el repositorio.

---

## El flujo

```text
Material original
      ↓
Aportes individuales      ← cada uno investiga por su lado
      ↓
Consolidación             ← se fusionan, se marcan contradicciones, se conserva la fuente
      ↓
Discusión del equipo
      ↓
Decisiones (ADR)          ← lo que se decidió y POR QUÉ
      ↓
Solución del reto
      ↓
Entregable final
      ↓
Aprendizajes reutilizables → _Base-Conocimiento/Aprendizajes/
```

Al cerrar un módulo: lo que sirva para los siguientes **sube** a `_Base-Conocimiento/`.
Ese es el punto del repositorio — que el Módulo 4 arranque con lo aprendido en el 1.

---

## Trabajar con IA — las skills del equipo

Los tres usamos IA sobre esta misma base. Para que no cada uno improvise su propio criterio,
hay **skills compartidas** en `.claude/skills/`: instrucciones versionadas que el asistente
carga antes de trabajar, de modo que los tres obtengamos el mismo comportamiento.

Se invocan **por nombre, con barra**, al inicio del mensaje:

| Skill | Invócala cuando… | Qué aporta |
|---|---|---|
| `/reto-latencia` | vayas a ejecutar, medir, implementar una variante o tocar **cualquier archivo** bajo `Reto-Latencia-Minima/` | Los invariantes del experimento: qué no se puede cambiar sin invalidar una conclusión del informe, y en qué ADR está registrada cada decisión |
| `/consolidar-conocimiento` | haya que fusionar los aportes de varios en una nota consolidada del módulo | El procedimiento de fusión: conserva las fuentes, registra las contradicciones y genera el `.html` que se lee |

### Por qué esto no es decoración

`/reto-latencia` existe por un motivo concreto, y conviene entenderlo antes de tocar el reto:

> Un cambio puede dejar el sistema **funcionando perfectamente** y a la vez **destruir la validez
> de las conclusiones del informe**. Sin error, sin caída, sin que nadie se entere hasta la
> sustentación.

Ejemplos reales que la skill documenta: subir el límite de 16 hosts saca la tabla de la caché L1
y tumba la afirmación «clasificar no contamina la medición»; convertir las IPs en literales del
código hace que el compilador **elimine el clasificador del binario** y la medición de control dé
cero. Ninguno de los dos rompe nada visible.

El `README.md` del reto explica **cómo se arranca**. La skill explica **qué se rompe en silencio**.
Son complementarios, no redundantes.

### Reglas que aplican a los tres

- **La IA no inventa material del diplomado.** Si algo no está en el material, la respuesta
  correcta es «no está en el material».
- Todo documento generado con IA es `investigacion`, **nunca** `material-oficial` — aunque lo
  parezca. Verifica la ficha en el `FUENTES.md` del autor (`Aportes/<autor>/FUENTES.md`).
- Diferenciar siempre: **(a)** contenido del diplomado · **(b)** conocimiento complementario ·
  **(c)** recomendación propia.
- El contrato completo está en `CLAUDE.md` (resumen ejecutable) y `PROMPT-MAESTRO.md` (fuente de
  verdad). El asistente los lee al inicio de cada sesión.

Al cerrar cualquier trabajo sobre el reto: `python3 verificar.py`. No comprueba que el código
funcione — comprueba que el experimento **siga midiendo lo que dice medir**.

---

## Estado actual

| Módulo | Título | Estado |
|---|---|---|
| 0 | Inducción / Aula Virtual | ✅ cerrado |
| 1 | **Fundamentos de la Arquitectura de Software** | 🟡 en curso — **cierra 29/09** |
| 2 – 4 | *(pendientes de publicar)* | ⬜ |

**Entrega crítica:** Reto de Latencia Mínima · objetivo **27/09** · cierre **29/09**.
Después del cierre **no se califica**, sin excepción.

Detalle completo en `_Base-Conocimiento/INDICE.md`.

---

## Equipo — Group 2

| Integrante | Rol en el reto M1 | Variante |
|---|---|---|
| Aparicio Marín, Freddy Erney | Implementación | A — HTTP/1.1 REST · puerto 9100 |
| Céspedes Leguizamón, Camilo Andrés | Implementación | C — Unix domain socket · puerto 9102 |
| Mazo Serna, Daniel (Danny) | Arquitectura · harness · informe | D — memoria compartida + controles |

Bryan Andrés Brack Perilla no participa en el trabajo (confirmado el 13/09).
