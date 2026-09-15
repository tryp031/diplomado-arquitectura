# Sistema Clasificador de Hosts — Group 2

Entrega del **Reto de Latencia Mínima**, Módulo 1 del Diplomado en Arquitectura de
Software y Cloud Computing, Pontificia Universidad Javeriana Cali.

**Freddy Aparicio · Camilo Céspedes · Daniel Mazo**

---

## Arrancar

**macOS o Linux**

```bash
./iniciar.sh
```

**Windows** — doble clic en `iniciar.cmd`, o desde PowerShell:

```powershell
.\iniciar.ps1
```

Compila lo que esta máquina pueda compilar, levanta el plano de control y abre el
navegador en `http://127.0.0.1:8080`. Solo necesita **Python 3.9 o superior**.
Sin `npm`, sin `pip install`, sin `node_modules`.

**¿Algo no arranca?** No preguntes por chat, preguntale a la máquina:

```bash
python3 doctor.py      # macOS / Linux / WSL
doctor.cmd             # Windows (doble clic)
```

Te dice qué tenés, qué falta y el comando exacto para conseguirlo.

---

## Tres caminos, no uno

El plano de control es Python puro y corre en todas partes. El plano de datos usa
memoria compartida POSIX, sockets ICMP crudos y un compilador de C — y eso en Windows
nativo no existe. Así que hay tres caminos, y conviene saber en cuál estás:

| Camino | Qué corre | Sirve para |
|---|---|---|
| **macOS / Linux nativo** | todo | las mediciones del informe |
| **WSL2 sobre Windows**<br>`wsl --install` | todo | desarrollar variantes en C, medir tu plataforma |
| **Windows nativo**<br>sin instalar nada | interfaz + variantes en Python | ver el sistema, desarrollar A y C, demostrar |

Windows nativo no quedó de segunda por descuido. Portar el plano de datos a Win32
significaría **una segunda implementación del sistema medido**, y cualquier diferencia
entre las dos sería indistinguible de una diferencia entre arquitecturas. El costo no
es de esfuerzo: es de validez. Está razonado en
[`docs/ADR/ADR-005`](docs/ADR/ADR-005-comparabilidad-entre-maquinas.md).

> **La regla que sale de ahí:** cualquiera ejecuta el proyecto donde quiera. Las cifras
> del informe salen de **un solo equipo declarado**. Si intentás comparar corridas de
> máquinas distintas, `analyze.py` se niega y te explica por qué.

---

## ⚠️ Lo primero que hay que entender: hay dos planos

```text
┌──────────────────────────────────────────────────────────────────┐
│  PLANO DE CONTROL — app/        milisegundos        NO se mide    │
│  React + HTTP. Formularios, listas, botones, gráficas.            │
└─────────────────────────────┬────────────────────────────────────┘
                              │  "medí 50 000 intercambios contra B"
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  PLANO DE DATOS — sistema/      microsegundos       SÍ se mide    │
│  cliente ⇄ servidor. EL CRONÓMETRO VIVE AQUÍ DENTRO.              │
└──────────────────────────────────────────────────────────────────┘
```

**La aplicación web no es el sistema del reto.** Un navegador y un servidor HTTP
viven en milisegundos; el sistema responde en microsegundos. Si midiéramos desde
el navegador, los números serían del navegador —mil veces peores— y no dirían
nada del sistema.

Por eso el plano de control **enciende** el sistema y **muestra** lo que mide,
pero no participa. Es el mismo patrón por el que el panel de una máquina
industrial no es la máquina.

### La prueba de que la separación funciona

Las mismas mediciones, lanzadas desde el navegador y desde la línea de comandos:

| Variante | Desde `./run.sh` | Desde la aplicación web |
|---|---|---|
| B · TCP en Python | 13,4 µs | 13,46 µs |
| Bc · TCP en C | 11,5 µs | 11,67 µs |
| D · memoria compartida | 83 ns | 83 ns |

Idénticos. Quien aprieta el botón no cambia lo que se mide.

### Y el contraste que lo hace visible

El formulario de estímulos muestra **dos números a la vez**: lo que tardó el
sistema (µs) y lo que tardó el viaje completo desde el navegador (ms). Ver 13 µs
al lado de 4 ms en la misma fila es la demostración de por qué la web no puede
ser el plano de datos.

---

## Qué hace el sistema

Recibe **32 bytes** con una dirección IPv4 y responde **32 bytes** con un veredicto:

| Veredicto | Cuándo |
|---|---|
| `LOCAL` | el host está en la **lista blanca** |
| `EXTERNO` | el host está en la **lista negra** |
| `DESCONOCIDO` | no está en ninguna de las dos |

La tabla son **16 hosts × 4 bytes = 64 bytes = exactamente una línea de caché**.
No es un tope arbitrario: es lo que garantiza que clasificar cueste ~1,9 ns y no
contamine la medición. La aplicación rechaza pasar de 16 y explica por qué.
Decisión completa en [`docs/ADR/ADR-004`](docs/ADR/ADR-004-dominio-listas-de-hosts.md).

