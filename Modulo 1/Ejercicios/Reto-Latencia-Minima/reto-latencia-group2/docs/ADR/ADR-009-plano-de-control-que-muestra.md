# ADR-009 — El plano de control: qué muestra y cómo le habla a cada sistema

- **Estado:** **Aceptada** el 2026-09-22. Acordada por Group 2 en la reunión del 21/09/2026
  (notas 2, 3, 4 y 5 del backlog) y ejecutada el 22/09.
- **Fecha:** 2026-09-22
- **Decide:** Group 2 — Freddy Aparicio · Camilo Céspedes · Daniel Mazo. Ejecuta Daniel Mazo.
- **Origen:** `Modulo 1/Notas/2026-09-21-reunion-group2-ajustes-reto.md`, notas 2, 3, 4 y 5
- **Enmienda:** [ADR-002](ADR-002-variante-D-memoria-compartida.md) §«no tiene conexiones
  que aceptar» — sigue siendo cierto, y ahora hay una forma acordada de hablarle igual
- **Depende de:** [ADR-001](ADR-001-frontera-de-medicion.md) (frontera F1) ·
  [ADR-004](ADR-004-dominio-listas-de-hosts.md) (dominio) ·
  [ADR-008](ADR-008-nomenclatura-de-los-sistemas.md) (nombres)

---

## Contexto

La reunión del 21/09 pidió cuatro cambios sobre lo que ve el evaluador. Tres son
eliminaciones y una es una funcionalidad que faltaba:

| Nota | Pedido |
|---|---|
| 2 | Quitar la sección de listas blancas y negras; dejar un dropdown de hosts sin clasificar |
| 3 | Que «Probar clasificación» funcione también con memoria compartida |
| 4 | En el CSV exportado: escribir el nombre del sistema, intercambiar `web_ms`/`sistema_us`, quitar `veredicto`, `resultado` y `detalle` |
| 5 | En la grilla: quitar la columna VEREDICTO y mostrar el nombre del sistema en vez de `VAR` |

## Problema

Las notas 2, 4 y 5 son tres eliminaciones que **convergen en el mismo sitio**. El reto dejó
de ser un eco puro el 14/09 justamente para tener algo que demostrar; si se quita la
clasificación de la pantalla de listas, de la grilla y del CSV, la pregunta legítima es qué
queda por demostrar.

## Decisión

**Se ejecutan las cuatro**, con esta respuesta explícita a la pregunta de arriba.

### Dónde se sigue viendo que el sistema clasifica

En **la respuesta al estímulo**, y ese es el único lugar donde siempre importó:

```text
editor de listas   → la UI mostraba una clasificación que ella misma tenía cargada
columna VEREDICTO  → repetía, fila a fila, lo que ya se había visto al preguntar
CSV (3 columnas)   → lo mismo, en archivo
respuesta al estímulo → lo produce el SISTEMA, viaja por la frontera F1  ← se conserva
```

Los tres artefactos retirados mostraban clasificación **que el plano de control ya conocía
de antemano**: se leían de `tabla-hosts.csv`, no de una respuesta. El que se conserva es el
único donde el veredicto llega del plano de datos. La demo no perdió su prueba; perdió tres
copias de algo que la UI podía haber inventado.

**Además**, el dropdown dejó de agrupar los hosts en «Lista blanca» y «Lista negra». Antes
la UI revelaba el veredicto *antes* de preguntarlo, lo que convertía la demo en una
tautología. Ahora el veredicto sólo aparece cuando el sistema lo responde. La nota 2 mejoró
la demostración, no la debilitó.

**Lo que no se mueve:** `sistema/tabla-hosts.csv` sigue siendo el dominio, el clasificador
sigue clasificando y ADR-004 queda intacto. La medición del 17/09 sigue siendo válida: mide
un clasificador, y el sistema sigue siendo un clasificador. Lo que se retiró es un *editor*.
El plano de control era editor de las filas, nunca autor del dominio.

