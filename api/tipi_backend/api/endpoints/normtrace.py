"""Endpoints del Análisis NormTrace (nivel 3, adenda nivel 2).

Sirve la corrida validada del dorado (LGA × ODS 6) para la ficha vitrina y las
corridas automáticas preliminares que existan. Toda corrida lleva
`nivel_revision`; ninguna automática se presenta como validada.
"""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse

from tipi_data import db
from tipi_backend.api.normtrace import (
    LGA_EXPEDIENTE_ID,
    count_con_analisis,
    load_brief,
    run_for_expediente,
)

log = logging.getLogger(__name__)

router = APIRouter(prefix="/normtrace", tags=["normtrace"])


def _mongo_lookup(expediente_id):
    """Corrida automática preliminar guardada en Mongo, si existe."""
    try:
        return db.normtrace_runs.find_one({"_id": expediente_id})
    except Exception as e:  # colección inexistente o Mongo caído: sin análisis
        log.warning("normtrace_runs lookup falló: %s", e)
        return None


@router.get("/expediente/{id}")
def normtrace_expediente(id: str):
    """Análisis NormTrace de un expediente (dorado validado o preliminar)."""
    run = run_for_expediente(id, mongo_lookup=_mongo_lookup)
    if run is None:
        return JSONResponse(status_code=404, content={"Error": "Sin análisis NormTrace"})
    run.pop("_id", None)
    return run


@router.get("/brief/{nombre}")
def normtrace_brief(nombre: str):
    """Markdown del brief dorado (se renderiza en el frontend)."""
    md = load_brief(nombre)
    if md is None:
        return JSONResponse(status_code=404, content={"Error": "Brief no encontrado"})
    return PlainTextResponse(md, media_type="text/markdown")


@router.get("/kpi")
def normtrace_kpi():
    """Conteo de expedientes con análisis NormTrace (para el KPI del dashboard)."""
    def _count_runs():
        try:
            return db.normtrace_runs.count_documents({})
        except Exception:
            return 0

    return {"con_analisis": count_con_analisis(_count_runs), "vitrina": LGA_EXPEDIENTE_ID}
