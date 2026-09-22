# ADR-010 — Qué se empaqueta en el entregable: una regla, no una mudanza

- **Estado:** **Aceptada** el 2026-09-22. Acordada por Group 2 en la reunión del 21/09/2026
  (notas 7, 8 y 11 del backlog) y ejecutada el 22/09.
- **Fecha:** 2026-09-22
- **Decide:** Group 2 — Freddy Aparicio · Camilo Céspedes · Daniel Mazo. Ejecuta Daniel Mazo.
- **Origen:** `Modulo 1/Notas/2026-09-21-reunion-group2-ajustes-reto.md`, notas 7, 8 y 11
- **Depende de:** [ADR-005](ADR-005-comparabilidad-entre-maquinas.md) (trazabilidad de la
  evidencia) · [ADR-008](ADR-008-nomenclatura-de-las-variantes.md) (nombres)

---

## Contexto

El enunciado pide tres entregables distintos y el árbol los tenía mezclados:

| | Qué pide | Dónde estaba |
|---|---|---|
| 1 | ZIP con el código fuente | todo el proyecto, con `docs/` y 143 MB de CSV dentro |
| 2 | Documentación técnica en PDF | `docs/` |
| 3 | Logs de ejecución | `sistema/resultados/` |

De ahí salieron tres notas que en realidad son una: **qué viaja en el ZIP.**

## Problema

La nota 8 pedía sacar `docs/` fuera del proyecto. El objetivo es correcto —los ADR no son
código fuente— pero la ejecución literal rompe algo medido:

```text
sistema/reloj.h                       4 menciones a ADR-0xx
sistema/clasificador.h                4
sistema/memoria-compartida-c/server.c 4
verificar.py                          8
sistema/analyze.py    imprime "Ver docs/ADR/ADR-005" al negarse a mezclar plataformas
```

más los enlaces relativos de los tres README. Si `docs/` se muda, **el ZIP entregado queda
lleno de punteros hacia documentos que el evaluador no recibió**.

La nota 11 («revisar resultados y pulirlo o removerlo») choca de frente con ADR-005:
`resultados/` es la evidencia del informe y el `.log` hermano es lo único que dice en qué
máquina se tomó cada corrida. «Removerlo» destruiría la cadena que ese ADR protege.

## Decisión

**Se separa DÓNDE VIVE de QUÉ SE EMPAQUETA.** Nada se muda fuera del repositorio y nada se
borra; lo que se crea es una regla de empaquetado ejecutable: `hacer-zip.sh`.

1. **`docs/` se queda** en el repositorio. Es de donde sale el PDF del entregable 2, y las
   referencias del código siguen resolviendo para quien trabaja en el árbol.
2. **`hacer-zip.sh` arma el entregable 1** por **lista blanca**: copia `app/`, `contrato/`,
   `sistema/`, los lanzadores y `verificar.py`, y poda `sistema/resultados/`, los binarios
   compilados y los `__pycache__`. Lo que no esté nombrado, no viaja — más seguro que una
   lista negra, donde un archivo nuevo se cuela solo.
3. **El ZIP lleva un `LEEME-ENTREGABLE.txt`** que dice dónde están los ADR que el código
   cita. Ése es el hueco que la mudanza habría dejado abierto y que la regla cierra.
4. **Nada de `resultados/` se borra.** Lo que la nota 11 pedía de verdad es que no viajen
   143 MB en el ZIP, y eso ya lo resuelve el punto 2. Lo que sí faltaba era **rotular**:
   `sistema/resultados/LEEME.md` declara cuál es la corrida oficial (17/09) y cuáles son
   histórico, para que nadie cite la equivocada.
5. **Las figuras se mueven a `docs/graficas/`** (nota 7). Son producto del análisis, no
   parte del sistema; `graficas.py` —que sí es código— se queda en `sistema/`.

## Consecuencias

- El ZIP pesa **124 KB y trae 45 archivos**, contra los ~143 MB del árbol completo.
- **Se verificó desempaquetándolo**, no sólo listándolo: compila el C, `verificar.py`
  pasa y una medición corta corre de punta a punta dando mediana 0,079 µs, coherente con
  los 83 ns del informe. Un ZIP que no compila es un entregable roto y eso sólo se sabe
  probándolo.
- `hacer-zip.sh` **falla con código 2** si detecta `docs/`, `resultados/` o `__pycache__`
  dentro del paquete. La regla se comprueba sola en cada corrida.
- El ZIP generado no se versiona: es un artefacto reproducible desde el árbol.

### Acciones derivadas

- [ ] Correr `./hacer-zip.sh` contra la versión final y dejar el resultado en
      `Modulo 1/Entregables/`, que **sigue vacío**.
- [ ] Elegir qué logs van en el entregable 3 — la recomendación son los seis del 17/09.
