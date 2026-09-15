# Mensaje al equipo — 14/09/2026

> **Para:** Freddy Aparicio · Camilo Céspedes
> **Reemplaza a** `MENSAJE-EQUIPO.md` y `GRUPO-WHATSAPP.md`, cuyas cifras (100 k y 3 M del
> eco puro) y cuyo reparto (4 personas) quedaron obsoletos.
> **Objetivo:** que Freddy y Camilo arranquen A y C esta semana, y que lleguemos al
> encuentro del 15/09 con las preguntas claras.

---

## 1 · Para pegar en el chat (versión corta)

```text
Equipo 👋 Les resumo cómo quedó todo. Les dejé una página con el estado completo, el
gráfico y el contrato técnico:

<PEGAR AQUÍ EL ENLACE DE LA PÁGINA>

Lo esencial:

1) SU IDEA SE ADOPTÓ. El sistema ya no es un eco: ahora clasifica hosts y responde
   LOCAL / EXTERNO / DESCONOCIDO. Está implementado y medido. Lo único que no usamos
   fue el comando ping, y abajo explico por qué.

2) POR QUÉ NO PING: con ICMP quien responde es el kernel del sistema operativo, no un
   programa nuestro. El reto pide un sistema que escuche y responda, y el entregable que
   más pesa es justificar la arquitectura y las herramientas. Con ping no hay nada
   nuestro que justificar. Aparte, lanzar el binario ping en cada medición cuesta de 1 a
   5 ms solo en arrancar el proceso, y el objetivo del reto es 1 ms.

3) PERO LO MEDÍ IGUAL, con un socket propio, y salió algo buenísimo para el informe:
   el comando ping da 111 µs y el mismo ICMP con socket propio da 9,7 µs. 12 veces de
   diferencia, y la diferencia es la herramienta, no el protocolo. O sea: no estábamos
   midiendo ICMP, estábamos midiendo el comando ping. Es la segunda vez que nos pasa
   (la primera fue creer que el lenguaje importaba: pesaba 9%, el transporte 91%).

4) DÓNDE ESTAMOS: el objetivo de 1 ms se cumple con 12 000x de holgura. El reto nunca
   estuvo en el número. Está en el método y en explicar los trade-offs.

QUÉ FALTA — y acá los necesito:

   Freddy  -> variante A, HTTP/1.1 REST, puerto 9100.
              Es LA MÁS IMPORTANTE del informe. No por difícil, sino porque es lo que
              construiría cualquier equipo por defecto: sin ella no podemos afirmar que
              la opción simple ya cumple el umbral.

   Camilo  -> variante C, Unix domain socket, puerto 9102.
              Aísla cuánto cuesta la pila de red.

El lenguaje lo eligen ustedes: está MEDIDO que no es la variable que importa. Elijan el
que dominen. Todo lo demás (medición, percentiles, gráficas) ya está hecho y es común;
ustedes solo cambian el transporte. El contrato está en la página, son 5 reglas.

Fechas: entregamos el 27/09 (el cierre es el 29 y no quiero dejarlo para ese día).
Mañana 15/09 a las 6 pm es el encuentro; llevo resultados y 4 preguntas al profe.
¿Se les mide? Si algo del contrato no se entiende me dicen y lo hablamos.
```

---

## 2 · Si alguno pregunta «¿y qué hago exactamente?»

```text
Concreto, en 4 pasos:

1. Clonás el repo y entrás a harness/
2. Copiás variante-B-tcp/client.py a tu carpeta (variante-A-http/ o variante-C-ipc/)
3. Cambiás SOLO el transporte. El bucle de medición no se toca: t0 antes de escribir,
   t1 después de leer la respuesta completa, reloj monótono, array preasignado,
   volcado al CSV al final.
4. Corrés ./run.sh A 1 --iters 100000 y me pasás el CSV.

Lo único del dominio que tenés que hacer en tu servidor:

    tabla = cargar(ruta_del_csv)          # UNA VEZ, al arrancar

    host_id   = leer_uint32(peticion, 0)
    veredicto = tabla.get(host_id, DESCONOCIDO)
    escribir(respuesta, veredicto, host_id)

No calculés tus propios percentiles: analyze.py es único, y por eso los resultados
son comparables entre nosotros.
```

---

## 3 · Lo que NO hay que poner en el chat

- La discusión de si la conclusión anterior estaba mal. Eso es trabajo de informe, no de
  chat, y arrancar el mensaje con «me equivoqué» entierra lo que necesito de ellos.
  Está en la página, que es donde corresponde.
- El detalle del clasificador de tiempo constante, las líneas de caché y el ensamblador.
  Es el mejor contenido del informe, pero en un chat espanta.
- Pedirles opinión sobre el dominio. Ya está decidido, implementado y medido; reabrirlo
  ahora cuesta días que no tenemos. Si alguno objeta, se habla — pero no se invita.

## 4 · Si no responden en 48 h

El estudio se sostiene sin ellos: B, Bc, D y E ya están medidas y dan el rango completo.
La variante C ya estaba marcada como prescindible en el registro de riesgos. **La A no**,
así que si Freddy no puede, la asumo yo el 21/09 — son unas 60 líneas y el harness ya
está. Lo que no se puede es enterarse el 25.
