"""Agregados de la Huella del Ejecutivo (fase H, módulo A).

Funciones puras sobre listas de iniciativas (dicts), para poder verificarlas
contra el CSV semilla sin Mongo. El endpoint las alimenta con el repositorio.
"""

import re
from collections import Counter


def parse_list(value):
    """Normaliza 'ods_secundarios'/'metas' del CSV a lista de strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [p.strip() for p in re.split(r"[;,]", str(value)) if p.strip()]


def _quarter(fecha):
    """'08/10/2024' -> '2024-T4'. None si no parsea."""
    if not fecha:
        return None
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", str(fecha))
    if not m:
        return None
    month = int(m.group(2))
    year = m.group(3)
    return f"{year}-T{(month - 1) // 3 + 1}"


def aggregate_executive(inits, corte=None):
    """Devuelve {kpis, por_ods, por_meta, por_trimestre, corte}.

    `inits`: lista de dicts con seccion, denominacion, fecha_presentacion,
    ods_principal (str|None), ods_secundarios (list), metas (list).
    """
    total = len(inits)
    aprobadas = [d for d in inits if (d.get("seccion") or "").startswith("Aprobadas")]
    con_ods = [d for d in aprobadas if d.get("ods_principal")]
    pct_ods = round(len(con_ods) / len(aprobadas) * 100) if aprobadas else 0
    leyes_nuevas = sum(
        1 for d in aprobadas
        if re.search(r"expide", (d.get("denominacion") or "")[:60], re.IGNORECASE)
    )

    principal, secundario = Counter(), Counter()
    for d in inits:
        if d.get("ods_principal"):
            principal[str(d["ods_principal"])] += 1
        for s in parse_list(d.get("ods_secundarios")):
            secundario[str(s)] += 1
    ods_keys = sorted(set(list(principal) + list(secundario)), key=lambda x: int(x))
    por_ods = [
        {"ods": o, "principal": principal.get(o, 0), "secundario": secundario.get(o, 0)}
        for o in ods_keys
    ]
    ods_dominante = max(ods_keys, key=lambda o: principal[o] + secundario[o]) if ods_keys else None

    meta_c = Counter()
    for d in inits:
        for m in parse_list(d.get("metas")):
            meta_c[m] += 1
    por_meta = [{"meta": m, "n": n} for m, n in meta_c.most_common()]

    tri = Counter()
    for d in inits:
        q = _quarter(d.get("fecha_presentacion"))
        if q:
            tri[q] += 1
    por_trimestre = [{"periodo": p, "n": tri[p]} for p in sorted(tri)]

    return {
        "kpis": {
            "iniciativas_presentadas": total,
            "aprobadas": len(aprobadas),
            "pct_con_correspondencia_ods": pct_ods,
            "leyes_nuevas": leyes_nuevas,
            "ods_dominante": ods_dominante,
        },
        "por_ods": por_ods,
        "por_meta": por_meta,
        "por_trimestre": por_trimestre,
        "corte": corte,
    }


def initiative_to_dict(model):
    """ExecutiveInitiative -> dict para la respuesta/agregación."""
    return {
        "id": model.id,
        "seccion": model.seccion,
        "num": model.num,
        "denominacion": model.denominacion,
        "fecha_presentacion": model.fecha_presentacion,
        "fecha_dof": model.fecha_dof,
        "estatus": model.estatus,
        "ods_principal": model.ods_principal,
        "ods_secundarios": model.ods_secundarios,
        "tema": model.tema,
        "confianza": model.confianza,
        "metas": model.metas,
    }
