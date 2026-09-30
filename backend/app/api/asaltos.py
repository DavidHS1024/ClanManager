"""Endpoints del Fin de Semana de Asaltos a la Capital del Clan."""

from fastapi import APIRouter, HTTPException, Query

from app.api.dependencias import ClienteClash, SesionBD
from app.schemas.asalto import AsaltoOut
from app.schemas.asalto_guardado import AsaltoDetalleOut, AsaltoResumenOut
from app.services import asaltos as servicio_asaltos

router = APIRouter(prefix="/asaltos", tags=["asaltos"])


@router.get("/actual")
async def asalto_actual(cliente: ClienteClash) -> AsaltoOut:
    """Devuelve el fin de semana de asaltos más reciente, consultado en vivo a Supercell."""
    items = await cliente.obtener_asaltos_capital(limite=1)
    if not items:
        raise HTTPException(status_code=404, detail="Sin fines de semana de asaltos registrados todavía")
    return AsaltoOut.desde_api(items[0])


@router.get("")
async def listar_asaltos(
    cliente: ClienteClash, limite: int = Query(default=5, ge=1, le=25)
) -> list[AsaltoOut]:
    """
    Devuelve varios fines de semana de asaltos recientes.

    Supercell solo conserva un puñado de temporadas pasadas; una vez que
    se le acaban, simplemente devuelve menos de las que pediste.
    """
    items = await cliente.obtener_asaltos_capital(limite=limite)
    return AsaltoOut.lista_desde_api(items)

@router.get("/historial")
async def listar_asaltos_guardados(
    sesion: SesionBD, limite: int = Query(default=10, ge=1, le=100)
) -> list[AsaltoResumenOut]:
    """Devuelve los fines de semana de asaltos guardados por nuestro propio programador."""
    asaltos = await servicio_asaltos.listar_asaltos(sesion, limite)
    return [AsaltoResumenOut.model_validate(a) for a in asaltos]


@router.get("/historial/{asalto_id}")
async def obtener_asalto_guardado(asalto_id: int, sesion: SesionBD) -> AsaltoDetalleOut:
    """Devuelve el detalle completo de un fin de semana de asaltos guardado."""
    asalto = await servicio_asaltos.obtener_asalto(sesion, asalto_id)
    if asalto is None:
        raise HTTPException(status_code=404, detail="Fin de semana de asaltos no encontrado")
    return AsaltoDetalleOut.model_validate(asalto)