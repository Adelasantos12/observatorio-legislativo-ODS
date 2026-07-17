"""Endpoints de la Huella del Ejecutivo (fase H, módulo A).

Iniciativas del Ejecutivo Federal codificadas por ODS y metas. La codificación es
preliminar y revisable (protocolo NormTrace): cada iniciativa lleva `confianza`;
las no codificadas aparecen como pendientes, nunca ocultas.
"""

import logging
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


@router.get("/ejecutivo")
def ejecutivo_resumen():
    """KPIs y agregados por ODS, meta y trimestre de la Huella del Ejecutivo."""
    cached = cache.get(_CACHE_KEY)
    if cached is not None:
        return cached
    inits = [initiative_to_dict(i) for i in ExecutiveInitiatives.get_all()]
    corte = ExecutiveInitiatives.get_corte()
    result = aggregate_executive(inits, corte=corte)
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
