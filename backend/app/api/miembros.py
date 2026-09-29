"""Endpoints relacionados con los miembros del clan."""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.api.dependencias import ClienteClash, SesionBD
from app.schemas.evolucion import EvolucionOut
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

@router.get("/evolucion")
async def evolucion_miembros(sesion: SesionBD, desde: datetime, hasta: datetime) -> EvolucionOut:
    """
    Compara el estado de cada miembro entre la captura más cercana a
    'desde' y la más cercana a 'hasta'.
    """
    if hasta <= desde:
        raise HTTPException(status_code=400, detail="'hasta' debe ser posterior a 'desde'")

    captura_inicial = await servicio_capturas.obtener_captura_desde(sesion, desde)
    captura_final = await servicio_capturas.obtener_captura_hasta(sesion, hasta)

    if captura_inicial is None:
        raise HTTPException(status_code=404, detail="No hay capturas en o después de 'desde'")
    if captura_final is None:
        raise HTTPException(status_code=404, detail="No hay capturas en o antes de 'hasta'")

    miembros = servicio_capturas.calcular_evolucion(captura_inicial, captura_final)
    return EvolucionOut(
        captura_inicial_en=captura_inicial.capturado_en,
        captura_final_en=captura_final.capturado_en,
        miembros=miembros,
    )