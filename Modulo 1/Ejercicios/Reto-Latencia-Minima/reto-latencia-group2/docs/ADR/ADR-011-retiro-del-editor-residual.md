# ADR-011 — Se retira lo que quedaba del editor: el endpoint de escritura y el aviso de los 16 hosts

- **Estado:** **Propuesta** — decidida por Daniel Mazo el 2026-09-22 durante la revisión
  posterior a ADR-009. **Pendiente de ratificación por Freddy y Camilo**, porque enmienda
  una decisión que salió del backlog acordado en la reunión del 21/09.
- **Fecha:** 2026-09-22
- **Decide:** Daniel Mazo. Ejecuta Daniel Mazo.
- **Origen:** revisión con la aplicación en ejecución (sesión del 22/09), no del backlog.
- **Supersede parcialmente:** [ADR-009](ADR-009-plano-de-control-que-muestra.md) §Consecuencias,
  en los dos puntos citados abajo.
- **No afecta:** [ADR-001](ADR-001-frontera-de-medicion.md) (frontera F1) ·
  [ADR-003](ADR-003-resolucion-del-reloj.md) (reloj) ·
  [ADR-004](ADR-004-dominio-listas-de-hosts.md) (dominio, tope de 16, payload) ·
  [ADR-005](ADR-005-comparabilidad-entre-maquinas.md) (comparabilidad).
  **Ningún dato medido cambió** y `sistema/tabla-hosts.csv` no se tocó.

---

## Contexto

ADR-009 retiró el **editor de listas** de la interfaz y dejó constancia de dos residuos
deliberados:

> «El endpoint que guardaba la tabla sigue en el servidor, sin consumidor.»

> «La justificación de los 16 hosts (64 B = una línea de caché) vivía dentro del editor y
> se habría perdido con él. Se conservó moviéndola al formulario de estímulos.»

Al ejecutar la aplicación el 22/09 se revisaron ambos residuos en su sitio real, ya no sobre
el papel. Los dos son consecuencia del mismo retiro y se resuelven juntos.

## Decisión

### 1. Se retira `PUT /api/tabla` y todo lo que arrastra

Eliminados de `app/servidor.py`: el handler `do_PUT`, `escribir_tabla()`,
`cabecera_conservada()`, la constante `CABECERA` y el `import re` que quedó huérfano.

El motivo no es la limpieza. Un endpoint sin interfaz que lo invocara seguía siendo capaz de
**reescribir el dominio del experimento y reiniciar los servidores del plano de datos**. Un
`PUT` desde cualquier pestaña bastaba. ADR-004 puso el dominio en `tabla-hosts.csv` y ADR-009
devolvió su edición a ese archivo: mientras el endpoint existiera, esa devolución era una
convención, no un hecho. Ahora el proceso solo **lee** la tabla.

Se conservan `leer_tabla()`, `GET /api/tabla` y `TABLA_MAX` con su comentario: la lectura es
lo que alimenta el desplegable de hosts, y el campo `limite` del JSON es contrato de API que
Freddy y Camilo podrían estar consumiendo.

### 2. Se retira el desplegable «por qué solo 16 hosts» de la interfaz

ADR-009 lo había conservado a propósito. Se retira igualmente: en el formulario de estímulos
explicaba un límite que ese formulario no deja tocar, y quien manda un estímulo no decide
nada con esa información.

**Esto es una pérdida real y hay que nombrarla:** la interfaz ya no explica por sí sola por
qué el desplegable tiene 16 entradas y no 200. Quien vea solo la aplicación no encuentra ahí
el argumento de la línea de caché.

Dónde sigue vivo ese argumento, que es lo que hace asumible la pérdida:

| Dónde | Qué dice |
|---|---|
| `ADR-004` | la decisión completa, con su justificación |
| `verificar.py`, comprobación 1 | lo hace cumplir: falla si la tabla pasa de 16 |
| `servidor.py`, `TABLA_MAX` | `16 x 4 B = 64 B = una línea de caché. Ver ADR-004.` |
| cabecera de `tabla-hosts.csv` | lo explica a quien edita el dominio, que es quien puede romperlo |

El argumento se retira de donde se leía sin poder actuar y permanece donde se puede
infringir. **El invariante no se tocó: siguen siendo 16.**

## Consecuencias

- La interfaz ya no puede escribir el dominio por ninguna vía. Editar hosts es editar
  `tabla-hosts.csv` y reiniciar los servidores.
- `PUT /api/tabla` responde **501**; `GET /api/tabla` sigue respondiendo 200.
- Para la sustentación: si alguien pregunta por qué 16 hosts, ya no hay un desplegable en la
  web que lo conteste — la respuesta está en ADR-004 y la impone `verificar.py`.
- `python3 verificar.py` sigue en verde (9/9) después del cambio.

### Corrección aparte, del mismo día

«Arrancar todas» solo avisaba cuando algo fallaba y **nunca limpiaba el aviso anterior**: un
error ya resuelto —un servidor huérfano de una sesión previa ocupando el 9101— seguía en
pantalla después de que el reintento funcionara. Ahora el aviso se limpia al empezar la
operación, como ya hacía el botón de cada variante. Se detectó ejecutando la aplicación, no
leyéndola.

### Acciones derivadas

- [ ] Ratificación de Freddy y Camilo: este ADR enmienda una decisión del backlog del 21/09.
- [x] Añadir ADR-008 a ADR-011 al índice `_Base-Conocimiento/ADR/LEEME.md`, que se quedó en
      ADR-007. Hecho el 22/09, con la nota de equivalencia de nombres.
- [x] `python3 verificar.py` en verde tras los cambios (9/9).
- [x] `PUT` retirado y comprobado (501), `GET` intacto (200), estímulos y medición probados.

---

> **Nota de método.** Los dos residuos estaban **documentados** en ADR-009, así que ninguno
> era un descuido: eran deuda declarada. La diferencia entre declararla y saldarla es que un
> endpoint escrito «sin consumidor» solo está inactivo mientras nadie lo llame.
