"""Esquemas de datos de los miembros del clan."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MiembroOut(BaseModel):
    """Miembro del clan tal como lo devuelve nuestra API al frontend."""

    # Permite construir el esquema a partir de objetos de la base de datos,
    # además de a partir de diccionarios.
    model_config = ConfigDict(from_attributes=True)

    tag: str
    nombre: str
    rol: str
    nivel_experiencia: int
    nivel_ayuntamiento: int
    trofeos: int
    donaciones: int
    donaciones_recibidas: int
    # Liga actual del sistema de batallas clasificatorias. Puede faltar si
    # el jugador no tiene liga asignada.
    liga: str | None = None

    # Posición del miembro dentro del ranking interno del clan.
    rango_clan: int | None = None
    rango_clan_anterior: int | None = None
    # Aldea de constructor: null en cuentas muy antiguas, o en registros
    # guardados antes de que empezáramos a leer estos campos.
    trofeos_base: int | None = None
    liga_base: str | None = None

    @classmethod
    def desde_api(cls, datos: dict) -> "MiembroOut":
        """
        Construye un miembro a partir del diccionario crudo de Supercell.

        Esta clase es el único lugar que conoce los nombres de campo de la API externa.
        """
        return cls(
            tag=datos["tag"],
            nombre=datos["name"],
            rol=datos["role"],
            nivel_experiencia=datos["expLevel"],
            nivel_ayuntamiento=datos["townHallLevel"],
            trofeos=datos["trophies"],
            donaciones=datos["donations"],
            donaciones_recibidas=datos["donationsReceived"],
            liga=(datos.get("leagueTier") or {}).get("name"),
            rango_clan=datos.get("clanRank"),
            rango_clan_anterior=datos.get("previousClanRank"),
            trofeos_base=datos.get("builderBaseTrophies"),
            liga_base=(datos.get("builderBaseLeague") or {}).get("name"),
        )

    @classmethod
    def lista_desde_clan(cls, clan: dict) -> list["MiembroOut"]:
        """Construye la lista de miembros a partir del detalle completo del clan."""
        return [cls.desde_api(miembro) for miembro in clan["memberList"]]


class PuntoHistorialOut(MiembroOut):
    """Estado de un miembro en un momento dado de su historial de capturas."""

    capturado_en: datetime