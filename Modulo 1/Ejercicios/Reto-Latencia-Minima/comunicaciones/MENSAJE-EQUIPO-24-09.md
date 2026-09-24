# Mensaje al equipo — 24/09/2026

> **Para:** Freddy Aparicio · Camilo Céspedes
> **De:** Daniel Mazo
> **Contexto:** respuesta a la revisión de Camilo, la corrida nueva que pidió Freddy y el
> estado del proyecto a cinco días del cierre (29/09).

---

## 1 · Para pegar en el chat (versión corta)

```text
Equipo 👋 Resumen del 24/09:

1. CAMILO — tu revisión ya está en main (PR #17):
   - La carpeta resultados/archivo/ NO se borra: es la corrida del 14/09 que el informe
     cita en §7.1 como prueba de que el veredicto de TCP Python cambia según el día.
   - Quité los ADR/residuos que estaban mal (variante E en run.sh y el visor, una ruta
     rota a ESPEC-MEDICION.md). Los comentarios que explican invariantes se quedan.

2. FREDDY — hicimos la corrida nueva y es la OFICIAL desde hoy (24/09):
   - TCP Python:           p50 14,9 µs · p99.9 106 µs · 164 de 3 M muestras sobre 1 ms
   - Memoria compartida C: p50 83 ns   · p99.9 209 ns · 0 de 3 M
   - La tesis se refuerza: TCP Python dio 0 / 136 / 164 en tres corridas del mismo
     código; memoria compartida, 0 en las tres.
   - Ya están actualizados el informe, el guion del video, la presentación, los README,
     las figuras y el visor.

3. Si alguno quiere correrlo en su máquina: ver §3 de comunicaciones/MENSAJE-EQUIPO-24-09.md.
   OJO: usen la ronda 9, nunca 1-3 (esas son las oficiales).

Lo que falta para el 29/09 está en §4 del mismo archivo.
```

---

## 2 · Qué cambió el 24/09

### PR #17 — revisión de Camilo (mergeado)

| Punto de Camilo | Qué se hizo | Por qué |
|---|---|---|
| «Carpeta con logs de los primeros días que ya no se usa» | **Nada: se conserva** | `sistema/resultados/archivo/` guarda la corrida del 14/09, evidencia de §7.1. Las rondas 0 y 9 ya están rotuladas en `resultados/LEEME.md` |
| «Muchos ADR en comentarios» | Se quitaron los que estaban **mal** | Código muerto de la variante E en `run.sh`, nota E0 y cita ADR-003 visible en el visor, ruta rota a `ESPEC-MEDICION.md`, rango de ADR desactualizado en `hacer-zip.sh` |
| | Se **conservan** los que explican invariantes | Dicen por qué no se toca el reloj, los 16 hosts o los 32 B. `reloj.h` y los clasificadores están congelados por hash en `verificar.py` |

### Corrida oficial nueva — pedido de Freddy

Mismo código, mismos parámetros (`--warmup 100000 --iters 1000000`, 3 rondas por variante),
misma máquina de referencia (Apple M4, macOS 26.6, arm64).

| | p50 | p99.9 | máx | > 1 ms |
|---|---|---|---|---|
| TCP Python | 14 875 ns | 105 750 ns | 15 762 417 ns | 164 / 3 M |
| Memoria compartida C | **83 ns** | 209 ns | 41 792 ns | **0** / 3 M |

**Conclusiones que cambiaron de magnitud** (el sentido de la tesis no cambia):

| Antes (17/09) | Ahora (24/09) | Dónde |
|---|---|---|
| 74× por debajo de 1 ms | **67×** | informe, guion, presentación |
| 162× entre las dos | **179×** | ídem |
| máx de D = 447× su mediana | **504×** (42 µs) | ídem |
| B incumplía ya con 100 000 muestras | con 100 000 **cumple al límite** (991 µs); incumple desde 1 M | informe §7.3, guion 2:40, lámina A1 |
| 2 corridas independientes | **3** (14/09, 17/09, 24/09) | informe §5.2 y §7.1 |

**Una limitación nueva, declarada en el informe (supuesto S4):** la máquina no estaba en
reposo: la carga al empezar era 5,76 sobre 10 núcleos. Desde hoy `run.sh` escribe la carga en
cada log (`carga:`); antes no se registraba.

**Dos arreglos en `run.sh`:**
- Al archivar, la fecha ahora sale de la cabecera del log y no del mtime (tras un
  `git checkout` el mtime mentía: la corrida del 17/09 se archivó con fecha del 23/09; ya se
  renombró con la fecha correcta).
- Registra la carga de la máquina.

---

## 3 · Cómo correr las pruebas en su máquina

Desde `reto-latencia-group2/`:

```bash
python3 doctor.py        # qué le falta a esta máquina (Windows: doctor.cmd)
python3 verificar.py     # debe terminar en «Todo en orden»
./iniciar.sh             # la web en localhost:8080 (Windows: iniciar.cmd)
```

Para medir (solo macOS, Linux o WSL2):

```bash
cd sistema
./run.sh tcp-python 9 --warmup 100000 --iters 1000000
./run.sh memoria-compartida-c 9 --warmup 100000 --iters 1000000
./analyze.py --md resultados/resultados-*-9.csv
```

- **Ronda 9, nunca 1, 2 o 3:** esas son la corrida oficial y `run.sh` las archivaría.
- **No hagan commit de nada bajo `sistema/resultados/`** después de medir en su máquina: la
  ronda 9 también tiene un log versionado (14/09) que `run.sh` movería a `archivo/`.
- Sus números **no se comparan** con los oficiales: son de otra máquina (ADR-005). Sirven para
  ver que funciona, no como evidencia.

---

## 4 · Lo que falta para el 29/09

| # | Qué | Quién | Nota |
|---|---|---|---|
| 1 | **`Modulo 1/Entregables/` está vacío** | cualquiera | Entregable 1: `./hacer-zip.sh`. Entregable 3: los seis `.log` de `resultados/` (24/09). Son dos comandos |
| 2 | **Grabar el video** | a definir | El guion (`GUION-VIDEO.md`) y la presentación ya tienen las cifras del 24/09 |
| 3 | **Entregable 2 (PDF)** | a definir | `INFORME.pdf` se regenera con `python3 informe-a-pdf.py`. Falta decidir si esa es la versión final |
| 4 | **Documentación técnica de TCP Python** | Freddy | `Aportes/freddy/` sigue vacío |
| 5 | **Ratificar ADR-011** | Freddy y Camilo | Sigue como *Propuesta* |
| 6 | Menores | — | Mensajes `[cliente B]`/`[cliente D]` del renombre; nota Windows nativo vs WSL2 en el README (pendiente de Camilo); el visor calcula percentiles con otro método que `analyze.py` (difiere en la última cifra del p99.9 de TCP Python); `control-dominio/README.md` dice «3 % … 64 ns» y su tabla 2,3 % y 83 ns; el consolidado del M1 y `Aportes/danny/m1-clasificador-hosts-danny.html` citan cifras de corridas anteriores |
