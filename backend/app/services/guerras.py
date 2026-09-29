"""Servicio para guardar y actualizar el registro de la guerra actual."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.guerra import Guerra, GuerraAtaque, GuerraMiembro
from app.schemas.guerra import BandoGuerraOut, GuerraActualOut
from app.services.clash_client import ClashClient


async def guardar_guerra_actual(sesion: AsyncSession, cliente: ClashClient) -> Guerra | None:
    """
    Consulta la guerra actual y guarda o actualiza su registro.

    Si el clan no está en guerra, no hay nada que guardar y devuelve None.
    Si ya existe un registro para esa guerra, identificada por su fecha de
    inicio de preparación, se actualiza en el lugar: sus miembros y ataques
    se reemplazan por los más recientes, en vez de acumular filas
    duplicadas en cada sondeo.
    """
    datos = await cliente.obtener_guerra_actual()
    guerra_actual = GuerraActualOut.desde_api(datos)

    if guerra_actual.clan is None or guerra_actual.rival is None:
        return None
    if guerra_actual.preparacion_inicio is None:
        return None

    resultado = await sesion.execute(
        select(Guerra)
        .where(Guerra.preparacion_inicio == guerra_actual.preparacion_inicio)
        .options(selectinload(Guerra.miembros), selectinload(Guerra.ataques))
    )
    guerra = resultado.scalar_one_or_none()

    if guerra is None:
        guerra = Guerra(preparacion_inicio=guerra_actual.preparacion_inicio)
        sesion.add(guerra)
    else:
        # La API siempre entrega el estado acumulado hasta el momento, así
        # que reconstruir desde cero es más simple y más seguro que tratar
        # de aplicar solo lo que cambió. flush() fuerza a que el borrado de
        # las filas viejas se ejecute antes de insertar las nuevas: sin
        # esto, SQLAlchemy puede mandar ambas operaciones en un orden que
        # choca contra la restricción de unicidad de (guerra_id, tag).
        guerra.miembros.clear()
        guerra.ataques.clear()
        await sesion.flush()

    _actualizar_datos_generales(guerra, guerra_actual)
    _agregar_miembros_y_ataques(guerra, guerra_actual.clan, es_propio=True)
    _agregar_miembros_y_ataques(guerra, guerra_actual.rival, es_propio=False)

    await sesion.commit()
    return guerra


def _actualizar_datos_generales(guerra: Guerra, actual: GuerraActualOut) -> None:
    """Copia los campos simples de la guerra, sin tocar miembros ni ataques."""
    guerra.estado = actual.estado
    guerra.tamano_equipo = actual.tamano_equipo
    guerra.ataques_por_miembro = actual.ataques_por_miembro
    guerra.modificador_batalla = actual.modificador_batalla
    guerra.inicio = actual.inicio
    guerra.fin = actual.fin

    guerra.clan_tag = actual.clan.tag
    guerra.clan_nombre = actual.clan.nombre
    guerra.clan_nivel = actual.clan.nivel_clan
    guerra.clan_estrellas = actual.clan.estrellas
    guerra.clan_destruccion = actual.clan.destruccion
    guerra.clan_ataques_usados = actual.clan.ataques_usados
    guerra.clan_experiencia_ganada = actual.clan.experiencia_ganada

    guerra.rival_tag = actual.rival.tag
    guerra.rival_nombre = actual.rival.nombre
    guerra.rival_nivel = actual.rival.nivel_clan
    guerra.rival_estrellas = actual.rival.estrellas
    guerra.rival_destruccion = actual.rival.destruccion


def _agregar_miembros_y_ataques(guerra: Guerra, bando: BandoGuerraOut, *, es_propio: bool) -> None:
    """Agrega los miembros de un bando y los ataques que cada uno realizó."""
    for miembro in bando.miembros:
        guerra.miembros.append(
            GuerraMiembro(
                tag=miembro.tag,
                nombre=miembro.nombre,
                nivel_ayuntamiento=miembro.nivel_ayuntamiento,
                posicion_mapa=miembro.posicion_mapa,
                es_propio=es_propio,
                ataques_recibidos=miembro.ataques_recibidos,
            )
        )
        for ataque in miembro.ataques_realizados:
            guerra.ataques.append(
                GuerraAtaque(
                    orden=ataque.orden,
                    atacante_tag=ataque.atacante_tag,
                    atacante_nombre=ataque.atacante_nombre or miembro.nombre,
                    defensor_tag=ataque.defensor_tag,
                    defensor_nombre=ataque.defensor_nombre or "",
                    estrellas=ataque.estrellas,
                    destruccion=ataque.destruccion,
                    duracion_segundos=ataque.duracion_segundos,
                )
            )

async def listar_guerras(sesion: AsyncSession, limite: int) -> list[Guerra]:
    """Devuelve las guerras guardadas, de la más reciente a la más antigua."""
    resultado = await sesion.execute(
        select(Guerra).order_by(Guerra.preparacion_inicio.desc()).limit(limite)
    )
    return list(resultado.scalars().all())


async def obtener_guerra(sesion: AsyncSession, guerra_id: int) -> Guerra | None:
    """Devuelve una guerra guardada por id, con sus miembros y ataques cargados."""
    resultado = await sesion.execute(
        select(Guerra)
        .where(Guerra.id == guerra_id)
        .options(selectinload(Guerra.miembros), selectinload(Guerra.ataques))
    )
    return resultado.scalar_one_or_none()

async def ultima_guerra_conocida(sesion: AsyncSession) -> Guerra | None:
    """Devuelve la guerra más reciente que tenemos registrada, o None si no hay ninguna."""
    resultado = await sesion.execute(
        select(Guerra).order_by(Guerra.preparacion_inicio.desc()).limit(1)
    )
    return resultado.scalar_one_or_none()