"""Evaluación dorada: el candado de calidad de las corridas NormTrace.

Compara una corrida automática contra el ejemplo dorado y aplica los cinco
umbrales de la adenda (todos obligatorios):

1. Resolución de citas: 100%.
2. Cobertura de estándares: 100% (las 8 metas del ODS 6 + bloques de OG 15).
3. Acuerdo de rol (sustantivo vs contextual): ≥ 80%.
4. Acuerdo de cobertura: ≥ 70%, con juicios de ajuste a ≤ 1 escalón ordinal en
   ≥ 75% de los casos.
5. Sin falsos sustantivos graves: ningún registro que el dorado marca contextual
   sale "sustantivo + completa".

Los umbrales estructurales (1 y 2) se evalúan siempre sobre la corrida dada. Los
umbrales de acuerdo (3–5) requieren pares estándar↔disposición comparables con el
dorado; si la corrida no trae registros comparables (p. ej. no hubo corrida
automática por falta de proveedor LLM), se reportan como OMITIDOS, no como
aprobados.
"""

from . import citations, frameworks
from .gold import load_gold

# Orden ordinal de los fits para medir distancia (no_aplica queda fuera del orden).
_FIT_ORD = {"debil": 0, "medio": 1, "fuerte": 2}

# Umbrales.
T3_ROL = 0.80
T4_COBERTURA = 0.70
T4_ADYACENCIA = 0.75


def _key(row):
    """Clave de emparejamiento estándar↔disposición, normalizada."""
    est = frameworks.meta_key(row.get("estandar", ""))
    disp = (row.get("disposicion", "") or "").lower()
    # Normaliza 'Art. 7 fracc. I-VI' -> 'art 7' para emparejar por artículo.
    import re
    m = re.search(r"art[íi]?c?\.?\s*(\d{1,3})", disp)
    art = m.group(1) if m else disp.strip()
    return (est, art)


def _index_by_key(rows):
    idx = {}
    for r in rows:
        idx.setdefault(_key(r), []).append(r)
    return idx


def _fit_distance(a, b):
    """Distancia ordinal entre dos fits; None si alguno es no_aplica/desconocido."""
    if a not in _FIT_ORD or b not in _FIT_ORD:
        return None
    return abs(_FIT_ORD[a] - _FIT_ORD[b])


