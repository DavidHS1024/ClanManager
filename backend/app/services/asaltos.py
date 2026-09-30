"""Servicio para guardar y actualizar el registro del fin de semana de asaltos."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.asalto import AsaltoAtaque, AsaltoCapital, AsaltoDistrito, AsaltoMiembro, AsaltoRegistro
from app.schemas.asalto import AsaltoOut, RegistroCapitalOut
from app.services.clash_client import ClashClient


async def guardar_asalto_actual(sesion: AsyncSession, cliente: ClashClient) -> AsaltoCapital | None:
    """
    Consulta el fin de semana de asaltos más reciente y guarda o actualiza
    su registro.

    Se identifica por su fecha de inicio, única para cada fin de semana.
    Si Supercell todavía no tiene ningún fin de semana registrado para
    este clan, devuelve None.
    """
    items = await cliente.obtener_asaltos_capital(limite=1)
    if not items:
        return None

    asalto_actual = AsaltoOut.desde_api(items[0])
    if asalto_actual.inicio is None:
        return None

    resultado = await sesion.execute(
        select(AsaltoCapital)
        .where(AsaltoCapital.inicio == asalto_actual.inicio)
        .options(
            selectinload(AsaltoCapital.miembros),
            selectinload(AsaltoCapital.registros)
            .selectinload(AsaltoRegistro.distritos)
            .selectinload(AsaltoDistrito.ataques),
        )
    )
    asalto = resultado.scalar_one_or_none()

    if asalto is None:
        asalto = AsaltoCapital(inicio=asalto_actual.inicio)
        sesion.add(asalto)
    else:
        # Misma razón que en guerras: reconstruir desde cero es más simple
        # y más seguro que aplicar solo lo que cambió, y el flush() evita
        # que el borrado de las filas viejas choque con la inserción de
        # las nuevas dentro del mismo flush.
        asalto.miembros.clear()
        asalto.registros.clear()
        await sesion.flush()

    asalto.estado = asalto_actual.estado
    asalto.fin = asalto_actual.fin
    asalto.oro_capital_total = asalto_actual.oro_capital_total
    asalto.asaltos_completados = asalto_actual.asaltos_completados
    asalto.ataques_totales = asalto_actual.ataques_totales
    asalto.distritos_rivales_destruidos = asalto_actual.distritos_rivales_destruidos
    asalto.recompensa_ofensiva = asalto_actual.recompensa_ofensiva
    asalto.recompensa_defensiva = asalto_actual.recompensa_defensiva

    for miembro in asalto_actual.miembros:
        asalto.miembros.append(
            AsaltoMiembro(
                tag=miembro.tag,
                nombre=miembro.nombre,
                ataques_usados=miembro.ataques_usados,
                limite_ataques=miembro.limite_ataques,
                ataques_bono=miembro.ataques_bono,
                oro_capital_saqueado=miembro.oro_capital_saqueado,
            )
        )

    for sentido, lista in (
        ("ofensivo", asalto_actual.ataques_realizados),
        ("defensivo", asalto_actual.ataques_recibidos),
    ):
        for registro_datos in lista:
            asalto.registros.append(_construir_registro(registro_datos, sentido))

    await sesion.commit()
    return asalto


def _construir_registro(registro: RegistroCapitalOut, sentido: str) -> AsaltoRegistro:
    """Arma un AsaltoRegistro con sus distritos y ataques, sin tocar la base de datos."""
    fila = AsaltoRegistro(
        sentido=sentido,
        clan_tag=registro.clan_tag,
        clan_nombre=registro.clan_nombre,
        clan_nivel=registro.clan_nivel,
        ataques_usados=registro.ataques_usados,
        distritos_totales=registro.distritos_totales,
        distritos_destruidos=registro.distritos_destruidos,
    )
    for distrito in registro.distritos:
        fila_distrito = AsaltoDistrito(
            distrito_id_juego=distrito.id,
            nombre=distrito.nombre,
            nivel=distrito.nivel,
            destruccion=distrito.destruccion,
            estrellas=distrito.estrellas,
            ataques_usados=distrito.ataques_usados,
            saqueado=distrito.saqueado,
        )
        for ataque in distrito.ataques:
            fila_distrito.ataques.append(
                AsaltoAtaque(
                    atacante_tag=ataque.atacante_tag,
                    atacante_nombre=ataque.atacante_nombre,
                    estrellas=ataque.estrellas,
                    destruccion=ataque.destruccion,
                )
            )
        fila.distritos.append(fila_distrito)
    return fila


async def listar_asaltos(sesion: AsyncSession, limite: int) -> list[AsaltoCapital]:
    """Devuelve los fines de semana de asaltos guardados, del más reciente al más antiguo."""
    resultado = await sesion.execute(
        select(AsaltoCapital).order_by(AsaltoCapital.inicio.desc()).limit(limite)
    )
    return list(resultado.scalars().all())


async def obtener_asalto(sesion: AsyncSession, asalto_id: int) -> AsaltoCapital | None:
    """Devuelve un fin de semana de asaltos guardado por id, con todo su detalle cargado."""
    resultado = await sesion.execute(
        select(AsaltoCapital)
        .where(AsaltoCapital.id == asalto_id)
        .options(
            selectinload(AsaltoCapital.miembros),
            selectinload(AsaltoCapital.registros)
            .selectinload(AsaltoRegistro.distritos)
            .selectinload(AsaltoDistrito.ataques),
        )
    )
    return resultado.scalar_one_or_none()