"""Iniciativa del Ejecutivo Federal codificada por ODS/metas (Huella 2030, fase H).

Colección `executive_initiatives`. La codificación (`ods_*`, `metas`, `tema`,
`confianza`) es preliminar y revisable; `confianza` puede ser
`alta|media|baja|pendiente`. Una iniciativa nueva sin codificar entra como
`confianza="pendiente"` y se muestra como "sin codificar", nunca oculta.
"""

from datetime import datetime

from pydantic import Field

from tipi_data.models.base import MongoModel


class ExecutiveInitiative(MongoModel):
    seccion: str | None = None
    num: int | None = None
    denominacion: str | None = None
    fecha_presentacion: str | None = None
    fecha_dof: str | None = None
    estatus: str | None = None
    ods_principal: str | None = None          # p. ej. "16" (o None si sin codificar)
    ods_secundarios: list[str] = Field(default_factory=list)
    tema: str | None = None
    confianza: str | None = None              # alta|media|baja|pendiente
    metas: list[str] = Field(default_factory=list)  # p. ej. ["16.3","16.6"]
    updated_at: datetime | None = None

    def __str__(self):
        return f"{self.id} — {self.denominacion}"
