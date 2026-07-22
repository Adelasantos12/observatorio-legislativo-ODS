"""Estados del trámite de una iniciativa mexicana (para el extractor).

Alineado con los estados del manager de la API
(`api/tipi_backend/api/managers/mexico/initiative_status.py`). Una iniciativa
recién publicada en la Gaceta entra como "Presentada"; el estado se actualiza si
más adelante se integra el catálogo del SIL.
"""

import re

FINAL_STATES = ["publicada en el dof", "desechada", "retirada", "precluida"]


def is_final_state(status):
    if not status:
        return False
    return any(re.search(s, status, re.IGNORECASE) for s in FINAL_STATES)


def has_finished(initiative_status):
    return is_final_state(initiative_status)
