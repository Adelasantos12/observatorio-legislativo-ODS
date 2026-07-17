"""Agregados de minutas de la Cámara de Diputados (fase H, módulo B).

Funciones puras sobre listas de minutas (dicts), verificables contra CSV sin
Mongo. El endpoint las alimenta con el repositorio.

REGLA NO NEGOCIABLE: el desglose por origen es una *aportación por origen*
—descriptiva, quién impulsó cada asunto— y NUNCA un ranking competitivo entre
bancadas. Las minutas sin origen documentado se agrupan como "por documentar"
(nunca se les inventa una bancada) y se reportan aparte para no distorsionar el
panorama. El orden de salida es alfabético por origen, no por volumen, para no
sugerir competencia.
"""

import re
from collections import Counter

from tipi_backend.api.huella import parse_list

# Etiqueta única para minutas cuyo origen aún no se documenta.
POR_DOCUMENTAR = "por documentar"


def aggregate_minutas(minutas, corte=None):
    """Devuelve {kpis, por_origen, por_ods, por_meta, corte}.

    `minutas`: lista de dicts con origen (str|None), ods_principal (str|None),
    ods_secundarios (list), metas (list).
    """
    total = len(minutas)
    con_ods = [m for m in minutas if m.get("ods_principal")]
    pct_ods = round(len(con_ods) / total * 100) if total else 0

    # Aportación por origen: descriptiva, no ranking. Orden alfabético estable.
    origen_c = Counter()
    sin_origen = 0
    for m in minutas:
        origen = (m.get("origen") or "").strip()
        if origen:
            origen_c[origen] += 1
        else:
            sin_origen += 1
    por_origen = [
        {"origen": o, "n": origen_c[o]}
        for o in sorted(origen_c, key=lambda s: s.lower())
    ]
    if sin_origen:
        por_origen.append({"origen": POR_DOCUMENTAR, "n": sin_origen, "por_documentar": True})

    principal, secundario = Counter(), Counter()
    for m in minutas:
        if m.get("ods_principal"):
            principal[str(m["ods_principal"])] += 1
        for s in parse_list(m.get("ods_secundarios")):
            secundario[str(s)] += 1
    ods_keys = sorted(set(list(principal) + list(secundario)), key=lambda x: int(x))
    por_ods = [
        {"ods": o, "principal": principal.get(o, 0), "secundario": secundario.get(o, 0)}
        for o in ods_keys
    ]

    meta_c = Counter()
    for m in minutas:
        for meta in parse_list(m.get("metas")):
            meta_c[meta] += 1
    por_meta = [{"meta": meta, "n": n} for meta, n in meta_c.most_common()]

    return {
        "kpis": {
            "minutas_totales": total,
            "con_correspondencia_ods": len(con_ods),
            "pct_con_correspondencia_ods": pct_ods,
            "origenes_documentados": len(por_origen) - (1 if sin_origen else 0),
            "sin_origen_documentado": sin_origen,
        },
        "por_origen": por_origen,
        "por_ods": por_ods,
        "por_meta": por_meta,
        "corte": corte,
    }


def minuta_to_dict(model):
    """Minuta -> dict para la respuesta/agregación."""
    return {
        "id": model.id,
        "clave": model.clave,
        "legislatura": model.legislatura,
        "anio": model.anio,
        "periodo": model.periodo,
        "numero": model.numero,
        "denominacion": model.denominacion,
        "fecha_presentacion": model.fecha_presentacion,
        "fecha_aprobacion": model.fecha_aprobacion,
        "origen": model.origen,
        "estatus": model.estatus,
        "expediente_ref": model.expediente_ref,
        "ods_principal": model.ods_principal,
        "ods_secundarios": model.ods_secundarios,
        "tema": model.tema,
        "confianza": model.confianza,
        "metas": model.metas,
    }
