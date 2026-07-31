#!/usr/bin/env python3
"""CRN Indexer — Capa de Referencia Normativa para PAIL-MX.

Indexa una carpeta de .md (p. ej. un vault de Obsidian con normas) y produce:
  manifest.json   — norma, archivo, publicacion_dof, ultima_reforma_dof, estatus
  articles.json   — por norma: artículo, línea, historia de reformas de la unidad
  crossrefs.json  — remisiones detectadas: (norma, artículo) -> norma destino [, artículo]

Uso:
  python3 crn_indexer.py index   <carpeta_vault> <carpeta_salida>
  python3 crn_indexer.py query   <carpeta_salida> "<Norma>" <artículo>
  python3 crn_indexer.py inbound <carpeta_salida> "<Norma>" [artículo]

`inbound` responde: ¿quién cita esta norma/artículo? = leyes candidatas a armonización
cuando la iniciativa reforma esa unidad (verificación R2-08 de PAIL-MX).
"""
import json, re, sys, unicodedata
from pathlib import Path

ART_RE = re.compile(r"^#{1,6}\s*Art[íi]culo\s+(.+?)\s*$", re.M)
REF_UNIT_RE = re.compile(r">\s*\*[^*\n]*DOF[^*\n]*\*")
FM_RE = re.compile(r"^---\n(.*?)\n---", re.S)


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def frontmatter(text):
    m = FM_RE.match(text)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"')
    return fm


def guess_name(fm, path):
    return fm.get("nombre") or fm.get("title") or path.stem.replace("_", " ")


