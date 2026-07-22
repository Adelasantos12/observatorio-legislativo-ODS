"""Extractor de iniciativas de la Gaceta Parlamentaria (México).

Modelado sobre `paraguay/initiatives.py`, pero la Gaceta es HTML (no API): por
cada día publica una página (y anexos I, II, …) con las iniciativas inline. Este
extractor recorre la página del día y sus anexos, parsea con `gaceta.py` y crea o
actualiza los documentos `Initiative`. La descarga real ocurre en `gaceta.fetch_*`
(aislada), de modo que la lógica de ingesta es testeable con HTML de fixture.
"""

from datetime import datetime

from tipi_data.models.initiative import Initiative
from tipi_data.repositories.initiatives import Initiatives

from qhld_engine.logger import get_logger
from qhld_engine.infrastructure.config.settings import get_settings
from . import gaceta

log = get_logger(__name__)

# Anexos habituales de una Gaceta (además de la página principal sin anexo).
DEFAULT_ANEXOS = [None, "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]


class InitiativesExtractor:
    def __init__(self):
        settings = get_settings()
        self.legislatura = getattr(settings, "gaceta_legislatura", "66")
        self.date = getattr(settings, "gaceta_date", "") or datetime.today().strftime("%Y%m%d")
        self.all_references = []

    # --- Interfaz usada por ExtractorTask ---------------------------------

    def extract(self):
        """Ingesta la Gaceta del día configurado (`gaceta_date`) y sus anexos."""
        for anexo in DEFAULT_ANEXOS:
            url = gaceta.build_url(self.date, self.legislatura, anexo)
            html = gaceta.fetch_gaceta(url)
            if not html:
                continue
            self.ingest_html(html, url)

    def ingest_html(self, html, url=""):
        """Parsea un HTML de Gaceta ya descargado y persiste sus iniciativas.

        Separado de la descarga para poder testear la ingesta con fixtures.
        """
        for ini in gaceta.parse_gaceta(html):
            try:
                self._create_or_update(ini, url)
            except Exception as e:  # noqa: BLE001
                log.warning("Iniciativa {}: {}".format(ini.ref, e))

    def _create_or_update(self, ini, url=""):
        reference = "{}-{}".format(self.date, ini.ref)
        try:
            initiative = Initiatives.get(reference)
        except Exception:
            initiative = Initiative(id="")
        initiative["id"] = reference
        initiative["reference"] = reference
        initiative["title"] = ini.title
        initiative["initiative_type"] = "Iniciativa con proyecto de decreto"
        initiative["status"] = "Presentada"
        initiative["place"] = "Cámara de Diputados"
        initiative["url"] = url
        initiative["content"] = ini.content or [""]
        if ini.author:
            initiative["author_deputies"] = [ini.author]
        if ini.party:
            initiative["author_parliamentarygroups"] = [ini.party]
        initiative["created"] = self._parse_date(self.date)
        initiative["updated"] = self._parse_date(self.date)
        if not initiative.extra:
            initiative["extra"] = dict()
        initiative["extra"]["source"] = "gaceta"
        initiative.untag()
        Initiatives.save(initiative)
        log.info("Iniciativa {} procesada".format(reference))

    @staticmethod
    def _parse_date(yyyymmdd):
        try:
            return datetime(int(yyyymmdd[0:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:8]))
        except (ValueError, IndexError):
            return None

    # --- Métodos de referencia (no aplican a la Gaceta diaria) -------------

    def extract_references(self):
        self.all_references = []

    def extract_initiatives(self):
        self.extract()
