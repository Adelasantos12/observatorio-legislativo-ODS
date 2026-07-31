#!/usr/bin/env python3
"""PAIL Engine — motor del protocolo PAIL-MX v2.

Carga el rulebook (pail_protocol.json), ejecuta sobre el texto de una
iniciativa las verificaciones deterministas y heurísticas como código, y
emite las de juicio como PENDIENTE_JUICIO con el criterio embebido (payload
listo para un LLM). Aplica las reglas de agregación y produce el dictamen
JSON. Depende de crn_indexer para las verificaciones contra corpus.

Uso:
  python3 pail_engine.py analizar <iniciativa.md|.txt> \
      [--rulebook pail_protocol.json] [--indices crn_indices] \
      [--mtl] [--out dictamen.json]

Capas: nucleo_triaje y csn corren siempre; mtl solo con --mtl;
racionalidad se emite siempre como PENDIENTE_JUICIO (la resuelve el LLM).
"""
import argparse, json, re, sys, unicodedata
from pathlib import Path

# ---------- utilidades ----------

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")

ART_SPLIT = re.compile(r"(?m)^(?:#{1,6}\s*)?(Art[íi]culo\s+(?:\d+[\w°.]*(?:\s+(?:Bis|Ter|Qu[áa]ter|Quinquies))?|[ÚU]nico))[\s.\-–]")
ROMAN = r"[IVXLCDM]+"
FRAC = re.compile(rf"(?m)^\s*({ROMAN})\.\s+(.+)$")
TRANS_HDR = re.compile(r"(?im)^\s*(?:#{1,6}\s*)?(TRANSITORIOS?|ART[ÍI]CULOS?\s+TRANSITORIOS?)\s*$")
EXPO_HDR = re.compile(r"(?i)EXPOSICI[ÓO]N\s+DE\s+MOTIVOS")

def hallazgo(check, resultado, evidencia=None, explicacion="", extra=None):
    h = {"id": check["id"], "capa": check["capa"], "nombre": check["nombre"],
         "tipo": check["tipo"], "resultado": resultado,
         "severidad": check["severidad"], "evidencia": evidencia or [],
         "explicacion": explicacion}
    if check["tipo"] == "juicio":
        h["criterio_para_llm"] = check["criterio"]
    if extra:
        h.update(extra)
    return h

def ev(cita, ubicacion, fuente="iniciativa"):
    return {"cita": cita.strip()[:300], "ubicacion": ubicacion, "fuente": fuente}

# ---------- segmentación mínima de la iniciativa ----------

def segmentar(texto):
    partes = {"expo": None, "articulado": texto, "transitorios": None}
    t = TRANS_HDR.search(texto)
    if t:
        partes["articulado"] = texto[: t.start()]
        partes["transitorios"] = texto[t.start():]
    e = EXPO_HDR.search(partes["articulado"])
    m0 = ART_SPLIT.search(partes["articulado"])
    if e and m0 and e.start() < m0.start():
        partes["expo"] = partes["articulado"][e.start(): m0.start()]
    arts, spans = [], list(ART_SPLIT.finditer(partes["articulado"]))
    for i, m in enumerate(spans):
        fin = spans[i + 1].start() if i + 1 < len(spans) else len(partes["articulado"])
        arts.append({"rotulo": m.group(1), "texto": partes["articulado"][m.start(): fin],
                     "linea": partes["articulado"][: m.start()].count("\n") + 1})
    partes["articulos"] = arts
    return partes

# ---------- verificaciones deterministas / heurísticas ----------

def chk_regex_partes(c, P, ctx):
    faltan = [n for n, k in [("exposición de motivos", "expo"), ("articulado", "articulos"),
                             ("régimen transitorio", "transitorios")] if not P.get(k)]
    if not faltan:
        return hallazgo(c, "CUMPLE")
    return hallazgo(c, "PARCIAL", [], f"Partes ausentes: {', '.join(faltan)}")

def chk_regex_tipo(c, P, ctx):
    t = norm(P["articulado"][:4000])
    tipo = ("reforma" if re.search(r"se reforma|se adiciona|se deroga", t)
            else "ley_nueva" if re.search(r"se expide", t) else "indeterminado")
    ctx["tipo_instrumento"] = tipo
    return hallazgo(c, "CUMPLE" if tipo != "indeterminado" else "NO_EVALUABLE",
                    [], f"tipo_instrumento={tipo}")

