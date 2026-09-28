"""Endpoints relacionados con los miembros del clan."""

from fastapi import APIRouter

from app.schemas.miembro import MiembroOut
from app.services.clash_client import ClashClient

# Todas las rutas de este archivo comparten el prefijo /miembros y se
# agrupan bajo la etiqueta "miembros" en la documentación automática.
router = APIRouter(prefix="/miembros", tags=["miembros"])


@router.get("")
async def listar_miembros() -> list[MiembroOut]:
    """Devuelve la lista actual de miembros, consultada en vivo a Supercell."""
    cliente = ClashClient()
    clan = await cliente.obtener_clan()
    return MiembroOut.lista_desde_clan(clan)