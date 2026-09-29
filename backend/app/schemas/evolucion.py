"""Esquemas para la evolución de los miembros entre dos capturas."""

from datetime import datetime

from pydantic import BaseModel


class EvolucionMiembroOut(BaseModel):
    """Cambios de un miembro entre dos capturas."""

    tag: str
    nombre: str

    donaciones_inicial: int
    donaciones_final: int
    donaciones_delta: int
    # True si donaciones_final < donaciones_inicial: probable reinicio
    # semanal de temporada en vez de una caída real de donaciones.
    donaciones_reinicio: bool

    trofeos_inicial: int
    trofeos_final: int
    trofeos_delta: int
    trofeos_reinicio: bool

    rango_clan_inicial: int | None
    rango_clan_final: int | None
    # Positivo si el miembro subió puestos (rango más bajo es mejor).
    rango_delta: int | None


class EvolucionOut(BaseModel):
    """Comparación del clan entre la captura más cercana a cada fecha pedida."""

    captura_inicial_en: datetime
    captura_final_en: datetime
    miembros: list[EvolucionMiembroOut]