def chk_numeracion(c, P, ctx):
    nums, probs = [], []
    for a in P["articulos"]:
        m = re.search(r"\d+", a["rotulo"])
        if m:
            nums.append((int(m.group()), a))
    vistos = {}
    for n, a in nums:
        if n in vistos:
            probs.append(ev(a["rotulo"], f"línea {a['linea']}"))
    for (n1, _), (n2, a2) in zip(nums, nums[1:]):
        if n2 not in (n1, n1 + 1) and "Bis" not in a2["rotulo"]:
            probs.append(ev(f"{a2['rotulo']} tras artículo {n1}", f"línea {a2['linea']}"))
    if not P["articulos"]:
        return hallazgo(c, "NO_EVALUABLE", [], "Sin artículos detectados")
    return hallazgo(c, "CUMPLE" if not probs else "INCUMPLE", probs,
                    "" if not probs else "Saltos o duplicados en la numeración")

def chk_parrafos(c, P, ctx):
    probs = [ev(a["rotulo"] + f" — {len(pp)} párrafos", f"línea {a['linea']}")
             for a in P["articulos"]
             if len(pp := [p for p in a["texto"].split("\n\n") if len(p.strip()) > 40]) > 4]
    return hallazgo(c, "CUMPLE" if not probs else "PARCIAL", probs,
                    "" if not probs else "Artículos que exceden 4 párrafos (revisar unidad temática)")

def chk_fracciones(c, P, ctx):
    probs = []
    for a in P["articulos"]:
        fr = FRAC.findall(a["texto"])
        if len(fr) >= 2:
            penult = fr[-2][1].rstrip()
            if not re.search(r",\s*y\s*$", penult):
                probs.append(ev(f"{a['rotulo']}, fr. {fr[-2][0]}: «…{penult[-60:]}»", f"línea {a['linea']}"))
    return hallazgo(c, "CUMPLE" if not probs else "PARCIAL", probs,
                    "" if not probs else "Penúltima fracción sin la fórmula ', y'")

def chk_enunciado_reforma(c, P, ctx):
    if ctx.get("tipo_instrumento") != "reforma":
        return hallazgo(c, "NO_APLICA")
    m = re.search(r"(?i)se\s+(?:reforma[n]?|adiciona[n]?|deroga[n]?)[^.]{10,600}", P["articulado"])
    if not m:
        return hallazgo(c, "INCUMPLE", [], "Decreto de reforma sin enunciado que precise qué se reforma/adiciona/deroga")
    ctx["enunciado_reforma"] = m.group(0)
    return hallazgo(c, "CUMPLE", [ev(m.group(0), "proemio del decreto")])

def chk_transitorios(c, P, ctx):
    if not P["transitorios"]:
        return hallazgo(c, "INCUMPLE", [], "Sin régimen transitorio")
    t, probs = P["transitorios"], []
    if not re.search(r"(?i)entrar[áa]\s+en\s+vigor", t):
        probs.append(ev("(ausente)", "transitorios — sin cláusula de entrada en vigor"))
    m = re.search(r"(?i)se\s+derogan\s+todas\s+las\s+disposiciones[^.]*", t)
    if m and not re.search(r"(?i)se\s+deroga[n]?\s+(?:el|la|los|las)\s", t):
        probs.append(ev(m.group(0), "transitorios — derogación exclusivamente genérica"))
    return hallazgo(c, "CUMPLE" if not probs else "PARCIAL", probs)

def chk_mandatos_sin_plazo(c, P, ctx):
    if not P["transitorios"]:
        return hallazgo(c, "NO_APLICA")
    probs = []
    for m in re.finditer(r"(?i)deber[áa]n?\s+(?:emitir|expedir|instalar|armonizar|adecuar)[^.]{0,300}\.", P["transitorios"]):
        if not re.search(r"(?i)\d+\s*(d[íi]as|meses|a[ñn]os)|plazo", m.group(0)):
            probs.append(ev(m.group(0), "transitorios"))
    return hallazgo(c, "CUMPLE" if not probs else "INCUMPLE", probs,
                    "" if not probs else "Mandatos transitorios sin plazo")

