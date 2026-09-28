"""Esquemas de datos de los miembros del clan."""

from pydantic import BaseModel


class MiembroOut(BaseModel):
    """Miembro del clan tal como lo devuelve nuestra API al frontend."""

    tag: str
    nombre: str
    rol: str
    nivel_experiencia: int
    nivel_ayuntamiento: int
    trofeos: int
    donaciones: int
    donaciones_recibidas: int
    # Liga actual del sistema de batallas clasificatorias.
    # Puede faltar si el jugador no tiene liga asignada.
    liga: str | None = None

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
        )

    @classmethod
    def lista_desde_clan(cls, clan: dict) -> list["MiembroOut"]:
        """Construye la lista de miembros a partir del detalle completo del clan."""
        return [cls.desde_api(miembro) for miembro in clan["memberList"]]