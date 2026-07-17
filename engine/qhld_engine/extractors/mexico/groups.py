"""Extractor de grupos parlamentarios (México).

Los grupos se derivan del string del título de cada iniciativa (Grupo
Parlamentario X). No hay un feed dedicado en la Gaceta, así que estos métodos son
no-op, igual que en la plantilla de `paraguay/groups.py`.
"""

from qhld_engine.logger import get_logger

log = get_logger(__name__)


class GroupsExtractor:
    def __init__(self):
        pass

    def extract(self):
        pass

    def load(self, groups_file):
        pass

    def calculate_composition(self):
        log.info("GroupsExtractor(mexico): composición derivada de las iniciativas.")
