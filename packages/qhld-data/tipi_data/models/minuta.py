"""Minuta de la Cámara de Diputados como cámara de origen (Huella 2030, módulo B).

Colección `minutas`. Una minuta es un asunto aprobado por la Cámara de Diputados
(cámara de origen) y turnado al Senado. Este módulo agrega las minutas por su
**origen de autoría** (grupo parlamentario o Ejecutivo Federal) para mostrar la
*aportación por origen* a la Agenda 2030.

IMPORTANTE (regla no negociable del proyecto): el desglose por origen es
descriptivo — quién impulsó cada asunto — y NUNCA un ranking competitivo entre
bancadas. Cuando el origen no está documentado, `origen` es `None` y el frontend
lo muestra como "por documentar"; jamás se inventa una atribución.

La codificación (`ods_*`, `metas`, `tema`, `confianza`) es preliminar y revisable
(protocolo NormTrace) y se edita vía `minutas_ods.csv`.
"""

from datetime import datetime

from pydantic import Field

from tipi_data.models.base import MongoModel


class Minuta(MongoModel):
    clave: str | None = None                  # p. ej. "CD-LXVI-II-2P-139"
    legislatura: str | None = None            # p. ej. "LXVI"
    anio: str | None = None                   # año legislativo, p. ej. "II"
    periodo: str | None = None                # p. ej. "2P"
    numero: int | None = None
    denominacion: str | None = None
    fecha_presentacion: str | None = None
    fecha_aprobacion: str | None = None
    origen: str | None = None                 # grupo parlamentario | "Ejecutivo Federal" | None
    estatus: str | None = None
    expediente_ref: str | None = None         # id de executive_initiative si aplica
    ods_principal: str | None = None
    ods_secundarios: list[str] = Field(default_factory=list)
    tema: str | None = None
    confianza: str | None = None              # alta|media|baja|pendiente
    metas: list[str] = Field(default_factory=list)
    updated_at: datetime | None = None

    def __str__(self):
        return f"{self.id} — {self.denominacion}"
