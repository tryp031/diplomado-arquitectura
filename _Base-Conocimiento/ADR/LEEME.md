# ADR — dónde vive cada decisión

Esta carpeta contiene una **copia** de los ADR 000–004 del Reto de Latencia Mínima
(Módulo 1). Al 16/09/2026 esas copias son idénticas byte a byte a las del proyecto.

**La fuente de verdad es el proyecto**, no esta carpeta:

```text
Modulo 1/Ejercicios/Reto-Latencia-Minima/reto-latencia-group2/docs/ADR/
```

Ahí están los siete, incluidos los que **nunca se copiaron aquí**:

| ADR | Aquí | En el proyecto |
|---|---|---|
| 000 · plantilla | ✅ | ✅ |
| 001 · frontera de medición | ✅ | ✅ |
| 002 · variante D, memoria compartida | ✅ | ✅ |
| 003 · resolución del reloj | ✅ | ✅ |
| 004 · dominio, listas de hosts | ✅ | ✅ |
| 005 · comparabilidad entre máquinas | ❌ | ✅ |
| 006 · concurrencia y hilos | ❌ | ✅ |
| 007 · reducción de alcance a B y D | ❌ | ✅ |

## Por qué esto es un problema y no una comodidad

La copia **ya divergió**: tres decisiones existen solo en el proyecto. Quien lea esta
carpeta creyendo que está completa concluirá que el alcance sigue siendo de seis
variantes, y se equivocará. Una copia que se queda atrás es peor que no tener copia,
porque parece autoridad.

## Qué hacer con esto

Pendiente de decidir en la reunión del **21/09**. Las dos salidas razonables:

1. **Borrar esta copia** y reapuntar los enlaces (`CONTRIBUIR.md`, `Modulo 1/README.md`,
   `_Plantillas/LEEME.md`, `_Base-Conocimiento/generar-indice.py` y los documentos del
   reto) al `docs/ADR/` del proyecto. Es lo coherente con que los ADR viajen con la
   entrega que los produjo.
2. **Conservarla y sincronizarla**, aceptando el coste de mantener dos copias al día.

Mientras tanto: **no edites los ADR aquí.** Edítalos en el proyecto.
