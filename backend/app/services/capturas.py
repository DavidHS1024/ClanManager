"""Servicio para crear y consultar capturas históricas del clan."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.captura import Captura, CapturaMiembro
from app.schemas.miembro import MiembroOut
from app.services.clash_client import ClashClient


async def crear_captura(sesion: AsyncSession, cliente: ClashClient) -> Captura:
    """Consulta el estado actual del clan y lo guarda como una nueva captura."""
    clan = await cliente.obtener_clan()

    captura = Captura(
        tag_clan=clan["tag"],
        nombre_clan=clan["name"],
        nivel_clan=clan["clanLevel"],
        total_miembros=clan["members"],
        miembros=[
            CapturaMiembro(**MiembroOut.desde_api(datos).model_dump())
            for datos in clan["memberList"]
        ],
    )

    sesion.add(captura)
    await sesion.commit()
    return captura


async def listar_capturas(sesion: AsyncSession, limite: int) -> list[Captura]:
    """Devuelve las capturas más recientes, de la más nueva a la más antigua."""
    resultado = await sesion.execute(
        select(Captura).order_by(Captura.capturado_en.desc()).limit(limite)
    )
    return list(resultado.scalars().all())


async def obtener_captura(sesion: AsyncSession, captura_id: int) -> Captura | None:
    """Devuelve una captura por id, con sus miembros ya cargados."""
    resultado = await sesion.execute(
        select(Captura)
        .where(Captura.id == captura_id)
        .options(selectinload(Captura.miembros))
    )
    return resultado.scalar_one_or_none()