def evaluate(run: dict, gold: list | None = None, article_index=None) -> dict:
    """Evalúa una corrida contra el dorado. Devuelve un reporte por umbral."""
    gold = gold if gold is not None else load_gold()
    registros = run.get("registros", [])

    # --- Umbral 1: resolución de citas ---------------------------------------
    cit = citations.citation_resolution(registros, article_index)
    t1 = {
        "nombre": "Resolución de citas 100%",
        "obligatorio": True,
        "valor": cit["tasa"],
        "umbral": 1.0,
        "pasa": cit["tasa"] >= 1.0,
        "detalle": cit["no_resueltas"],
    }

    # --- Umbral 2: cobertura de estándares -----------------------------------
    _, faltantes = frameworks.cobertura_estandares(registros, run.get("marco", "ods6"))
    t2 = {
        "nombre": "Cobertura de estándares 100%",
        "obligatorio": True,
        "valor": 0.0 if faltantes else 1.0,
        "umbral": 1.0,
        "pasa": not faltantes,
        "detalle": sorted(faltantes),
    }

    # --- Umbrales 3–5: acuerdo con el dorado ---------------------------------
    gold_idx = _index_by_key(gold)
    pares = []  # (run_row, gold_row) emparejados por clave
    for r in registros:
        matches = gold_idx.get(_key(r))
        if matches:
            pares.append((r, matches[0]))

    comparables = len(pares)
    if comparables == 0:
        omitido = {
            "obligatorio": True, "pasa": None, "omitido": True,
            "detalle": "Sin registros comparables con el dorado (¿corrida automática ausente?).",
        }
        t3 = {"nombre": "Acuerdo de rol ≥ 80%", **omitido}
        t4 = {"nombre": "Acuerdo de cobertura ≥ 70% (adyacencia ≥ 75%)", **omitido}
        t5 = {"nombre": "Sin falsos sustantivos graves", **omitido}
    else:
        rol_ok = sum(
            1 for r, g in pares
            if r.get("rol_correspondencia") == g.get("rol_correspondencia")
        )
        t3_val = rol_ok / comparables
        t3 = {
            "nombre": "Acuerdo de rol ≥ 80%", "obligatorio": True,
            "valor": t3_val, "umbral": T3_ROL, "pasa": t3_val >= T3_ROL,
            "detalle": f"{rol_ok}/{comparables} pares coinciden en rol",
        }

        cob_ok = sum(1 for r, g in pares if r.get("cobertura") == g.get("cobertura"))
        t4_val = cob_ok / comparables
        # Adyacencia ordinal de los seis fits.
        dist_ok, dist_tot = 0, 0
        fits = ["actor_fit", "procedimiento_fit", "coordinacion_fit",
                "enforcement_fit", "salvaguarda_derechos_fit", "federalismo_fit"]
        for r, g in pares:
            for f in fits:
                d = _fit_distance(r.get(f), g.get(f))
                if d is None:
                    continue
                dist_tot += 1
                if d <= 1:
                    dist_ok += 1
        adyac = (dist_ok / dist_tot) if dist_tot else 1.0
        t4 = {
            "nombre": "Acuerdo de cobertura ≥ 70% (adyacencia ≥ 75%)", "obligatorio": True,
            "valor": t4_val, "umbral": T4_COBERTURA,
            "adyacencia": adyac, "adyacencia_umbral": T4_ADYACENCIA,
            "pasa": (t4_val >= T4_COBERTURA) and (adyac >= T4_ADYACENCIA),
            "detalle": f"cobertura {cob_ok}/{comparables}; adyacencia {dist_ok}/{dist_tot}",
        }

        falsos = [
            r.get("disposicion") for r, g in pares
            if g.get("rol_correspondencia") == "contextual_habilitante"
            and r.get("rol_correspondencia") == "sustantivo"
            and r.get("cobertura") == "completa"
        ]
        t5 = {
            "nombre": "Sin falsos sustantivos graves", "obligatorio": True,
            "valor": 0 if falsos else 1, "umbral": 1, "pasa": not falsos,
            "detalle": falsos,
        }

    umbrales = [t1, t2, t3, t4, t5]
    evaluables = [u for u in umbrales if u.get("pasa") is not None]
    aprueba = all(u["pasa"] for u in evaluables)
    omitidos = [u for u in umbrales if u.get("omitido")]

    return {
        "umbrales": umbrales,
        "comparables": comparables,
        "aprueba": aprueba,
        "omitidos": len(omitidos),
    }


def format_report(report: dict) -> str:
    """Reporte legible por umbral."""
    lines = ["=== Evaluación dorada NormTrace (LGA × ODS 6) ==="]
    for u in report["umbrales"]:
        if u.get("omitido"):
            estado = "OMITIDO"
        elif u["pasa"]:
            estado = "PASA"
        else:
            estado = "FALLA"
        val = ""
        if "valor" in u and not u.get("omitido"):
            v = u["valor"]
            val = f" — {v:.0%}" if isinstance(v, float) else f" — {v}"
        lines.append(f"[{estado}] {u['nombre']}{val}")
        det = u.get("detalle")
        if det and (not u.get("pasa") or u.get("omitido")):
            lines.append(f"        {det}")
    lines.append(f"comparables con el dorado: {report['comparables']}")
    if report["omitidos"]:
        lines.append(
            f"NOTA: {report['omitidos']} umbral(es) de acuerdo omitidos "
            "(sin corrida automática comparable; configure LLM_PROVIDER para evaluarlos)."
        )
    lines.append("RESULTADO: " + ("APRUEBA" if report["aprueba"] else "REPRUEBA"))
    return "\n".join(lines)
