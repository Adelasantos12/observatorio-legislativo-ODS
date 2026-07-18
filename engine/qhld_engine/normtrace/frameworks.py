"""Marcos de estándares para el mapeo NormTrace.

Un marco es el conjunto de estándares (metas ODS + bloques de obligación de
tratado) que una corrida debe cubrir. Para el ODS 6 se toman las 8 metas del
catálogo y los bloques de la Observación General 15 (derecho humano al agua) y
del PIDESC presentes en el ejemplo dorado. La cobertura (umbral 2 de la
evaluación) se mide contra esta lista canónica.
"""

# Las 8 metas del ODS 6 (identificadores del catálogo de metas).
ODS6_METAS = ["6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.a", "6.b"]

# Bloques de estándar convencional presentes en el dorado (además de las metas).
ODS6_BLOQUES_TRATADO = [
    "OG 15 / DH agua: elementos normativos",
    "OG 15: no discriminacion y grupos",
    "OG 15: igualdad de genero",
    "OG 15: interdependencia salud",
    "OG 15: exigibilidad y reparacion",
    "Progresividad presupuestal (art. 2.1 PIDESC)",
    "Cadena federal: armonizacion estatal",
]


def meta_key(estandar: str) -> str:
    """Normaliza un `estandar` a su clave de meta ('ODS 6.1 ...' -> '6.1').

    Los bloques de tratado se devuelven tal cual (no son metas numéricas).
    """
    e = (estandar or "").strip()
    if e.upper().startswith("ODS"):
        # 'ODS 6.1 Acceso...' -> '6.1'
        parts = e.split()
        if len(parts) >= 2:
            return parts[1]
    return e


ODS6_STANDARDS = ODS6_METAS + ODS6_BLOQUES_TRATADO

MARCOS = {
    "ods6": {
        "nombre": "ODS 6 — Agua limpia y saneamiento + derecho humano al agua",
        "metas": ODS6_METAS,
        "bloques": ODS6_BLOQUES_TRATADO,
        "standards": ODS6_STANDARDS,
        # Ley vitrina del marco y su fuente de texto.
        "ley": "Ley General de Aguas",
        "fuente_texto": "LeyesBiblio — Ley General de Aguas, DOF 11-12-2025",
        "leyesbiblio_slug": "LGAg",
    }
}


def get_marco(nombre: str) -> dict:
    if nombre not in MARCOS:
        raise ValueError(f"Marco NormTrace desconocido: {nombre!r}. Disponibles: {list(MARCOS)}")
    return MARCOS[nombre]


def cobertura_estandares(registros: list[dict], marco: str) -> tuple[set, set]:
    """Devuelve (cubiertos, faltantes) de los estándares del marco en `registros`."""
    m = get_marco(marco)
    objetivo = set()
    for meta in m["metas"]:
        objetivo.add(meta)
    for bloque in m["bloques"]:
        objetivo.add(bloque)
    presentes = set()
    for r in registros:
        k = meta_key(r.get("estandar", ""))
        if k in objetivo:
            presentes.add(k)
        elif r.get("estandar", "").strip() in objetivo:
            presentes.add(r.get("estandar", "").strip())
    faltantes = objetivo - presentes
    return presentes, faltantes
