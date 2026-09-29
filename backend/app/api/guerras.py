"""Endpoints relacionados con las guerras de clanes."""

from fastapi import APIRouter, Query

from app.api.dependencias import ClienteClash
from app.schemas.guerra import GuerraActualOut, GuerraRegistroOut

router = APIRouter(prefix="/guerras", tags=["guerras"])


@router.get("/actual")
async def guerra_actual(cliente: ClienteClash) -> GuerraActualOut:
    """
    Devuelve la guerra clásica en curso, consultada en vivo a Supercell.

    Si el clan no está en guerra en este momento, el resultado trae
    estado "notInWar" y el resto de los campos en null.
    """
    datos = await cliente.obtener_guerra_actual()
    return GuerraActualOut.desde_api(datos)


@router.get("/registro")
async def registro_guerras(
    cliente: ClienteClash, limite: int = Query(default=10, ge=1, le=50)
) -> list[GuerraRegistroOut]:
    """
    Devuelve el historial resumido de guerras pasadas.

    Requiere que el clan tenga su registro de guerra en público; si está
    privado, Supercell responde con error y esta llamada falla con un 502.
    """
    datos = await cliente.obtener_registro_guerras(limite)
    return GuerraRegistroOut.lista_desde_api(datos)