def build(folder, outdir):
    folder, outdir = Path(folder).expanduser(), Path(outdir).expanduser()
    outdir.mkdir(parents=True, exist_ok=True)
    files = sorted(folder.rglob("*.md"))
    manifest, articles, warnings = [], {}, []
    texts = {}
    for p in files:
        t = p.read_text(encoding="utf-8", errors="replace")
        fm = frontmatter(t)
        name = guess_name(fm, p)
        if name in texts:
            warnings.append(f"NOMBRE DUPLICADO: '{name}' en {p.name} ya usado por otro archivo — revisar frontmatter; se indexa como '{name} [{p.stem}]'")
            name = f"{name} [{p.stem}]"
        h1 = re.search(r"^#\s+(.+)$", t, re.M)
        if h1 and norm(name) not in norm(h1.group(1)) and norm(h1.group(1)) not in norm(name):
            warnings.append(f"{p.name}: nombre del frontmatter ('{name}') no coincide con el encabezado del documento ('{h1.group(1).strip()}') — posible etiquetado erróneo de la conversión")
        texts[name] = t
        entry = {
            "norma": name,
            "archivo": str(p.relative_to(folder)),
            "publicacion_dof": fm.get("publicacion_dof"),
            "ultima_reforma_dof": fm.get("ultima_reforma_dof"),
            "estatus": fm.get("estatus", "SIN ESTATUS"),
        }
        if not entry["ultima_reforma_dof"]:
            # 1) intentar recuperar la fecha del cuerpo del documento (formato DOF dd-mm-aaaa)
            m2 = re.search(
                r"[ÚU]ltima[s]?\s+reforma[s]?\s+(?:publicada[s]?\s+)?(?:en\s+el\s+)?DOF[:\s]+"
                r"([0-9]{2})-([0-9]{2})-([0-9]{4})", t)
            if m2:
                d, mo, y = m2.groups()
                entry["ultima_reforma_dof"] = f"{y}-{mo}-{d}"
                entry["fuente_reforma"] = "cuerpo_del_documento"
            elif not re.search(r"reforma[a-z]*\s+DOF", t, re.I) and entry["publicacion_dof"]:
                # 2) sin rastro de reforma alguna en el cuerpo: ley probablemente nunca reformada
                entry["sin_reformas_probable"] = True
            else:
                # 3) hay menciones de reformas pero ninguna fecha recuperable: metadato faltante real
                warnings.append(f"{name}: falta ultima_reforma_dof y no se recuperó del cuerpo → citas pendiente_verificacion")
        if not entry["publicacion_dof"]:
            warnings.append(f"{name}: falta publicacion_dof en frontmatter")
        manifest.append(entry)
        lines = t.splitlines()
        arts = []
        for m in ART_RE.finditer(t):
            ln = t[: m.start()].count("\n") + 1
            block_end = min(ln + 40, len(lines))
            reforms = [x.strip() for x in lines[ln:block_end] if REF_UNIT_RE.search(x)]
            nxt = REF_UNIT_RE.search("\n".join(lines[ln:block_end]))
            arts.append({
                "articulo": m.group(1).rstrip("."),
                "linea": ln,
                "reforma_unidad": reforms[0].strip("> *") if reforms else None,
            })
        articles[name] = arts
        if not arts:
            warnings.append(f"{name}: 0 artículos indexados — posible nota del vault (no norma) o encabezados de artículo con formato distinto")
    # remisiones: buscar menciones de cada norma dentro de los artículos de las demás
    name_pats = {n: re.compile(re.escape(norm(n))) for n in texts}
    art_target = re.compile(
        r"art[íi]culos?\s+([0-9]+[0-9oA-Za-z\s,y-]{0,40}?)\s+(?:de|del)\s+(?:el\s|la\s|los\s|las\s)?", re.I)
    crossrefs = []
    for src, t in texts.items():
        tn = norm(t)
        spans = [(m.start(), m.group(1).rstrip(".")) for m in ART_RE.finditer(t)]
        for dst, pat in name_pats.items():
            if dst == src:
                continue
            for m in pat.finditer(tn):
                # artículo fuente = último encabezado antes de la mención
                src_art = None
                for pos, a in spans:
                    if pos < m.start():
                        src_art = a
                    else:
                        break
                # ¿la mención viene precedida de "artículo N de ..."?
                window = tn[max(0, m.start() - 90): m.start()]
                am = None
                for am in art_target.finditer(window):
                    pass
                crossrefs.append({
                    "norma_origen": src, "articulo_origen": src_art,
                    "norma_destino": dst,
                    "articulo_destino": am.group(1).strip() if am and window.rstrip().endswith(("de", "del", "de la", "del ")) is False else (am.group(1).strip() if am else None),
                })
    (outdir / "manifest.json").write_text(json.dumps(
        {"corpus": "CRN-PAIL-MX", "normas": manifest, "advertencias": warnings},
        ensure_ascii=False, indent=2), encoding="utf-8")
    (outdir / "articles.json").write_text(json.dumps(articles, ensure_ascii=False, indent=2), encoding="utf-8")
    (outdir / "crossrefs.json").write_text(json.dumps(crossrefs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Normas: {len(manifest)} | Artículos: {sum(len(a) for a in articles.values())} | "
          f"Remisiones detectadas: {len(crossrefs)} | Advertencias: {len(warnings)}")
    for w in warnings[:10]:
        print("  AVISO:", w)


def load(outdir):
    o = Path(outdir).expanduser()
    return (json.loads((o / "manifest.json").read_text(encoding="utf-8")),
            json.loads((o / "articles.json").read_text(encoding="utf-8")),
            json.loads((o / "crossrefs.json").read_text(encoding="utf-8")))


def find_norma(manifest, q):
    qn = norm(q)
    hits = [e for e in manifest["normas"] if qn in norm(e["norma"])]
    if not hits:
        sys.exit(f"Norma no encontrada en el corpus: {q} (regla CRN-4: NO_VERIFICABLE)")
    return hits[0]


def query(outdir, nq, art):
    manifest, articles, _ = load(outdir)
    e = find_norma(manifest, nq)
    arts = articles[e["norma"]]
    target = [a for a in arts if norm(a["articulo"]) == norm(art) or a["articulo"].split()[0] == art]
    if not target:
        sys.exit(f"{e['norma']}: artículo {art} no localizado")
    a = target[0]
    if e.get("sin_reformas_probable"):
        vig = f"sin reformas; texto original DOF {e['publicacion_dof']}"
    elif e.get("ultima_reforma_dof"):
        vig = f"última reforma DOF {e['ultima_reforma_dof']}" + (
            " (recuperada del cuerpo del documento)" if e.get("fuente_reforma") else "")
    else:
        vig = "reforma no determinada — cita pendiente_verificacion"
    print(f"{e['norma']}, artículo {a['articulo']} — "
          f"(norma: {vig}; "
          f"unidad: {a['reforma_unidad'] or 'sin reforma registrada en el archivo'}; "
          f"estatus: {e['estatus']}) [línea {a['linea']} de {e['archivo']}]")


def inbound(outdir, nq, art=None):
    manifest, _, crossrefs = load(outdir)
    e = find_norma(manifest, nq)
    hits = [c for c in crossrefs if c["norma_destino"] == e["norma"]
            and (art is None or (c.get("articulo_destino") or "").startswith(art))]
    srcs = {}
    for c in hits:
        srcs.setdefault(c["norma_origen"], set()).add(c["articulo_origen"] or "?")
    print(f"Remisiones entrantes a {e['norma']}" + (f", artículo {art}" if art else "") + f": {len(hits)}")
    print("Leyes candidatas a armonización (R2-08):")
    for s, aa in sorted(srcs.items()):
        arts_l = sorted(aa)
        print(f"  - {s} (desde art. {', '.join(arts_l[:8])}{'…' if len(arts_l) > 8 else ''})")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "index":
        build(sys.argv[2], sys.argv[3])
    elif cmd == "query":
        query(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "inbound":
        inbound(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    else:
        sys.exit(__doc__)
