"""Endpoints relacionados con los miembros del clan."""

from fastapi import APIRouter, HTTPException, Query

from app.api.dependencias import ClienteClash, SesionBD
from app.schemas.miembro import MiembroOut, PuntoHistorialOut
from app.services import capturas as servicio_capturas

router = APIRouter(prefix="/miembros", tags=["miembros"])


@router.get("")
async def listar_miembros(cliente: ClienteClash) -> list[MiembroOut]:
    """Devuelve la lista actual de miembros, consultada en vivo a Supercell."""
    clan = await cliente.obtener_clan()
    return MiembroOut.lista_desde_clan(clan)


@router.get("/{tag}/historial")
async def historial_miembro(
    tag: str, sesion: SesionBD, limite: int = Query(default=50, ge=1, le=500)
) -> list[PuntoHistorialOut]:
    """
    Devuelve el historial de un miembro a través de las capturas guardadas.

    El tag va sin el '#' inicial en la URL, por ejemplo /miembros/8809J8GLJ/historial.
    """
    historial = await servicio_capturas.historial_miembro(sesion, tag, limite)
    if not historial:
        raise HTTPException(status_code=404, detail="Sin historial para ese tag")
    return [PuntoHistorialOut.model_validate(cm) for cm in historial]