def chk_oraciones(c, P, ctx):
    probs = []
    for a in P["articulos"]:
        for o in re.split(r"(?<=[.;])\s+", a["texto"]):
            if len(o.split()) > 60:
                probs.append(ev(o, f"{a['rotulo']} (línea {a['linea']}) — {len(o.split())} palabras"))
    return hallazgo(c, "CUMPLE" if not probs else "PARCIAL", probs[:15],
                    "" if not probs else f"{len(probs)} oración(es) superan el umbral de 60 palabras")

def chk_habilitaciones(c, P, ctx):
    hits = [ev(m.group(0), "articulado")
            for m in re.finditer(r"(?i)(?:conforme|con\s+arreglo)?\s*(?:a\s+)?(?:el|lo\s+que\s+establezca\s+el)?\s*reglamento[^.]{0,200}\.", P["articulado"])][:10]
    if not hits:
        return hallazgo(c, "NO_APLICA")
    return hallazgo(c, "PENDIENTE_JUICIO", hits,
                    "Habilitaciones detectadas; el juicio (alcance, órgano, plazo, reserva) requiere LLM",
                    {"criterio_para_llm": c["criterio"]})

def chk_impacto(c, P, ctx):
    m = re.search(r"(?i)sin\s+impacto\s+presupuest\w+[^.]*", P.get("expo") or P["articulado"])
    crea = re.search(r"(?i)se\s+crea[n]?\s+(?:el|la|un|una)\s+(instituto|comisi[óo]n|registro|consejo|organismo|sistema)", P["articulado"])
    if m and crea:
        return hallazgo(c, "INCUMPLE", [ev(m.group(0), "exposición de motivos"), ev(crea.group(0), "articulado")],
                        "Declara sin impacto presupuestario pero crea estructura")
    return hallazgo(c, "PENDIENTE_JUICIO", [], "", {"criterio_para_llm": c["criterio"]})

# ---------- verificaciones contra corpus (CSN) ----------

def cargar_indices(ruta):
    p = Path(ruta)
    try:
        return {k: json.loads((p / f"{k}.json").read_text(encoding="utf-8"))
                for k in ("manifest", "articles", "crossrefs")}
    except Exception:
        return None

def normas_invocadas(texto, manifest):
    inv = []
    tn = norm(texto)
    for e in manifest["normas"]:
        if len(e["norma"]) > 12 and norm(e["norma"]) in tn:
            inv.append(e)
    return inv

def chk_vigencia(c, P, ctx, idx):
    if not idx:
        return hallazgo(c, "NO_VERIFICABLE", [], "Índices CRN no disponibles")
    inv = normas_invocadas(P["articulado"], idx["manifest"])
    ctx["normas_invocadas"] = [e["norma"] for e in inv]
    probs, evs = [], []
    for e in inv:
        ref = e.get("ultima_reforma_dof") or f"sin reformas; texto original DOF {e.get('publicacion_dof')}"
        evs.append({"norma": e["norma"], "ultima_reforma": ref, "estatus": e.get("estatus")})
        if "abrog" in norm(str(e.get("estatus", ""))):
            probs.append({"norma": e["norma"], "estatus": e["estatus"]})
    res = "CUMPLE" if inv and not probs else ("PARCIAL" if probs else "NO_EVALUABLE")
    return hallazgo(c, res, [], "Invoca norma(s) con estatus abrogado" if probs else "",
                    {"normas_invocadas": evs, "invocaciones_problema": probs})

def chk_inbound(c, P, ctx, idx):
    if ctx.get("tipo_instrumento") != "reforma":
        return hallazgo(c, "NO_APLICA")
    if not idx:
        return hallazgo(c, "NO_VERIFICABLE", [], "Índices CRN no disponibles")
    enun = ctx.get("enunciado_reforma", "")
    objetivo = next((e for e in idx["manifest"]["normas"] if norm(e["norma"]) in norm(enun)), None)
    if not objetivo:
        return hallazgo(c, "NO_VERIFICABLE", [ev(enun or "(sin enunciado)", "proemio")],
                        "Norma objetivo de la reforma no localizada en el corpus",
                        {"normas_faltantes": [enun.strip()[:120]]})
    arts_ref = re.findall(r"\d+\s*(?:Bis|Ter)?", enun)
    entrantes = [x for x in idx["crossrefs"] if x["norma_destino"] == objetivo["norma"]
                 and (not arts_ref or not x.get("articulo_destino")
                      or any(x["articulo_destino"].startswith(a.strip()) for a in arts_ref))]
    srcs = sorted({(x["norma_origen"], x.get("articulo_origen") or "?") for x in entrantes})
    return hallazgo(c, "CUMPLE" if not srcs else "PENDIENTE_JUICIO", [],
                    ("Sin remisiones entrantes registradas" if not srcs else
                     f"{len(srcs)} remisiones entrantes: verificar si el decreto o sus transitorios las atienden"),
                    {"norma_objetivo": objetivo["norma"],
                     "armonizacion_candidata": [{"norma": s, "desde_articulo": a} for s, a in srcs][:40]})

