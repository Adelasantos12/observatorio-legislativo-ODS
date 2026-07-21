"""Scraper de minutas de la Cámara de Diputados (iniclave) — Huella 2030, v3.

Fuente: sistema "iniclave" de la Cámara de Diputados, que publica por año
legislativo la relación de minutas de la Cámara como cámara de origen. El corte
verificado (21/jul/2026) vive como semilla cruda en
`normtrace/03_tables/legislative_mapping/minutas_lxvi_raw.csv` (139 minutas de la
LXVI, columnas: clave, anio, titulo, fecha_aprobacion, observaciones, estatus,
pdfs). El scraper produce exactamente ese esquema.

Diseño (como `gaceta.py`/`sil_ejecutivo.py`): funciones deterministas y sin red
sobre el CSV/HTML ya obtenido; `sync_minutas` orquesta y hace
`upsert_preserving_coding` (nunca pisa codificación, atribución ni
`nivel_revision`). Verificación de completitud: la numeración de claves debe ser
**continua** en la legislatura; si hay un hueco, se reporta en el log, no se
silencia (adenda v3 §A1).

La clave es única y estable, p. ej. `CD-LXVI-I-1P-001` o `CD-LXVI-II-1E-139`
(1E = periodo extraordinario). Estatus normalizados: `publicada_dof`,
`en_revisora`, `devuelta`.
"""

import csv
import re
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
RAW_CSV = _REPO_ROOT / "normtrace/03_tables/legislative_mapping/minutas_lxvi_raw.csv"

RAW_COLS = ["clave", "anio", "titulo", "fecha_aprobacion", "observaciones", "estatus", "pdfs"]


def parse_clave(clave: str):
    """'CD-LXVI-I-1P-001' -> (legislatura, anio, periodo, numero).

    Tolera claves con más o menos guiones; el número es el último segmento.
    """
    parts = (clave or "").split("-")
    legislatura = parts[1] if len(parts) > 1 else None
    anio = parts[2] if len(parts) > 2 else None
    periodo = parts[3] if len(parts) > 3 else None
    numero = None
    if parts:
        m = re.search(r"\d+", parts[-1])
        if m:
            numero = int(m.group(0))
    return legislatura, anio, periodo, numero


def parse_pdfs(field: str):
    return [p.strip() for p in (field or "").split(";") if p.strip()]


def load_raw_csv(path=None):
    """Lee la semilla cruda del iniclave y devuelve filas dict."""
    path = Path(path) if path else RAW_CSV
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def sequence_report(claves):
    """Verifica que la numeración de claves sea continua.

    Devuelve {min, max, total, gaps: [n...]}. `gaps` vacío = sin huecos.
    """
    nums = sorted(parse_clave(c)[3] for c in claves if parse_clave(c)[3] is not None)
    if not nums:
        return {"min": None, "max": None, "total": 0, "gaps": []}
    completo = set(range(nums[0], nums[-1] + 1))
    gaps = sorted(completo - set(nums))
    return {"min": nums[0], "max": nums[-1], "total": len(nums), "gaps": gaps}


def raw_to_minuta(raw: dict):
    """Convierte una fila cruda del iniclave en un Minuta (solo fuente).

    No aporta codificación ni atribución: `nivel_revision` queda None y la
    codificación en pendiente; la fija después la tubería de codificación.
    """
    from tipi_data.models.minuta import Minuta

    clave = raw["clave"].strip()
    legislatura, anio, periodo, numero = parse_clave(clave)
    return Minuta(
        _id=clave,
        clave=clave,
        legislatura=legislatura,
        anio=raw.get("anio") or anio,
        periodo=periodo,
        numero=numero,
        denominacion=(raw.get("titulo") or "").strip() or None,
        fecha_aprobacion=(raw.get("fecha_aprobacion") or "").strip() or None,
        observaciones=(raw.get("observaciones") or "").strip() or None,
        estatus=(raw.get("estatus") or "").strip() or None,
        pdfs=parse_pdfs(raw.get("pdfs")),
        confianza="pendiente",
        updated_at=datetime.now(timezone.utc),
    )


def sync_minutas(csv_path=None, legislatura: str = "LXVI") -> dict:
    """Sincroniza el iniclave (semilla cruda) con la colección `minutas`.

    Hace upsert preservando codificación/atribución/nivel_revision. Reporta el
    desglose por estatus y año, y **cualquier hueco** en la secuencia de claves.
    """
    from tipi_data.repositories.minutas import Minutas

    rows = load_raw_csv(csv_path)
    claves = [r["clave"].strip() for r in rows]
    seq = sequence_report(claves)

    from collections import Counter
    por_estatus = Counter()
    por_anio = Counter()
    for raw in rows:
        Minutas.upsert_preserving_coding(raw_to_minuta(raw))
        por_estatus[(raw.get("estatus") or "").strip()] += 1
        por_anio[(raw.get("anio") or "").strip()] += 1

    corte = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    Minutas.set_corte(corte)
    return {
        "total": len(rows),
        "por_estatus": dict(por_estatus),
        "por_anio": dict(por_anio),
        "secuencia": seq,
        "corte": corte,
    }
