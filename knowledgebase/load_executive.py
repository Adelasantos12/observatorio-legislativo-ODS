"""Importa la semilla de iniciativas del Ejecutivo Federal en Mongo (fase H).

Lee `normtrace/03_tables/legislative_mapping/iniciativas_ejecutivo_ods.csv` y hace
upsert en la colección `executive_initiatives`, con id estable
`EJE-2024-2030-{num}-{seccion_slug}`. Marca la fecha de corte de la semilla.

Uso:
    python knowledgebase/load_executive.py [ruta_al_csv]
"""

import csv
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from pymongo import MongoClient
from tipi_data.utils import generate_slug

HERE = Path(__file__).parent
ROOT = HERE.parent
CSV_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    ROOT / "normtrace/03_tables/legislative_mapping/iniciativas_ejecutivo_ods.csv"
)
SEED_CORTE = "2026-07-17"  # corte de la semilla (17/jul/2026)

host = os.environ.get("MONGO_HOST", "localhost")
port = int(os.environ.get("MONGO_PORT", "27017"))
db_name = os.environ.get("MONGO_DB_NAME", os.environ.get("MONGO_DB", "mx"))
user = os.environ.get("MONGO_USER")
password = os.environ.get("MONGO_PASSWORD")


def _split(value):
    return [p.strip() for p in re.split(r"[;,]", value or "") if p.strip()]


def build_doc(row):
    seccion = row["seccion"]
    num = int(row["num"])
    return {
        "_id": f"EJE-2024-2030-{num}-{generate_slug(seccion)}",
        "seccion": seccion,
        "num": num,
        "denominacion": row["denominacion"],
        "fecha_presentacion": row["fecha_presentacion"] or None,
        "fecha_dof": row["fecha_dof"] or None,
        "estatus": row["estatus"] or None,
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
    col = client[db_name]["executive_initiatives"]

    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    for row in rows:
        doc = build_doc(row)
        col.replace_one({"_id": doc["_id"]}, doc, upsert=True)

    client[db_name]["huella_meta"].replace_one(
        {"_id": "ejecutivo"}, {"_id": "ejecutivo", "corte": SEED_CORTE}, upsert=True)

    print(f"Importadas {len(rows)} iniciativas del Ejecutivo en '{db_name}.executive_initiatives'.")
    print(f"Corte: {SEED_CORTE}. Total en colección: {col.count_documents({})}")


if __name__ == "__main__":
    main()
