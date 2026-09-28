"""Endpoints relacionados con los miembros del clan."""

from fastapi import APIRouter

from app.schemas.miembro import MiembroOut
from app.api.dependencias import ClienteClash

# Todas las rutas de este archivo comparten el prefijo /miembros y se
# agrupan bajo la etiqueta "miembros" en la documentación automática.
router = APIRouter(prefix="/miembros", tags=["miembros"])

@router.get("")
async def listar_miembros(cliente: ClienteClash) -> list[MiembroOut]:
    """Devuelve la lista actual de miembros, consultada en vivo a Supercell."""
    clan = await cliente.obtener_clan()
    return MiembroOut.lista_desde_clan(clan)