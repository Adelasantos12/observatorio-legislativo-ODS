"""Endpoints de la Huella del Ejecutivo (fase H, módulo A).

Iniciativas del Ejecutivo Federal codificadas por ODS y metas. La codificación es
preliminar y revisable (protocolo NormTrace): cada iniciativa lleva `confianza`;
las no codificadas aparecen como pendientes, nunca ocultas.
"""

import json
import logging
import os
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from tipi_data.repositories.executive_initiatives import ExecutiveInitiatives
from tipi_backend.api import cache
from tipi_backend.api.huella import aggregate_executive, initiative_to_dict
from tipi_backend.settings import Config

log = logging.getLogger(__name__)

router = APIRouter(prefix="/huella", tags=["huella"])

_CACHE_KEY = "huella_ejecutivo_agg"


def _catalogos_dir():
    candidates = [
        os.environ.get("CATALOGOS_DIR"),
        "/app/normtrace/03_tables/catalogos",
        str(Path(__file__).resolve().parents[3] / "normtrace/03_tables/catalogos"),
    ]
    for c in candidates:
        if c and Path(c).is_dir():
            return Path(c)
    return None


@router.get("/catalogos")
def catalogos():
    """Catálogos ODS (nombre + color) y metas (código, ods, nombre corto/oficial)."""
    d = _catalogos_dir()
    if d is None:
        return JSONResponse(status_code=404, content={"Error": "Catálogos no disponibles"})
    ods = json.loads((d / "ods.json").read_text(encoding="utf-8"))
    metas = json.loads((d / "metas.json").read_text(encoding="utf-8"))
    return {"ods": ods, "metas": metas}


@router.get("/ejecutivo")
def ejecutivo_resumen():
    """KPIs y agregados por ODS, meta y trimestre de la Huella del Ejecutivo."""
    cached = cache.get(_CACHE_KEY)
    if cached is not None:
        return cached
    inits = [initiative_to_dict(i) for i in ExecutiveInitiatives.get_all()]
    corte = ExecutiveInitiatives.get_corte()
    result = aggregate_executive(inits, corte=corte)
    # KPI nivel 3: expedientes con análisis NormTrace (hoy: el dorado de la LGA).
    from tipi_backend.api.normtrace import LGA_EXPEDIENTE_ID, count_con_analisis

    def _count_runs():
        try:
            from tipi_data import db
            return db.normtrace_runs.count_documents({})
        except Exception:
            return 0

    result["kpis"]["iniciativas_con_normtrace"] = count_con_analisis(_count_runs)
    result["normtrace_vitrina"] = LGA_EXPEDIENTE_ID
    cache.set(_CACHE_KEY, result, timeout=60 * 60)  # 1 h
    return result


@router.get("/ejecutivo/iniciativas")
def ejecutivo_iniciativas(
    ods: Annotated[str | None, Query()] = None,
    meta: Annotated[str | None, Query()] = None,
    seccion: Annotated[str | None, Query()] = None,
    q: Annotated[str | None, Query()] = None,
):
    """Lista filtrable de iniciativas del Ejecutivo."""
    inits = ExecutiveInitiatives.search(ods=ods, meta=meta, seccion=seccion, q=q)
    return [initiative_to_dict(i) for i in inits]


@router.get("/ejecutivo/iniciativas/{id}")
def ejecutivo_iniciativa(id: str):
    """Ficha (expediente) de una iniciativa del Ejecutivo."""
    try:
        return initiative_to_dict(ExecutiveInitiatives.get(id))
    except Exception as e:
        log.error(e)
        return JSONResponse(status_code=404, content={"Error": "No initiative found"})
