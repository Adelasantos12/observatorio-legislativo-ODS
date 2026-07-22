"""Repositorio de iniciativas del Ejecutivo Federal (Huella 2030, fase H)."""

import re

from tipi_data import DoesNotExist, db
from tipi_data.models.executive_initiative import ExecutiveInitiative


# Campos de codificación que el scraper NO debe pisar en un upsert.
CODING_FIELDS = ("ods_principal", "ods_secundarios", "metas", "tema", "confianza")


class ExecutiveInitiatives:
    @staticmethod
    def get(id):
        doc = db.executive_initiatives.find_one({"_id": id})
        if doc is None:
            raise DoesNotExist(f"ExecutiveInitiative {id} does not exist")
        return ExecutiveInitiative.model_validate(doc)

    @staticmethod
    def get_all():
        return [ExecutiveInitiative.model_validate(d)
                for d in db.executive_initiatives.find().sort("num", 1)]

    @staticmethod
    def save(initiative: ExecutiveInitiative):
        return db.executive_initiatives.replace_one(
            {"_id": initiative.id}, initiative.to_bson(), upsert=True)

    @staticmethod
    def upsert_preserving_coding(initiative: ExecutiveInitiative):
        """Upsert por _id que NO sobreescribe la codificación existente.

        Si ya existe el documento, conserva sus campos de codificación
        (`ods_*`, `metas`, `tema`, `confianza`) y solo actualiza los campos de
        fuente (denominación, fechas, estatus…). Así el scraper del SIL no borra
        el trabajo de codificación de la autora.
        """
        existing = db.executive_initiatives.find_one({"_id": initiative.id})
        data = initiative.to_bson()
        if existing:
            for f in CODING_FIELDS:
                if f in existing:
                    data[f] = existing[f]
        return db.executive_initiatives.replace_one({"_id": initiative.id}, data, upsert=True)

    @staticmethod
    def get_corte():
        """Fecha de corte del último éxito de sincronización (o None)."""
        doc = db.huella_meta.find_one({"_id": "ejecutivo"})
        return doc.get("corte") if doc else None

    @staticmethod
    def set_corte(corte):
        db.huella_meta.replace_one(
            {"_id": "ejecutivo"}, {"_id": "ejecutivo", "corte": corte}, upsert=True)

    @staticmethod
    def search(ods=None, meta=None, seccion=None, q=None):
        query = {}
        if ods:
            query["$or"] = [{"ods_principal": str(ods)}, {"ods_secundarios": str(ods)}]
        if meta:
            query["metas"] = meta
        if seccion:
            query["seccion"] = seccion
        if q:
            query["denominacion"] = re.compile(re.escape(q), re.IGNORECASE)
        return [ExecutiveInitiative.model_validate(d)
                for d in db.executive_initiatives.find(query).sort("num", 1)]
