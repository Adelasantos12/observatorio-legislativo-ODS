"""Extractor de miembros (México).

La Gaceta Parlamentaria no expone un feed de diputadas y diputados; la autoría se
deriva del string del título de cada iniciativa (ver `gaceta.parse_title`). Se
deja como no-op para satisfacer la interfaz de `ExtractorTask`; un feed de
integrantes (p. ej. del SIL o del directorio de la Cámara) puede añadirse después.
"""

from qhld_engine.logger import get_logger

log = get_logger(__name__)


class MembersExtractor:
    def __init__(self):
        pass

    def extract(self):
        log.info("MembersExtractor(mexico): sin feed de miembros; se omite.")
