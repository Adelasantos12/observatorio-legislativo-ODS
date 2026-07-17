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


if __name__ == "__main__":
    app()
