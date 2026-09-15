# Cómo aportar al proyecto

Reglas mínimas. Son pocas a propósito: una convención que nadie sigue no sirve de nada.

---

## 1. Dónde va cada cosa

| Lo que tienes | Dónde va |
|---|---|
| PDF, HTML o presentación **oficial** del diplomado | `Modulo N/Material-Clase/` — tal cual llegó, sin editar |
| Tus apuntes de clase | `Modulo N/Aportes/<tu-nombre>/` |
| Una investigación tuya (o hecha con IA) | `Modulo N/Aportes/<tu-nombre>/` |
| Notas de un encuentro sincrónico | `Modulo N/Notas/` |
| Algo que fusiona varios aportes | `Modulo N/Consolidado/` |
| Una decisión técnica del equipo | `_Base-Conocimiento/ADR/` |
| Lo que se sube a Brightspace | `Modulo N/Entregables/` |
| Un concepto que sirve en varios módulos | `_Base-Conocimiento/` |

**Regla dura:** `Material-Clase/` **nunca se edita**. Si algo del material te parece incorrecto o
ambiguo, no lo corrijas ahí — regístralo en tu aporte o en el consolidado. La fuente primaria se
conserva intacta aunque esté equivocada; poder demostrar que estaba equivocada es parte del valor.

### Al terminar: regenera el índice

```bash
_Base-Conocimiento/generar-indice.py
```

Actualiza `INDICE.html`, la portada del proyecto. Tu documento aparece solo — el índice se
construye escaneando las carpetas, no hay lista escrita a mano.

### El consolidado se lee en HTML, se edita en Markdown

Cada `Modulo N/Consolidado/mN-consolidado.md` tiene su `.html` al lado. **Para leer, abre el HTML**
(índice lateral, tablas legibles, tema claro/oscuro, funciona en el móvil). **Para corregir, edita
el `.md`** y regenera:

```bash
.claude/skills/consolidar-conocimiento/consolidar_html.py "Modulo 1/Consolidado/m1-consolidado.md"
```

Solo necesita Python 3. **No edites el `.html` a mano:** se sobrescribe en la siguiente
regeneración y tu cambio se pierde.

---

## 2. Nombres de archivo

```text
m<módulo>-<tema>-<autor>.<ext>
```

| Ejemplo | Qué es |
|---|---|
| `m1-cuadernillo-estudio-camilo.html` | Aporte individual de Camilo |
| `m1-atributos-calidad-freddy.md` | Investigación de Freddy |
| `m1-consolidado.md` | La fusión — **sin nombre de autor**, porque ya es del equipo |
| `ADR-005-eleccion-transporte.md` | Decisión arquitectónica |

Sin mayúsculas, sin espacios, sin tildes en el nombre del archivo. Guiones, no guiones bajos.

---

## 3. Ficha de autoría — obligatoria

Todo aporte lleva ficha. En un `.md` va como cabecera; en un `.html` o un PDF va en el
`FUENTES.md` de tu carpeta.

```markdown
| Campo | Valor |
|---|---|
| **Autor** | Nombre completo |
| **Fecha** | AAAA-MM-DD |
| **Módulo** | N |
| **Tema** | una línea |
| **Tipo** | material-oficial · apunte · investigacion · consolidado · decision · reto · entregable · referencia |
| **Fuentes** | de dónde salió |
| **Estado** | borrador · vigente · superado |
```

**Si lo generaste con IA, dilo.** No es una falta — es información necesaria para saber cuánto
verificar. Un documento generado con IA es `investigacion`, nunca `material-oficial`.

---

## 4. Fuentes externas

Toda fuente externa lleva: **autor o entidad · URL · fecha de consulta · qué parte del análisis la
usa**. Una URL suelta no es una fuente, es un marcador.

---

## 5. Lo que NO se hace

| ❌ | Por qué |
|---|---|
| Editar el aporte de otro | Se comenta o se resuelve en el consolidado. El aporte firmado es de quien lo firmó |
| Borrar una contradicción entre aportes | Se **registra** en el consolidado, con cuál se eligió y por qué. Las contradicciones son información |
| Subir el mismo documento a dos carpetas | Duplicidad. Va en un sitio y se enlaza desde el otro |
| Editar un `.html` generado (`INDICE.html`, `mN-consolidado.html`) | Se regeneran y tu cambio desaparece |
| Poner algo generado con IA en `Material-Clase/` | Rompe la trazabilidad desde el primer día |
| Subir binarios pesados (>1 MB) sin avisar | El proyecto ya pesa 220 MB por los CSV del reto |
| Entregar sin pasar por `Consolidado/` | El entregable sale de la fusión, no de un aporte suelto |

---

## 6. Al cerrar un reto o un módulo

Preguntarse: **¿qué de esto sirve para el módulo siguiente?**
Lo que sirva sube a `_Base-Conocimiento/Aprendizajes/`. Lo que no, se queda en su módulo.

Si un módulo no deja nada en `Aprendizajes/`, o no se aprendió nada, o no se hizo la pregunta.

---

## 7. Si usas IA

Los tres del equipo usamos IA. Para que las respuestas sean consistentes:

- El contrato de trabajo está en `CLAUDE.md` (resumen) y `PROMPT-MAESTRO.md` (completo).
- Hay skills compartidas en `.claude/skills/` — se invocan por nombre, p. ej. `/consolidar-conocimiento`.
- **La IA no inventa material del diplomado.** Si algo no está en el material, la respuesta correcta
  es «no está en el material», no una versión plausible.
- Diferenciar siempre: **(a)** contenido del diplomado · **(b)** conocimiento complementario ·
  **(c)** recomendación propia. Los tres aportes existentes ya marcan esta distinción — respétala.
