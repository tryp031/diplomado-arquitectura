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
| **Nuevo en el proyecto** | `INDICE.html`, luego este README y `CONTRIBUIR.md` |
| **Vas a aportar algo** | `CONTRIBUIR.md` — nombres, fichas de autoría, dónde va cada cosa |
| **Buscas el estado de todo** | `_Base-Conocimiento/INDICE.md` |
| **Buscas fechas y entregas** | `_Base-Conocimiento/CRONOGRAMA.md` |
| **Quieres estudiar un módulo** | `Modulo N/Consolidado/mN-consolidado.html` — ábrelo en el navegador |
| **Vas a trabajar el reto del M1** | `Modulo 1/Aportes/danny/m1-clasificador-hosts-danny.html` (ábrelo en el navegador) |
| **Eres un agente de IA** | `CLAUDE.md` y `PROMPT-MAESTRO.md` — el contrato de trabajo |

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
├── .claude/skills/            ← skills compartidas (los tres usamos IA)
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
