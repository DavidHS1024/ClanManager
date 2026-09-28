"""Esquemas de datos de las capturas históricas del clan."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.miembro import MiembroOut


class CapturaOut(BaseModel):
    """Resumen de una captura, sin el detalle de cada miembro."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    capturado_en: datetime
    nombre_clan: str
    nivel_clan: int
    total_miembros: int


class CapturaDetalleOut(CapturaOut):
    """Una captura junto con el estado de cada miembro en ese momento."""

    miembros: list[MiembroOut]