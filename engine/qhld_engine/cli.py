"""QHLD engine CLI — the `qhld` command (entrypoint: ``qhld_engine.cli:app``).

Composition root: wires the command groups defined under
``qhld_engine.presentation.cli`` and hosts the single-shot leaf commands
(stats, footprint, send-alerts, topic-alignment) inline. Task classes are
imported lazily inside each command so ``qhld --help`` stays fast and side-effect
free.
"""

import typer

from qhld_engine.presentation.cli import debug, extractor, tagger, untagger

app = typer.Typer(
    name="qhld",
    help="QHLD engine CLI — extract, tag, stats, footprint.",
    no_args_is_help=True,
)

app.add_typer(extractor.app, name="extractor")
app.add_typer(tagger.app, name="tagger")
app.add_typer(untagger.app, name="untagger")
app.add_typer(debug.app, name="debug")


@app.command("stats")
def stats():
    """Generate aggregated stats by topic, deputy and parliamentary group."""
    from qhld_engine.stats.process_stats import GenerateStats

    GenerateStats().generate()


@app.command("footprint")
def footprint():
    """Compute the legislative footprint for every topic and entity."""
    from qhld_engine.footprint.compute_footprint import ComputeFootprint

    ComputeFootprint().compute()


@app.command("send-alerts")
def send_alerts():
    """Trigger the (async) send-alerts task."""
    from qhld_engine.alerts.send_alerts import SendAlerts

    SendAlerts()


@app.command("topic-alignment")
def topic_alignment(
    id: str | None = typer.Argument(None, help="Initiative id; omit to recompute for all."),
):
    """Recompute topic alignment for one initiative, or all when no id is given."""
    from qhld_engine.tagger.topic_alignment import calculate_topic_alignment

    calculate_topic_alignment(id)


@app.command("sil-ejecutivo")
def sil_ejecutivo(
    legislatura: str = typer.Option("66", help="Legislatura vigente en el SIL."),
    html_file: str | None = typer.Option(
        None, "--html-file", help="Ruta a un HTML del SIL (offline); omite la descarga."
    ),
):
    """Sincroniza iniciativas del Ejecutivo Federal desde el SIL (Huella 2030).

    Alimenta la colección `executive_initiatives` preservando la codificación
    ODS/metas existente. Reporta el desglose por sección
    (Aprobadas/Pendientes/Desechadas/Retiradas).
    """
    from qhld_engine.extractors.mexico.sil_ejecutivo import SECCIONES, sync_sil_ejecutivo

    html = None
    if html_file:
        with open(html_file, encoding="latin-1") as fh:
            html = fh.read()

    res = sync_sil_ejecutivo(legislatura=legislatura, html=html)
    typer.echo(f"SIL Ejecutivo — corte {res['corte']} — total {res['total']}")
    for seccion in SECCIONES:
        typer.echo(f"  {res['por_seccion'].get(seccion, 0):>3}  {seccion}")


@app.command("iniclave-minutas")
def iniclave_minutas(
    csv_path: str = typer.Option(None, "--csv", help="CSV crudo del iniclave (offline); omite para el semilla."),
    legislatura: str = typer.Option("LXVI", help="Legislatura vigente."),
):
    """Sincroniza minutas de la Cámara de Diputados desde el iniclave (Huella v3).

    Alimenta la colección `minutas` preservando codificación, atribución y
    `nivel_revision` ya documentados. Verifica que la numeración de claves sea
    continua: si hay un hueco, lo reporta (no lo silencia).
    """
    from qhld_engine.extractors.mexico.iniclave_minutas import sync_minutas

    res = sync_minutas(csv_path=csv_path, legislatura=legislatura)
    typer.echo(f"Minutas — corte {res['corte']} — total {res['total']}")
    for estatus, n in sorted(res["por_estatus"].items()):
        typer.echo(f"  {n:>3}  {estatus}")
    seq = res["secuencia"]
    typer.echo(f"  secuencia: {seq['min']}–{seq['max']} ({seq['total']} claves)")
    if seq["gaps"]:
        typer.secho(f"  ⚠ HUECOS en la secuencia: {seq['gaps']}", fg="yellow")
    else:
        typer.echo("  secuencia continua, sin huecos ✓")