### Nota 3 — cómo se le habla al sistema sin sockets

ADR-002 dice que memoria compartida no tiene conexiones que aceptar: una sola ranura por
sentido, y dos clientes se pisan el payload. **Eso sigue siendo cierto y no se cambia.**

Se descartó mantener un cliente residente en el plano de control: ocuparía la única ranura
y, si alguien lanza una medición a la vez, las dos partes se pisan y **la corrida sale
contaminada sin dar error** — el peor modo de fallo posible en este proyecto.

Se adopta el cliente **de usar y tirar**: `client --clasificar <ip>` hace un intercambio,
imprime el veredicto y termina.

- Es una rama que **retorna antes** del warmup y del bucle medido. Ninguna cifra del
  informe pasa por ese código.
- El cronómetro sigue siendo F1: las mismas dos marcas alrededor del mismo intercambio.
- Se **niega a correr mientras haya una medición en curso** (`progreso["activa"]`). Ésa es
  la salvaguarda que hace aceptable el camino.
- El arranque del proceso cuesta milisegundos y **no entra** en la cifra del sistema: queda
  en `web_ms`, donde ya vivía el coste del plano de control.

**Advertencia que va en la respuesta, no sólo aquí:** un estímulo suelto arranca en frío,
sin warmup, y mide UN intercambio. Da del orden de 1–2 µs donde el informe reporta 83 ns.
**No es una contradicción y no debe citarse como medición**: el p50 del informe sale de un
millón de intercambios en caliente. Cada respuesta lleva esa nota adjunta para que nadie
tome el número de la pantalla como resultado del reto.

### Nota 4 — el CSV

Orden final: `n, fecha, hora_inicio, hora_fin, variante, host, ip, web_ms, sistema_us`.

Dos apuntes:

1. **La cabecera transcrita en la nota no era la real.** La nota decía
   `…variante, sistema_us, web_ms, host, ip…`; el archivo emitía
   `…variante, host, ip, veredicto, sistema_us, web_ms…`. El intercambio acordado se aplicó
   sobre el orden real.
2. **Quitar `resultado` y `detalle` deja el CSV sin forma de marcar una fila fallida.** Se
   quitan igual, por acuerdo, y se compensa con una línea del preámbulo: si `sistema_us` y
   `web_ms` van vacíos, ese estímulo falló. Es menos explícito que una columna `ERROR`, y se
   acepta a sabiendas.

La columna sigue llamándose `variante` aunque su contenido sea ahora el nombre: es lo que
pide la nota 4.1, y renombrar el encabezado rompería exportaciones anteriores sin ganancia.

## Consecuencias

- El editor de listas ya no existe en la interfaz (−152 líneas). El endpoint que guardaba la
  tabla sigue en el servidor, sin consumidor: **editar el dominio vuelve a ser cosa de
  `tabla-hosts.csv`**, que es donde ADR-004 lo puso.
- El filtro por veredicto del historial se retiró junto con la columna: filtrar por algo que
  no se muestra confunde.
- La justificación de los 16 hosts (64 B = una línea de caché) **vivía dentro del editor** y
  se habría perdido con él. Se conservó moviéndola al formulario de estímulos.
- **Efecto lateral detectado al probar, que el backlog no previó:** la columna VEREDICTO era
  también la que mostraba `ERROR`. Sin ella, un estímulo fallido aparecía en la grilla igual
  que uno válido —mismos guiones en los tiempos— y se detectó justamente así, con un
  servidor parado. Se marca la fila fallida junto al host (`⚠` y el error como *tooltip*) en
  vez de devolver la columna: la nota 5 pidió quitar el veredicto, no ocultar los errores.

### Acciones derivadas

- [x] `python3 verificar.py` en verde tras los cambios.
- [ ] Si la demo en vivo del 29/09 va a mostrar el CSV, avisar que una fila sin tiempos es
      una fila fallida: ya no lo dice una columna.
