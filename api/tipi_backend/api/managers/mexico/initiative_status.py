class InitiativeStatusManager():
    """Estados del trámite legislativo mexicano (Congreso de la Unión).

    Sigue el flujo descrito en docs/TROPICALIZACION.md:
    presentada → turnada a comisión → dictaminada (primera lectura) →
    discusión y votación en pleno → minuta a cámara revisora → aprobada →
    publicada en el DOF, con las ramas adicionales del proceso real. El
    catálogo del SIL es la fuente de verdad para la ingesta futura; este
    listado se alinea con él en lo esencial.
    """

    def __init__(self):
        self.all_status = [
                'Presentada',
                'Turnada a comisión',
                'En comisiones unidas',
                'Con prórroga',
                'Dictaminada (primera lectura)',
                'Discusión y votación en el pleno',
                'Aprobada por la cámara de origen',
                'Minuta en cámara revisora',
                'Aprobada',
                'Publicada en el DOF',
                'Desechada',
                'Retirada',
                'Precluida',
                ]

    def get_values(self):
        return self.all_status
