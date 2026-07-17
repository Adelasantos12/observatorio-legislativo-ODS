"""Importa la semilla de minutas de la Cámara de Diputados en Mongo (fase H, B).

Lee `normtrace/03_tables/legislative_mapping/minutas_ods.csv` y hace upsert en la
colección `minutas`, con id = clave.

La semilla documenta la aportación del **Ejecutivo Federal** (subconjunto real de
iniciativas del Ejecutivo aprobadas, con su origen de autoría inequívoco). Las
minutas de origen en grupos parlamentarios se documentan después vía el scraper
del iniclave y el parseo de dictámenes; hasta entonces aparecen como
"por documentar". El CSV es editable: la autora puede corregir origen y
codificación por clave.

Uso:
    python knowledgebase/load_minutas.py [ruta_al_csv]
"""

import csv
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from pymongo import MongoClient

HERE = Path(__file__).parent
ROOT = HERE.parent
CSV_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    ROOT / "normtrace/03_tables/legislative_mapping/minutas_ods.csv"
)
SEED_CORTE = "2026-07-17"

host = os.environ.get("MONGO_HOST", "localhost")
port = int(os.environ.get("MONGO_PORT", "27017"))
db_name = os.environ.get("MONGO_DB_NAME", os.environ.get("MONGO_DB", "mx"))
user = os.environ.get("MONGO_USER")
password = os.environ.get("MONGO_PASSWORD")


def _split(value):
    return [p.strip() for p in re.split(r"[;,]", value or "") if p.strip()]


def _int(value):
    value = (value or "").strip()
    return int(value) if value.isdigit() else None


def build_doc(row):
    return {
        "_id": row["clave"],
        "clave": row["clave"],
        "legislatura": row.get("legislatura") or None,
        "anio": row.get("anio") or None,
        "periodo": row.get("periodo") or None,
        "numero": _int(row.get("numero")),
        "denominacion": row.get("denominacion") or None,
        "fecha_presentacion": row.get("fecha_presentacion") or None,
        "fecha_aprobacion": row.get("fecha_aprobacion") or None,
        "origen": (row.get("origen") or "").strip() or None,
        "estatus": row.get("estatus") or None,
        "expediente_ref": (row.get("expediente_ref") or "").strip() or None,
        "ods_principal": (row.get("ods_principal") or "").strip() or None,
        "ods_secundarios": _split(row.get("ods_secundarios")),
        "tema": row.get("tema") or None,
        "confianza": (row.get("confianza") or "").strip() or "pendiente",
        "metas": _split(row.get("metas")),
        "updated_at": datetime.now(timezone.utc),
    }


def main():
    if user and password:
        client = MongoClient(host, port, username=user, password=password)
    else:
        client = MongoClient(host, port)
    col = client[db_name]["minutas"]

    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    for row in rows:
        doc = build_doc(row)
        col.replace_one({"_id": doc["_id"]}, doc, upsert=True)

    client[db_name]["huella_meta"].replace_one(
        {"_id": "minutas"}, {"_id": "minutas", "corte": SEED_CORTE}, upsert=True)

    print(f"Importadas {len(rows)} minutas en '{db_name}.minutas'.")
    print(f"Corte: {SEED_CORTE}. Total en colección: {col.count_documents({})}")


if __name__ == "__main__":
    main()
