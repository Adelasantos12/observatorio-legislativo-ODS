"""Endpoints de minutas de la Cámara de Diputados (fase H, módulo B).

Aportación por origen a la Agenda 2030. La atribución de origen y la codificación
ODS son preliminares y revisables; las minutas sin origen documentado aparecen
como "por documentar", nunca ocultas ni inventadas. El desglose por origen es
descriptivo, no un ranking competitivo entre bancadas.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from tipi_data.repositories.minutas import Minutas
from tipi_backend.api import cache
from tipi_backend.api.minutas import aggregate_minutas, minuta_to_dict

log = logging.getLogger(__name__)

router = APIRouter(prefix="/minutas", tags=["minutas"])

_CACHE_KEY = "minutas_agg"


@router.get("/")
def minutas_resumen():
    """KPIs y agregados por origen, ODS y meta de las minutas de la Cámara."""
    cached = cache.get(_CACHE_KEY)
    if cached is not None:
        return cached
    minutas = [minuta_to_dict(m) for m in Minutas.get_all()]
    corte = Minutas.get_corte()
    result = aggregate_minutas(minutas, corte=corte)
    cache.set(_CACHE_KEY, result, timeout=60 * 60)  # 1 h
    return result


@router.get("/lista")
def minutas_lista(
    ods: Annotated[str | None, Query()] = None,
    meta: Annotated[str | None, Query()] = None,
    origen: Annotated[str | None, Query()] = None,
    q: Annotated[str | None, Query()] = None,
):
    """Lista filtrable de minutas."""
    minutas = Minutas.search(ods=ods, meta=meta, origen=origen, q=q)
    return [minuta_to_dict(m) for m in minutas]


@router.get("/{id}")
def minuta_detalle(id: str):
    """Ficha de una minuta."""
    try:
        return minuta_to_dict(Minutas.get(id))
    except Exception as e:
        log.error(e)
        return JSONResponse(status_code=404, content={"Error": "No minuta found"})
