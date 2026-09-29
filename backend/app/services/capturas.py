"""Servicio para crear y consultar capturas históricas del clan."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.captura import Captura, CapturaMiembro
from app.schemas.miembro import MiembroOut
from app.services.clash_client import ClashClient, normalizar_tag


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

async def historial_miembro(sesion: AsyncSession, tag: str, limite: int) -> list[CapturaMiembro]:
    """
    Devuelve el historial de un miembro a través de las capturas guardadas,
    de la más reciente a la más antigua.
    """
    resultado = await sesion.execute(
        select(CapturaMiembro)
        .join(Captura)
        .where(CapturaMiembro.tag == normalizar_tag(tag))
        .order_by(Captura.capturado_en.desc())
        .limit(limite)
        .options(selectinload(CapturaMiembro.captura))
    )
    return list(resultado.scalars().all())

async def obtener_captura_desde(sesion: AsyncSession, fecha: datetime) -> Captura | None:
    """Primera captura registrada en o después de la fecha dada."""
    resultado = await sesion.execute(
        select(Captura)
        .where(Captura.capturado_en >= fecha)
        .order_by(Captura.capturado_en.asc())
        .limit(1)
        .options(selectinload(Captura.miembros))
    )
    return resultado.scalar_one_or_none()


async def obtener_captura_hasta(sesion: AsyncSession, fecha: datetime) -> Captura | None:
    """Última captura registrada en o antes de la fecha dada."""
    resultado = await sesion.execute(
        select(Captura)
        .where(Captura.capturado_en <= fecha)
        .order_by(Captura.capturado_en.desc())
        .limit(1)
        .options(selectinload(Captura.miembros))
    )
    return resultado.scalar_one_or_none()


def calcular_evolucion(inicial: Captura, final: Captura) -> list[dict]:
    """
    Compara el estado de cada miembro entre dos capturas.

    Solo incluye a quienes están presentes en ambas; un miembro que se unió
    o salió del clan entre una captura y otra simplemente no aparece.
    """
    por_tag_inicial = {m.tag: m for m in inicial.miembros}

    evolucion = []
    for miembro_final in final.miembros:
        miembro_inicial = por_tag_inicial.get(miembro_final.tag)
        if miembro_inicial is None:
            continue

        rango_delta = None
        if miembro_inicial.rango_clan is not None and miembro_final.rango_clan is not None:
            rango_delta = miembro_inicial.rango_clan - miembro_final.rango_clan

        evolucion.append({
            "tag": miembro_final.tag,
            "nombre": miembro_final.nombre,
            "donaciones_inicial": miembro_inicial.donaciones,
            "donaciones_final": miembro_final.donaciones,
            "donaciones_delta": miembro_final.donaciones - miembro_inicial.donaciones,
            "donaciones_reinicio": miembro_final.donaciones < miembro_inicial.donaciones,
            "trofeos_inicial": miembro_inicial.trofeos,
            "trofeos_final": miembro_final.trofeos,
            "trofeos_delta": miembro_final.trofeos - miembro_inicial.trofeos,
            "trofeos_reinicio": miembro_final.trofeos < miembro_inicial.trofeos,
            "rango_clan_inicial": miembro_inicial.rango_clan,
            "rango_clan_final": miembro_final.rango_clan,
            "rango_delta": rango_delta,
        })

    return evolucion