def chk_salientes(c, P, ctx, idx):
    if not idx:
        return hallazgo(c, "NO_VERIFICABLE", [], "Índices CRN no disponibles")
    inv = normas_invocadas(P["articulado"], idx["manifest"])
    a_art = en_bloque = 0
    for e in inv:
        for m in re.finditer(re.escape(norm(e["norma"])), norm(P["articulado"])):
            ventana = norm(P["articulado"])[max(0, m.start() - 90): m.start()]
            if re.search(r"art[íi]culos?\s+[\d]", ventana):
                a_art += 1
            else:
                en_bloque += 1
    total = a_art + en_bloque
    if not total:
        return hallazgo(c, "NO_APLICA", [], "Sin remisiones externas detectadas")
    prop = round(en_bloque / total, 2)
    return hallazgo(c, "CUMPLE", [], f"Remisiones: {a_art} a artículo, {en_bloque} en bloque",
                    {"indicador_cableado": {"a_articulo": a_art, "en_bloque": en_bloque,
                                            "proporcion_bloque": prop,
                                            "lectura": "predominio de remisión en bloque — mandato nombrado sin ruta operativa" if prop > 0.7 else "cableado aceptable"}})

METODOS = {"regex_partes": chk_regex_partes, "regex_tipo_instrumento": chk_regex_tipo,
           "numeracion_articulos": chk_numeracion, "parrafos_por_articulo": chk_parrafos,
           "formato_fracciones": chk_fracciones, "enunciado_reforma": chk_enunciado_reforma,
           "transitorios": chk_transitorios, "mandatos_sin_plazo": chk_mandatos_sin_plazo,
           "oraciones_largas": chk_oraciones, "habilitaciones": chk_habilitaciones,
           "impacto_presupuestal": chk_impacto}
METODOS_CORPUS = {"vigencia_invocadas": chk_vigencia, "inbound_corpus": chk_inbound,
                  "remisiones_salientes": chk_salientes}

# ---------- agregación y dictamen ----------

def dictaminar(hallazgos, sin_articulado=False):
    EVALUADOS = ("CUMPLE", "PARCIAL", "INCUMPLE", "NO_APLICA")
    bloq = [h for h in hallazgos if h["resultado"] == "INCUMPLE" and h["severidad"] == "BLOQUEANTE"]
    bloq_pend = [h for h in hallazgos if h["severidad"] == "BLOQUEANTE" and h["resultado"] not in EVALUADOS]
    n_eval = sum(1 for h in hallazgos if h["resultado"] in EVALUADOS)
    cobertura = round(n_eval / len(hallazgos), 2) if hallazgos else 0.0
    capas = {}
    for h in hallazgos:
        capas.setdefault(h["capa"], []).append(h)
    por_capa = {k: ("DEFICIENTE" if sum(1 for h in v if h["resultado"] == "INCUMPLE" and h["severidad"] == "MAYOR") >= 3
                    else "SIN_EVALUAR" if not any(h["resultado"] in EVALUADOS for h in v)
                    else "ACEPTABLE") for k, v in capas.items()}
    if sin_articulado:
        glob = "NO_EVALUABLE_INSUMO"
    elif bloq:
        glob = "NO_VIABLE_EN_SUS_TERMINOS"
    elif cobertura < 0.5 or bloq_pend:
        glob = "PRELIMINAR_COBERTURA_INSUFICIENTE"
    elif any(v == "DEFICIENTE" for v in por_capa.values()):
        glob = "VIABLE_CON_MODIFICACIONES"
    else:
        glob = "VIABLE"
    return por_capa, glob, cobertura

ORDEN_SEV = {"BLOQUEANTE": 0, "MAYOR": 1, "MENOR": 2, "ANALITICO": 3}

