> ⚠️ **OBSOLETO (14/09/2026).** Cifras del eco puro y reparto de 4 personas.
> Usar [`MENSAJE-EQUIPO-14-09.md`](MENSAJE-EQUIPO-14-09.md).

# Kit para el grupo de WhatsApp — Group 2

> Preparado el 10/09/2026. Copia y pega; no hace falta editar nada salvo donde diga `[…]`.
> **Lo único que no tengo:** los teléfonos de Freddy, Bryan y Camilo. Si no los tienes,
> pídelos por el foro de Brightspace o al correo institucional antes de crear el grupo.

---

## 1. Datos del grupo

**Nombre** (WhatsApp permite 25 caracteres):

```
Group 2 · Arq. Software
```

Alternativas: `Diplomado Arq · Group 2` · `Arquitectura PUJ · G2`

**Descripción del grupo** (pegar en Info del grupo → Descripción):

```
Group 2 — Diplomado en Arquitectura de Software y Cloud Computing (Javeriana Cali).
Freddy Aparicio · Bryan Brack · Camilo Céspedes · Daniel Mazo.

Coordinación de entregas del diplomado. 5 módulos, 02/09 a 10/11/2026.

Fechas que mandan en el Módulo 1:
• 15/09 6:00 pm — encuentro sincrónico (no obligatorio)
• 27/09 — fecha objetivo de entrega interna
• 29/09 — CIERRE del módulo. Después NO se califica.

Entregables M1: código (ZIP) + documentación técnica (PDF) + logs + informe de
resultados vs 1 ms + video ≤5 min o demo en vivo. Y la autoevaluación: 1 SOLO INTENTO.
```

**Imagen:** cualquier cosa sencilla. No pierdas tiempo aquí.

---

## 2. Primer mensaje — anclarlo al grupo

> Envíalo y mantenlo fijado (tocar el mensaje → Fijar). Es la referencia del grupo.

```
📌 Group 2 — Diplomado Arquitectura de Software

Fechas del Módulo 1:
• 15/09 6:00 pm — encuentro sincrónico (no obligatorio, graba)
• 27/09 — entrega interna nuestra
• 29/09 — cierre oficial. Después no se califica. Sin excepciones.

Entregables del reto:
1. Código fuente en ZIP
2. Documentación técnica en PDF (arquitectura + justificación + cómo se mide)
3. Logs de ejecución
4. Informe de resultados comparado contra 1 ms
5. Video MP4 ≤5 min *o* demo en vivo el 15/09 o el 29/09

Aparte: la autoevaluación M1 en Brightspace. *Un solo intento*, tiempo ilimitado.
Nadie la abra sin haber revisado los 4 Genially del módulo.
```

---

## 3. Mensaje de arranque — enviar en 3 partes

> **En tres mensajes, no en uno.** Un muro de texto en WhatsApp no se lee. Deja que
> respondan entre uno y otro; si alguien contesta al primero, mejor.

### Mensaje 1 — el gancho

```
Hola equipo 👋 Arranqué con el reto de latencia del M1 y me salió algo que creo que vale
la pena que veamos juntos antes de repartirnos el trabajo.

Monté tres versiones del mismo servicio (un eco de 32 bytes) y las medí con 3 millones de
muestras cada una:

• TCP en Python  → 13.209 ns de mediana
• TCP en C       → 12.000 ns
• Memoria compartida en C → *83 ns*

Lo interesante no es el 83. Es esto: pasar de Python a C, con el mismo transporte, mejoró
apenas *9%*. Cambiar el transporte, con el mismo lenguaje, mejoró *144 veces*.

O sea: el lenguaje era ruido. Todo el costo estaba en la capa de comunicación.
```

### Mensaje 2 — por qué importa para la entrega

```
Y el segundo hallazgo, que creo que es donde está la nota:

El reto pide latencia menor a 1 ms. Las tres versiones la cumplen *de sobra* en la mediana
(13 µs es 75 veces menos de 1 ms).

Pero mirando la cola: de 3 millones de mediciones, la versión en Python se pasó de 1 ms en
363 casos. La de C, en 141. La de memoria compartida, en *ninguno*.

O sea que dos de las tres *incumplen* el objetivo, y eso solo se ve si reportas percentiles
en lugar de promedios. Con promedios las tres parecían perfectas.

Creo que ahí está el trabajo: no en conseguir el número, que se consigue en 40 líneas, sino
en mostrar el trade-off. Que es justo el tema del módulo.
```

