"""Repositorio de minutas de la Cámara de Diputados (Huella 2030, módulo B)."""

import re

from tipi_data import DoesNotExist, db
from tipi_data.models.minuta import Minuta


# Campos de codificación que el scraper NO debe pisar en un upsert.
CODING_FIELDS = ("ods_principal", "ods_secundarios", "metas", "tema", "confianza")

# La atribución de origen tampoco se pisa una vez documentada por la autora:
# el scraper puede proponerla, pero un valor ya asentado manda.
PRESERVE_FIELDS = CODING_FIELDS + ("origen",)


class Minutas:
    @staticmethod
    def get(id):
        doc = db.minutas.find_one({"_id": id})
        if doc is None:
            raise DoesNotExist(f"Minuta {id} does not exist")
        return Minuta.model_validate(doc)

    @staticmethod
    def get_all():
        return [Minuta.model_validate(d) for d in db.minutas.find().sort("numero", 1)]

    @staticmethod
    def save(minuta: Minuta):
        return db.minutas.replace_one({"_id": minuta.id}, minuta.to_bson(), upsert=True)

    @staticmethod
    def upsert_preserving_coding(minuta: Minuta):
        """Upsert que conserva codificación y origen ya documentados.

        El scraper del iniclave solo aporta datos de fuente (denominación,
        fechas, estatus). La codificación ODS/metas y la atribución de origen
        —trabajo de la autora— se preservan si ya existen.
        """
        existing = db.minutas.find_one({"_id": minuta.id})
        data = minuta.to_bson()
        if existing:
            for f in PRESERVE_FIELDS:
                if f in existing:
                    data[f] = existing[f]
        return db.minutas.replace_one({"_id": minuta.id}, data, upsert=True)

    @staticmethod
    def get_corte():
        doc = db.huella_meta.find_one({"_id": "minutas"})
        return doc.get("corte") if doc else None

    @staticmethod
    def set_corte(corte):
        db.huella_meta.replace_one(
            {"_id": "minutas"}, {"_id": "minutas", "corte": corte}, upsert=True)

    @staticmethod
    def search(ods=None, meta=None, origen=None, q=None):
        query = {}
        if ods:
            query["$or"] = [{"ods_principal": str(ods)}, {"ods_secundarios": str(ods)}]
        if meta:
            query["metas"] = meta
        if origen:
            query["origen"] = origen
        if q:
            query["denominacion"] = re.compile(re.escape(q), re.IGNORECASE)
        return [Minuta.model_validate(d) for d in db.minutas.find(query).sort("numero", 1)]
