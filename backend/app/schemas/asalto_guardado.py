"""Esquemas para leer fines de semana de asaltos ya guardados en nuestra base de datos."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AtaqueAsaltoGuardadoOut(BaseModel):
    """Un ataque de asalto, tal como quedó guardado."""

    model_config = ConfigDict(from_attributes=True)

    atacante_tag: str
    atacante_nombre: str
    estrellas: int
    destruccion: int


class DistritoAsaltoGuardadoOut(BaseModel):
    """Un distrito, tal como quedó guardado."""

    model_config = ConfigDict(from_attributes=True)

    distrito_id_juego: int
    nombre: str
    nivel: int
    destruccion: int
    estrellas: int
    ataques_usados: int
    saqueado: int
    ataques: list[AtaqueAsaltoGuardadoOut]


class RegistroAsaltoGuardadoOut(BaseModel):
    """Un registro de enfrentamiento contra un clan, tal como quedó guardado."""

    model_config = ConfigDict(from_attributes=True)

    sentido: str
    clan_tag: str
    clan_nombre: str
    clan_nivel: int
    ataques_usados: int
    distritos_totales: int
    distritos_destruidos: int
    distritos: list[DistritoAsaltoGuardadoOut]


class MiembroAsaltoGuardadoOut(BaseModel):
    """Un miembro propio, tal como quedó guardado."""

    model_config = ConfigDict(from_attributes=True)

    tag: str
    nombre: str
    ataques_usados: int
    limite_ataques: int
    ataques_bono: int
    oro_capital_saqueado: int


class AsaltoResumenOut(BaseModel):
    """Resumen de un fin de semana de asaltos guardado, sin miembros ni registros."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    estado: str
    inicio: datetime
    fin: datetime | None
    oro_capital_total: int
    asaltos_completados: int
    ataques_totales: int
    distritos_rivales_destruidos: int
    recompensa_ofensiva: int
    recompensa_defensiva: int
    ultima_actualizacion_en: datetime


class AsaltoDetalleOut(AsaltoResumenOut):
    """Un fin de semana de asaltos guardado, con el detalle completo."""

    miembros: list[MiembroAsaltoGuardadoOut]
    registros: list[RegistroAsaltoGuardadoOut]