def resumen_ejecutivo(hallazgos, cobertura, sin_articulado):
    red = sorted([h for h in hallazgos if h["resultado"] in ("INCUMPLE", "PARCIAL")
                  and h["severidad"] in ("BLOQUEANTE", "MAYOR")],
                 key=lambda h: (ORDEN_SEV.get(h["severidad"], 9), h["resultado"] != "INCUMPLE"))
    oport = [h for h in hallazgos if (h["resultado"] == "PARCIAL" and h["severidad"] == "MENOR")
             or (h["severidad"] == "ANALITICO" and h.get("indicador_cableado"))
             or h.get("armonizacion_candidata")]
    def fila(h):
        return {"id": h["id"], "verificacion": h["nombre"], "severidad": h["severidad"],
                "resultado": h["resultado"],
                "hallazgo": h["explicacion"] or h["nombre"],
                "evidencia_muestra": (h["evidencia"][0] if h["evidencia"] else None),
                "armonizacion": h.get("armonizacion_candidata"),
                "cableado": h.get("indicador_cableado")}
    pend = [h for h in hallazgos if h["resultado"] in ("PENDIENTE_JUICIO", "NO_EVALUABLE", "NO_VERIFICABLE")]
    razones = {}
    for h in pend:
        razones[h["explicacion"] or h["resultado"]] = razones.get(h["explicacion"] or h["resultado"], 0) + 1
    return {"nota_insumo": ("El texto no contiene articulado segmentable: verificar que el documento sea una "
                            "iniciativa o proyecto de decreto (no una opinión, dictamen o nota) o reportar el "
                            "formato para ajustar el segmentador.") if sin_articulado else None,
            "red_flags": [fila(h) for h in red],
            "areas_oportunidad": [fila(h) for h in oport],
            "cobertura_evaluada": cobertura,
            "sin_evaluar": {"total": len(pend),
                            "razones": sorted(razones.items(), key=lambda x: -x[1])[:3]}}

DEPENDEN_DE_ARTICULADO = {"numeracion_articulos", "parrafos_por_articulo", "formato_fracciones",
                          "oraciones_largas", "transitorios", "mandatos_sin_plazo"}

def analizar(texto, rulebook, indices=None, mtl=False):
    P = segmentar(texto)
    ctx, hs = {}, []
    sin_articulado = not P["articulos"]
    for c in rulebook["verificaciones"]:
        if c["capa"] == "mtl" and not mtl:
            continue
        met = c.get("metodo")
        if sin_articulado and (met in DEPENDEN_DE_ARTICULADO or c["tipo"] == "juicio"):
            hs.append(hallazgo(c, "NO_EVALUABLE", [],
                               "Sin articulado segmentable: el insumo no parece una iniciativa o su formato no fue reconocido"))
            continue
        if met in METODOS:
            hs.append(METODOS[met](c, P, ctx))
        elif met in METODOS_CORPUS:
            hs.append(METODOS_CORPUS[met](c, P, ctx, indices))
        else:
            hs.append(hallazgo(c, "PENDIENTE_JUICIO"))
    por_capa, glob, cobertura = dictaminar(hs, sin_articulado)
    return {"protocolo": rulebook["protocolo"], "version_rulebook": rulebook["version"],
            "modulo_mtl_activo": mtl, "articulos_detectados": len(P["articulos"]),
            "resumen": resumen_ejecutivo(hs, cobertura, sin_articulado),
            "contexto": ctx, "verificaciones": hs,
            "dictamen_por_capa": por_capa, "dictamen_global": glob,
            "cobertura_evaluada": cobertura,
            "nota": "Las verificaciones PENDIENTE_JUICIO llevan criterio_para_llm embebido: resolverlas con LLM y re-agregar."}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["analizar"])
    ap.add_argument("archivo")
    ap.add_argument("--rulebook", default="pail_protocol.json")
    ap.add_argument("--indices", default=None)
    ap.add_argument("--mtl", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rb = json.loads(Path(a.rulebook).read_text(encoding="utf-8"))
    idx = cargar_indices(a.indices) if a.indices else None
    res = analizar(Path(a.archivo).read_text(encoding="utf-8", errors="replace"), rb, idx, a.mtl)
    salida = json.dumps(res, ensure_ascii=False, indent=1)
    if a.out:
        Path(a.out).write_text(salida, encoding="utf-8")
        print(f"Dictamen: {res['dictamen_global']} → {a.out}")
    else:
        print(salida)

if __name__ == "__main__":
    main()
