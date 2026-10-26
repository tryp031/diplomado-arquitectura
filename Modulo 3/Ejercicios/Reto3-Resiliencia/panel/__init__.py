# src/ no es un paquete (en Lambda cada módulo se importa en el primer nivel). El panel usa la
# MISMA regla que el router (src/reglas.py) para predecir el nivel desde lo que ve el cliente.
import sys
from pathlib import Path

_SRC = str(Path(__file__).resolve().parents[1] / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
