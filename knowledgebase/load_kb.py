"""Carga un seed de diccionario (knowledgebase) en Mongo.

Uso:
    python knowledgebase/load_kb.py [ruta_al_seed.json]

Por defecto carga seeds/ods_mx.seed.json en la colección `topics`
de la base indicada por MONGO_HOST / MONGO_PORT / MONGO_DB.

Formato del seed: mismo que tipi (ver api/tests/fixtures/knowledgebase.json):
lista de topics {name, shortname, description, knowledgebase, public,
tags: [{tag, subtopic, regex, shuffle}]}.

Nota sobre el modelo: en qhld-data `Topic.description` es list[str];
este loader acepta string o lista y normaliza.
"""

import json
import os
import sys
from pathlib import Path

from pymongo import MongoClient

HERE = Path(__file__).parent
seed_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "seeds" / "ods_mx.seed.json"

host = os.environ.get("MONGO_HOST", "localhost")
port = int(os.environ.get("MONGO_PORT", "27017"))
db_name = os.environ.get("MONGO_DB", "mx")

topics = json.loads(seed_path.read_text(encoding="utf-8"))
client = MongoClient(host, port)
col = client[db_name]["topics"]

for t in topics:
    desc = t.get("description", [])
    if isinstance(desc, str):
        t["description"] = [desc]
    t.setdefault("public", True)
    res = col.replace_one(
        {"name": t["name"], "knowledgebase": t.get("knowledgebase", "mx")},
        t,
        upsert=True,
    )
    action = "actualizado" if res.matched_count else "insertado"
    print(f"{action}: {t['name']} ({len(t.get('tags', []))} tags)")

print(f"\nTotal en '{db_name}.topics': {col.count_documents({})}")
print("Recuerda: el tagger cachea los tags ~5 min (api/tipi_backend, get_tags).")
