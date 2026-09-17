# ADR — dónde va cada decisión

Un ADR **viaja con lo que documenta**. Esa es toda la regla.

| Si la decisión es… | Va en… | Ejemplo |
|---|---|---|
| de un **ejercicio o proyecto** concreto | el `docs/ADR/` de ese ejercicio | la frontera de medición del reto de latencia |
| **transversal** al diplomado | aquí, en `_Base-Conocimiento/ADR/` | cómo versionamos · qué se considera evidencia |
| la **plantilla** | aquí: `ADR-000-plantilla.md` | se copia, no se edita |

## Qué hay aquí hoy

Solo `ADR-000-plantilla.md`. Todavía no ha habido ninguna decisión transversal al
diplomado: las siete que existen son del Reto de Latencia Mínima y viven con él.

## Los ADR del Reto de Latencia Mínima (Módulo 1)

```text
Modulo 1/Ejercicios/Reto-Latencia-Minima/reto-latencia-group2/docs/ADR/
```

| | Decide |
|---|---|
| `ADR-001` | frontera de medición — dónde se ponen las sondas (F1) |
| `ADR-002` | variante D — memoria compartida: mecanismo, lenguaje, planificación |
| `ADR-003` | resolución del reloj — granularidad ≠ unidades |
| `ADR-004` | dominio del reto — listas de hosts en vez de eco puro |
| `ADR-005` | comparabilidad entre máquinas — no mezclar corridas de equipos distintos |
| `ADR-006` | concurrencia — un hilo por conexión, y por qué D no puede tenerla |
| `ADR-007` | reducción de alcance a las variantes B y D |

## Por qué se borró la copia que había aquí

Hasta el 16/09 esta carpeta tenía una copia de los ADR 001 a 004. **Ya había
divergido**: los 005, 006 y 007 nunca llegaron a copiarse. Quien leyera esta carpeta
creyéndola completa habría concluido que el alcance del reto seguía siendo de seis
variantes, y se habría equivocado.

Una copia que se queda atrás es peor que no tener copia, porque **parece autoridad**.
Se borró la copia, no el contenido: los originales están íntegros en el proyecto y
el historial de git conserva todo.

## Cómo se listan en el índice

`generar-indice.py` recoge los ADR **de los dos sitios** —esta carpeta y el `docs/ADR/`
de cada ejercicio— para que el índice del diplomado los muestre todos sin que haya que
duplicar ni un archivo.
