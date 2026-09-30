"""Endpoints del Fin de Semana de Asaltos a la Capital del Clan."""

from fastapi import APIRouter, HTTPException, Query

from app.api.dependencias import ClienteClash
from app.schemas.asalto import AsaltoOut

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