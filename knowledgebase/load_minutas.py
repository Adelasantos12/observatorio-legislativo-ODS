"""Importa las minutas de la LXVI en Mongo (Huella módulo B, adenda v3).

Fusiona dos archivos y hace upsert en la colección `minutas` (id = clave):
  1. `minutas_lxvi_raw.csv` — 139 minutas reales del iniclave (fuente: título,
     fechas, observaciones, estatus, pdfs).
  2. `minutas_ods.csv` — codificación ODS/metas + atribución (editable a mano;
     fuente de verdad de la codificación).

Regla no negociable: NUNCA pisa la codificación de una minuta cuyo documento en
Mongo ya esté `nivel_revision = validado_autora` (la revisión de la autora manda).
Idempotente (upserts).

Uso:
    python knowledgebase/load_minutas.py
"""

import csv
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
MAP_DIR = ROOT / "normtrace/03_tables/legislative_mapping"
RAW_CSV = Path(sys.argv[1]) if len(sys.argv) > 1 else MAP_DIR / "minutas_lxvi_raw.csv"
CODING_CSV = MAP_DIR / "minutas_ods.csv"
# Atribución de grupo parlamentario obtenida por OCR de los dictámenes (clave,grupos).
# Producida fuera de línea (el sitio de la Cámara bloquea IPs de datacenter) y horneada
# como dato; la columna `grupos` puede venir vacía = "por documentar" (nunca se inventa).
ATRIB_CSV = MAP_DIR / "minutas_atribucion.csv"
SEED_CORTE = "2026-07-21"

host = os.environ.get("MONGO_HOST", "localhost")
port = int(os.environ.get("MONGO_PORT", "27017"))
db_name = os.environ.get("MONGO_DB_NAME", os.environ.get("MONGO_DB", "mx"))
user = os.environ.get("MONGO_USER")
password = os.environ.get("MONGO_PASSWORD")


def _split(v):
    return [p.strip() for p in re.split(r"[;,]", v or "") if p.strip()]


def _pdfs(v):
    return [p.strip() for p in (v or "").split(";") if p.strip()]


def _parse_clave(clave):
    parts = clave.split("-")
    leg = parts[1] if len(parts) > 1 else None
    anio = parts[2] if len(parts) > 2 else None
    periodo = parts[3] if len(parts) > 3 else None
    num = None
    if parts:
        m = re.search(r"\d+", parts[-1])
        num = int(m.group(0)) if m else None
    return leg, anio, periodo, num


def load_coding(path):
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        return {r["clave"].strip(): r for r in csv.DictReader(fh)}


def load_atribucion(path):
    """Mapa clave -> [grupos] desde el CSV de atribución por OCR. Solo entradas
    con grupo (las vacías = 'por documentar' no aportan y se ignoran)."""
    if not path.is_file():
        return {}
    out = {}
    with path.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            grupos = _split(r.get("grupos"))
            if grupos:
                out[r["clave"].strip()] = grupos
    return out


def build_doc(raw, coding, atribucion=None):
    clave = raw["clave"].strip()
    leg, anio, periodo, num = _parse_clave(clave)
    c = coding.get(clave, {})
    # La atribución por OCR del dictamen es la fuente para el grupo parlamentario de
    # las minutas de origen legislativo; si existe, manda sobre la del CSV de coding.
    atribucion = atribucion or {}
    grupos_ocr = atribucion.get(clave)
    origen_tipo = (c.get("origen_tipo") or "").strip() or None
    if grupos_ocr and origen_tipo != "ejecutivo":
        grupos = grupos_ocr
        origen_tipo = "legislativo"
    else:
        grupos = _split(c.get("grupos_parlamentarios"))
    return {
        "_id": clave,
        "clave": clave,
        "legislatura": leg,
        "anio": raw.get("anio") or anio,
        "periodo": periodo,
        "numero": num,
        "denominacion": (raw.get("titulo") or "").strip() or None,
        "fecha_aprobacion": (raw.get("fecha_aprobacion") or "").strip() or None,
        "observaciones": (raw.get("observaciones") or "").strip() or None,
        "estatus": (raw.get("estatus") or "").strip() or None,
        "pdfs": _pdfs(raw.get("pdfs")),
        "ods_principal": (c.get("ods_principal") or "").strip() or None,
        "ods_secundarios": _split(c.get("ods_secundarios")),
        "metas": _split(c.get("metas")),
        "tema": (c.get("tema") or "").strip() or None,
        "confianza": (c.get("confianza") or "").strip() or "pendiente",
        "origen_tipo": origen_tipo,
        "origen": "Ejecutivo Federal" if origen_tipo == "ejecutivo" else (
            "Cámara de Diputados" if origen_tipo == "legislativo" else None),
        "grupos_parlamentarios": grupos,
        "expediente_ref": (c.get("expediente_ref") or "").strip() or None,
        "nivel_revision": (c.get("nivel_revision") or "").strip() or "automatico_preliminar",
        "updated_at": datetime.now(timezone.utc),
    }


def main():
    from pymongo import MongoClient  # import perezoso: el módulo se puede probar sin Mongo
    if user and password:
        client = MongoClient(host, port, username=user, password=password)
    else:
        client = MongoClient(host, port)
    col = client[db_name]["minutas"]

    coding = load_coding(CODING_CSV)
    atribucion = load_atribucion(ATRIB_CSV)
    raws = list(csv.DictReader(RAW_CSV.open(encoding="utf-8")))
    claves_actuales = {r["clave"].strip() for r in raws}

    # Limpia minutas superadas de siembras anteriores (p. ej. claves MIN-EJE-*
    # del esquema viejo) para que la colección converja a la fuente vigente. Nunca
    # borra una minuta validada por la autora.
    stale = col.delete_many({
        "_id": {"$nin": list(claves_actuales)},
        "nivel_revision": {"$ne": "validado_autora"},
    })
    if stale.deleted_count:
        print(f"Eliminadas {stale.deleted_count} minutas superadas de una siembra anterior.")

    preservadas = 0
    for raw in raws:
        doc = build_doc(raw, coding, atribucion)
        existing = col.find_one({"_id": doc["_id"]})
        if existing and existing.get("nivel_revision") == "validado_autora":
            # La codificación validada por la autora es intocable; solo
            # actualizamos los campos de fuente del iniclave.
            fuente = {k: doc[k] for k in ("denominacion", "fecha_aprobacion",
                      "observaciones", "estatus", "pdfs", "updated_at")}
            col.update_one({"_id": doc["_id"]}, {"$set": fuente})
            preservadas += 1
        else:
            col.replace_one({"_id": doc["_id"]}, doc, upsert=True)

    client[db_name]["huella_meta"].replace_one(
        {"_id": "minutas"}, {"_id": "minutas", "corte": SEED_CORTE}, upsert=True)

    print(f"Importadas {len(raws)} minutas en '{db_name}.minutas' "
          f"({preservadas} con codificación validada preservada).")
    if atribucion:
        con_grupo = col.count_documents({"grupos_parlamentarios.0": {"$exists": True}})
        print(f"Atribución de grupo parlamentario aplicada: {len(atribucion)} minutas de la "
              f"Cámara (total con grupo en colección: {con_grupo}).")
    print(f"Corte: {SEED_CORTE}. Total en colección: {col.count_documents({})}")


if __name__ == "__main__":
    main()
