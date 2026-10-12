---
name: indice
description: Use cuando alguien pida abrir el índice del diplomado (INDICE.html), donde están las notas y cuadernillos de todos los módulos. Invócala con /indice o cuando el usuario diga "abre el índice", "ábreme el indice.html", "muéstrame las notas de los módulos" o "abre los cuadernillos".
---

# Abrir el índice del diplomado

El índice vive en `INDICE.html`, en la raíz del repo. No hay otro: no lo busques en los módulos.

## Pasos

1. Ábrelo en el navegador según el sistema operativo:
   - macOS: `open INDICE.html`
   - Linux: `xdg-open INDICE.html`
   - Windows (Git Bash): `start INDICE.html`

2. Revisa si está desactualizado: lista los documentos agregados en commits posteriores al
   último que tocó el índice.

   ```bash
   base=$(git log -1 --format=%H -- INDICE.html)
   git log "$base"..HEAD --name-only --diff-filter=A --format= \
     | grep -E '^(Modulo [0-9]+/(Consolidado|Aportes|Entregables|Notas)|_Base-Conocimiento)/' \
     | grep -Ei '\.(html|md|pdf)$' | sort -u
   ```

   Usa el rango de commits (`base..HEAD`) y filtra con `grep`. No lo cambies por `--since` ni por
   pathspecs con `*`: `--since` incluye el commit del propio índice, y un pathspec como
   `'Modulo */Aportes'` tiene que coincidir con la ruta completa, así que no devuelve nada.

   Puede listar archivos que no van en el índice (código, `FUENTES.md`, ficheros auxiliares).
   Antes de reportar, descarta los que ya aparecen en él (`grep -c <nombre> INDICE.html`).

3. Responde en una o dos líneas: que el índice quedó abierto y, si el comando del paso 2 listó
   archivos, cuántos son y cuáles hay que enlazar. **No edites el índice por tu cuenta**: ofrece
   actualizarlo y espera a que te digan que sí. Es un archivo compartido del equipo.