### Mensaje 3 — la propuesta y lo que necesito

```
LA PROPUESTA 👇

En vez de que los 4 hagamos una implementación (nos estorbaríamos, y el objetivo ya está
cumplido), que cada uno tome un transporte distinto y los comparemos con la misma
metodología:

A · HTTP/REST sobre TCP      ~50-200 µs  ← la línea base "así se hace normalmente"
B · TCP crudo                ~12-13 µs   ← ya está hecho, sirve de referencia
C · Unix socket o UDP        ~10-30 µs   ← cuánto cuesta la pila de red
D · Memoria compartida       ~83 ns      ← ya está hecho, es el límite físico

Ya dejé listo y probado el "harness" común: el script que mide, el que calcula percentiles
e histogramas, y el orquestador. Nadie arranca de cero — se copia el cliente de referencia
y se cambia el transporte. Son como 40 líneas.

LO QUE NECESITO DE USTEDES (hoy o mañana, para no perder el fin de semana):

1️⃣ ¿Les suena el enfoque comparativo, o prefieren que hagamos una sola implementación?
   Está a discusión de verdad, díganme.
2️⃣ ¿Quién toma la A y quién la C? (yo ya tengo B y D corriendo)
3️⃣ ¿Montamos repo en GitHub? Si alguien ya tiene uno, mejor.

Dos cosas más:
• Escribí a la facilitadora para confirmar si la entrega es grupal o individual — el
  enunciado está en singular pero la plataforma nos agrupó. Les cuento apenas responda.
  El plan sirve igual en los dos casos.
• ¿Quiénes pueden el *15/09 a las 6 pm*? Si llegamos con resultados le preguntamos al profe
  cómo espera que midamos, que es la duda que más nos puede costar.
```

---

## 4. Mensaje de seguimiento — si al 12/09 nadie responde

```
Equipo, les reboto lo de arriba 🙋‍♂️ Con que me digan solo una cosa me sirve: si toman la A
o la C. Yo sigo con lo mío mientras tanto, pero el 15/09 es el encuentro y sería bueno
llegar con algo del grupo, no solo mío.

Si prefieren que nos llamemos 15 minutos y lo cerramos hablando, también sirve. Díganme
cuándo les queda bien.
```

---

## 5. Cómo mantener el grupo útil

**[REC]** Tres reglas, no más. Los grupos de estudio mueren por exceso de proceso o por
falta total de él.

1. **Fechas y acuerdos van al mensaje fijado, no al chat.** Lo que se acuerde en
   conversación, edítalo en el mensaje fijado. Lo que no está fijado, no existe.
2. **Los archivos no van por WhatsApp.** Se comprimen, se pierden y no tienen versión. Van
   al repositorio Git. WhatsApp solo lleva enlaces.
3. **Una decisión por hilo.** Si hay que decidir algo, preguntarlo solo y con fecha límite.
   «¿Alguien opina?» no recibe respuesta; «¿tomas A o C? dime antes del viernes» sí.

### Lo que NO conviene hacer

- **No mandes el plan completo de entrada.** Ocho secciones en un chat espantan. Los
  documentos (`PLAN-EQUIPO.md`, `ESPEC-MEDICION.md`, los ADR) se comparten cuando ya
  aceptaron el enfoque, y por el repo.
- **No presentes las decisiones como tomadas.** Llegas con el harness montado, tres
  mediciones y los ADR escritos. Eso ahorra días, pero también puede leerse como «ejecuten
  lo que ya decidí». Por eso el mensaje 3 pregunta el enfoque *primero* y dice que está a
  discusión. **Si alguien defiende la implementación única, escúchalo en serio:** su
  argumento —que se parece más a lo que pide el enunciado literal— no es malo.
- **No des por hecho que la entrega es grupal.** Hasta que responda la facilitadora, el
  trabajo tiene que servir también si cada uno entrega por separado.

---

## 6. Checklist

- [ ] Conseguir los tres teléfonos (foro de Brightspace o correo institucional)
- [ ] Crear el grupo con el nombre y la descripción de §1
- [ ] Enviar y **fijar** el mensaje de §2
- [ ] Enviar los tres mensajes de §3, con pausa entre ellos
- [ ] Enviar el correo a la facilitadora (`EMAIL-FACILITADORA.md`) — es independiente
- [ ] Si el 12/09 no hay respuesta: enviar §4 y seguir en solitario
