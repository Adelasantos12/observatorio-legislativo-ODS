"""Carga TODOS los seeds del portal en Mongo, en orden e idempotente (upserts).

Un solo comando para dejar la base lista tras el primer deploy:

    python /app/knowledgebase/load_all.py

Ejecuta, con las mismas variables de entorno (MONGO_*):
  1. Diccionario ODS mexicano (kb "mx")           -> load_kb.py
  2. Marco RSI mexicano (kb "rsi_mx")             -> load_kb.py <seed rsi>
  3. Iniciativas del Ejecutivo (Huella, módulo A) -> load_executive.py
  4. Minutas de la Cámara (Huella, módulo B)       -> load_minutas.py

Todos los pasos son upserts: volver a correrlo no duplica ni pisa la
codificación (los repos usan `upsert_preserving_coding`). Si un paso falla,
se reporta y se continúa con los demás; el código de salida es distinto de cero
si alguno falló, para que el deploy lo note.
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RSI_SEED = HERE / "seeds" / "rsi_mx.seed.json"

PASOS = [
    ("Diccionario ODS mexicano (kb 'mx')", [sys.executable, str(HERE / "load_kb.py")]),
    ("Marco RSI mexicano (kb 'rsi_mx')", [sys.executable, str(HERE / "load_kb.py"), str(RSI_SEED)]),
    ("Iniciativas del Ejecutivo (Huella A)", [sys.executable, str(HERE / "load_executive.py")]),
    ("Minutas de la Cámara (Huella B)", [sys.executable, str(HERE / "load_minutas.py")]),
]


def main():
    fallos = []
    for nombre, cmd in PASOS:
        print(f"\n=== {nombre} ===", flush=True)
        # El marco RSI es opcional: si falta el seed, se omite sin marcar fallo.
        if "rsi_mx.seed.json" in cmd[-1] and not RSI_SEED.is_file():
            print(f"(omitido: no existe {RSI_SEED})")
            continue
        res = subprocess.run(cmd)
        if res.returncode != 0:
            fallos.append(nombre)
            print(f"!! FALLÓ: {nombre} (código {res.returncode})", flush=True)

    print("\n=== Resumen de carga ===")
    if fallos:
        print("Con errores en:", ", ".join(fallos))
        sys.exit(1)
    print("Todos los seeds cargados correctamente.")


if __name__ == "__main__":
    main()
