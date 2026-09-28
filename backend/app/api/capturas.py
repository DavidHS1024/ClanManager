"""Endpoints para crear y consultar capturas históricas del clan."""

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencias import ClienteClash, SesionBD
from app.schemas.captura import CapturaDetalleOut, CapturaOut
from app.services import capturas as servicio_capturas

router = APIRouter(prefix="/capturas", tags=["capturas"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def crear_captura(cliente: ClienteClash, sesion: SesionBD) -> CapturaDetalleOut:
    """Consulta el estado actual del clan a Supercell y lo guarda como una nueva captura."""
    captura = await servicio_capturas.crear_captura(sesion, cliente)
    return CapturaDetalleOut.model_validate(captura)


@router.get("")
async def listar_capturas(
    sesion: SesionBD, limite: int = Query(default=20, ge=1, le=200)
) -> list[CapturaOut]:
    """Devuelve las capturas más recientes, de la más nueva a la más antigua."""
    capturas = await servicio_capturas.listar_capturas(sesion, limite)
    return [CapturaOut.model_validate(c) for c in capturas]


@router.get("/{captura_id}")
async def obtener_captura(captura_id: int, sesion: SesionBD) -> CapturaDetalleOut:
    """Devuelve el detalle de una captura, con el estado de cada miembro."""
    captura = await servicio_capturas.obtener_captura(sesion, captura_id)
    if captura is None:
        raise HTTPException(status_code=404, detail="Captura no encontrada")
    return CapturaDetalleOut.model_validate(captura)