Las direcciones de ejemplo están en rangos reservados: **RFC 1918** para la lista
blanca (`10.0.0.0/8`, privadas) y **RFC 5737** para la negra (`198.51.100.0/24`,
reservada para documentación). No pertenecen a nadie y no enrutan. Poner una IP real
en una lista negra convierte un ejemplo en una afirmación sobre un tercero;
`verificar.py` lo impide.

---

## Antes de dar algo por terminado

```bash
python3 verificar.py
```

Comprueba los invariantes que sostienen las conclusiones del informe: que la tabla
siga cabiendo en una línea de caché, que el reloj no haya cambiado sin registrar la
decisión, que C y Python clasifiquen igual, que cada resultado tenga su plataforma.

No es un test de que el código funcione. Es un test de que **el experimento siga
midiendo lo que dice medir** — un sistema puede funcionar perfecto y haber dejado de
ser válido como medición, sin un solo error en pantalla.

Cada fallo dice qué conclusión del informe deja de sostenerse y en qué ADR está la
decisión que se está rompiendo.

---

## Estructura

```text
reto-latencia-group2/
├── iniciar.sh · iniciar.ps1 · iniciar.cmd    arrancar, según el sistema
├── doctor.py · doctor.cmd                    ¿qué puede correr esta máquina?
├── verificar.py                              el contrato de trabajo
├── app/                    PLANO DE CONTROL
│   ├── servidor.py         API sin dependencias (stdlib de Python 3)
│   └── index.html          interfaz React 18 desde CDN, sin build
├── sistema/                PLANO DE DATOS — lo que el reto mide
│   ├── tabla-hosts.csv     el dominio: fuente única de verdad
│   ├── clasificador.h/.py  la clasificación, en C y en Python
│   ├── reloj.h             el instrumento de medición, compartido
│   ├── variante-B-tcp/     TCP crudo en Python
│   ├── control-Bc-tcp-c/   TCP crudo en C (control: aísla el lenguaje)
│   ├── variante-D-shm/     memoria compartida + espera activa
│   ├── variante-E-icmp/    ICMP (línea base: responde el kernel)
│   ├── variante-A-http/    ⬜ Freddy
│   ├── variante-C-ipc/     ⬜ Camilo
│   ├── control-dominio/    mide cuánto cuesta clasificar
│   ├── run.sh · analyze.py el harness de MEDICIÓN
│   ├── demo.py             demostración por línea de comandos
│   ├── visor/              visor estático de resultados
│   └── resultados/         CSV + su log de plataforma
├── contrato/               herramientas del contrato de trabajo
└── docs/
    ├── ENUNCIADO.md        el reto, literal
    ├── DISENO-ARQUITECTURA.md
    └── ADR/                las cinco decisiones registradas
```

> **Dos cosas distintas se llaman «harness» en este proyecto.** `sistema/run.sh` +
> `analyze.py` son el **harness de medición**: orquestan una corrida. `verificar.py`
> es el **contrato de trabajo**: cuida que el experimento siga siendo válido. No se
> tocan entre sí.

---

## Sin la interfaz — solo línea de comandos

Requiere macOS, Linux o WSL2.

```bash
cd sistema
./run.sh B 1 --iters 1000000        # una medición completa
./analyze.py --md resultados/*.csv  # tabla comparativa
python3 demo.py --variante B        # demo interactiva
```

Los resultados del informe salen de aquí, nunca de la aplicación web.

---

## Resultados

| Arquitectura | Mediana | Cola p99,9 | Objetivo 1 ms |
|---|---|---|---|
| D · memoria compartida | **0,08 µs** | 0,12 µs | ✅ 12 000× por debajo |
| E · ICMP (el kernel) | 9,7 µs | 14,8 µs | ✅ |
| Bc · TCP en C | 11,5 µs | 30,1 µs | ✅ |
| B · TCP en Python | 13,4 µs | 39,0 µs | ✅ |
| — red real a internet | 16 984 µs | 52 111 µs | ❌ 17× por encima |

Sobre 9,15 millones de muestras. **Equipo de referencia: Apple M4, macOS 26.6, arm64.**

**El objetivo se cumple con cualquiera de las opciones locales.** El reto nunca
estuvo en alcanzar el número: está en el método, y en explicar qué se compra y
qué se paga con cada arquitectura.

---

## Para el equipo

- El contrato para implementar una variante está en [`sistema/README.md`](sistema/README.md).
- Freddy → variante A (HTTP/1.1), puerto 9100. Camilo → variante C (socket Unix), puerto 9102.
- En cuanto exista `sistema/variante-A-http/server.py`, la aplicación la detecta sola
  y aparece en la lista con su botón de arrancar. No hay que tocar nada más.
- Las variantes en Python se desarrollan en cualquier máquina, Windows nativo incluido.
  El contrato es de **correctitud**, no de velocidad: la corrida final de medición son
  minutos en el equipo de referencia.
- Si trabajás con Claude Code, la skill `reto-latencia` carga el criterio del proyecto
  (qué no se toca y por qué). Invocala con `/reto-latencia` antes de empezar.
- Antes de decir «listo»: `python3 verificar.py`.
