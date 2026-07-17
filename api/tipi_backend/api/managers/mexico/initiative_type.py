class InitiativeTypeManager():
    """Tipos de asunto legislativo del Congreso de la Unión (México).

    Modelado sobre la plantilla de `paraguay/`. Los nombres siguen la
    terminología de la Cámara de Diputados / Senado (ver docs/TROPICALIZACION.md).
    """

    def __init__(self):
        self.types = [
                'Iniciativa con proyecto de decreto',
                'Iniciativa de reforma constitucional',
                'Iniciativa del Ejecutivo Federal',
                'Iniciativa de diputadas y diputados',
                'Iniciativa de senadoras y senadores',
                'Iniciativa de congreso local',
                'Iniciativa ciudadana',
                'Proposición con punto de acuerdo',
                'Minuta',
                ]

    def get_values(self):
        return self.types

    def get_search_for(self, type):
        return {'initiative_type': {'$regex': type, '$options': 'gi'}}