@app.command("minutas-coding")
def minutas_coding(
    out: str = typer.Option(None, "--out", help="Ruta de minutas_ods.csv (por defecto la canónica)."),
):
    """Codifica las minutas por ODS/metas (herencia + LLM) y exporta minutas_ods.csv.

    Herencia gratis de las minutas cruzadas con el Ejecutivo; LLM (config LLM_*)
    para el resto (mock = línea base sin clave). Preserva filas validado_autora.
    """
    from qhld_engine.normtrace.minutas_coding import export_coding

    res = export_coding(out_path=out)
    typer.echo(
        f"minutas_ods.csv — {res['total']} minutas "
        f"({res['heredadas']} heredadas, {res['por_llm']} por LLM/mock, "
        f"{res['validadas_preservadas']} validadas preservadas)"
    )
    if res["verificacion_manual"]:
        typer.secho(
            f"  {len(res['verificacion_manual'])} matches con score < 0.75 a verificar a mano: "
            f"{', '.join(res['verificacion_manual'][:8])}"
            + ("…" if len(res['verificacion_manual']) > 8 else ""),
            fg="yellow",
        )


@app.command("normtrace-atribucion")
def normtrace_atribucion(
    base_url: str = typer.Option(None, "--base-url", help="Base de los PDFs del iniclave."),
    limit: int = typer.Option(None, "--limit", help="Máximo de minutas a procesar por corrida."),
):
    """Atribuye grupo parlamentario a las minutas leyendo el dictamen (job incremental).

    Solo minutas sin origen documentado; nunca pisa `validado_autora` ni inventa
    atribución (lo no parseable queda "por documentar").
    """
    from qhld_engine.normtrace.atribucion import run_atribucion

    res = run_atribucion(base_url=base_url, limit=limit)
    typer.echo(
        f"Atribución — {res['procesadas']} procesadas: "
        f"{res['atribuidas']} atribuidas, {res['sin_dictamen']} sin dictamen, "
        f"{res['por_documentar']} quedan por documentar."
    )


@app.command("normtrace-run")
def normtrace_run(
    iniciativa: str = typer.Option(None, "--iniciativa", help="Id de la iniciativa/ley."),
    marco: str = typer.Option("ods6", "--marco", help="Marco de estándares (ods6|...)."),
    text_file: str = typer.Option(None, "--text-file", help="Texto local (offline); omite la descarga."),
    out: str = typer.Option(None, "--out", help="Ruta para guardar la corrida JSON."),
):
    """Corre el protocolo NormTrace (nivel 3) sobre una ley contra un marco.

    Descarga el texto (LeyesBiblio), lo segmenta y codifica por estándar con el
    LLM configurado (LLM_PROVIDER; 'mock' por defecto produce una línea base
    preliminar sin clave). Toda salida nace 'automatico_preliminar'.
    """
    import json as _json

    from qhld_engine.normtrace.runner import run as nt_run

    result = nt_run(iniciativa, marco, text_file=text_file)
    payload = _json.dumps(result, ensure_ascii=False, indent=2)
    if out:
        from pathlib import Path as _P
        _P(out).write_text(payload, encoding="utf-8")
        typer.echo(f"Corrida guardada en {out} — {len(result['registros'])} registros "
                   f"({result['nivel_revision']}).")
    else:
        typer.echo(payload)


@app.command("normtrace-eval")
def normtrace_eval(
    run_file: str = typer.Option(None, "--run", help="Corrida automática a evaluar; omitir para autochequeo del dorado."),
    marco: str = typer.Option("ods6", "--marco", help="Marco (solo ods6 tiene dorado)."),
):
    """Evalúa una corrida contra el ejemplo dorado (candado de calidad).

    Sin `--run` hace autochequeo del dorado (resolución de citas 100% y cobertura
    100%): así CI verifica la integridad del contrato sin necesitar clave LLM. Con
    `--run` aplica los cinco umbrales a la corrida automática. Sale con código de
    error si reprueba.
    """
    import json as _json

    from qhld_engine.normtrace.evaluator import evaluate, format_report
    from qhld_engine.normtrace.gold import gold_run

    if run_file:
        run = _json.loads(open(run_file, encoding="utf-8").read())
    else:
        run = gold_run()  # autochequeo: el dorado como corrida validada

    report = evaluate(run)
    typer.echo(format_report(report))
    if not report["aprueba"]:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
