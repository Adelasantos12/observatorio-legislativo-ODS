"""Repositorio de minutas de la Cámara de Diputados (Huella 2030, módulo B)."""

import re

from tipi_data import DoesNotExist, db
from tipi_data.models.minuta import Minuta


# Campos de codificación que el scraper NO debe pisar en un upsert.
CODING_FIELDS = ("ods_principal", "ods_secundarios", "metas", "tema", "confianza")

# La atribución de origen y el nivel de revisión tampoco se pisan una vez
# documentados: el scraper aporta fuente, no codificación ni atribución.
PRESERVE_FIELDS = CODING_FIELDS + (
    "origen", "origen_tipo", "grupos_parlamentarios", "nivel_revision",
)


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
    def upsert_coding_unless_validated(minuta: Minuta):
        """Upsert de codificación/atribución que respeta la revisión de la autora.

        Si el documento existente ya está `validado_autora`, se conserva TAL CUAL
        (la edición a mano de `minutas_ods.csv` es fuente de verdad). En cualquier
        otro caso se actualiza con la codificación entrante, conservando los
        campos de fuente (título, fechas, estatus, pdfs) del documento existente.
        """
        existing = db.minutas.find_one({"_id": minuta.id})
        if existing and existing.get("nivel_revision") == "validado_autora":
            return None  # intocable
        data = minuta.to_bson()
        if existing:
            for f in ("legislatura", "anio", "periodo", "numero", "denominacion",
                      "fecha_aprobacion", "observaciones", "estatus", "pdfs",
                      "fecha_presentacion"):
                if f in existing and f not in data:
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
    def search(ods=None, meta=None, origen=None, q=None, estatus=None, anio=None, tema=None):
        query = {}
        if ods:
            query["$or"] = [{"ods_principal": str(ods)}, {"ods_secundarios": str(ods)}]
        if meta:
            query["metas"] = meta
        if origen:
            query["$or"] = query.get("$or", []) + [
                {"origen": origen}, {"grupos_parlamentarios": origen}]
        if estatus:
            query["estatus"] = estatus
        if anio:
            query["anio"] = anio
        if tema:
            query["tema"] = re.compile(re.escape(tema), re.IGNORECASE)
        if q:
            query["denominacion"] = re.compile(re.escape(q), re.IGNORECASE)
        return [Minuta.model_validate(d) for d in db.minutas.find(query).sort("numero", 1)]
