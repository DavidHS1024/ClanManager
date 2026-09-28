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
    # Puede faltar si el jugador aún no tiene liga asignada.
    liga: str | None = None

    @classmethod
    def desde_api(cls, datos: dict) -> "MiembroOut":
        """
        Construye un miembro a partir del diccionario crudo de Supercell.

        Este es el único lugar que conoce los nombres de campo de la API
        externa. Si Supercell los cambia, solo hay que corregir aquí.
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
            liga=(datos.get("league") or {}).get("name"),
        )