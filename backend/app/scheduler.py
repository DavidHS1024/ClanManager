"""Programador de capturas automáticas del clan."""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.db.sesion import FabricaSesion
from app.services import capturas as servicio_capturas
from app.services import guerras as servicio_guerras
from app.services.clash_client import ClashApiError, ClashClient

logger = logging.getLogger("clanmanager.scheduler")


async def capturar_periodicamente(cliente: ClashClient) -> None:
    """
    Tarea programada: crea una captura del clan y la guarda.

    Abre su propia sesión de base de datos, porque no hay una petición
    HTTP de la que tomarla como en los endpoints. Si la captura falla, el
    error se registra y no se propaga, para que un fallo puntual no
    detenga las capturas programadas siguientes.
    """
    async with FabricaSesion() as sesion:
        try:
            captura = await servicio_capturas.crear_captura(sesion, cliente)
        except ClashApiError as error:
            logger.error("Falló la captura automática: %s", error)
            return

    logger.info(
        "Captura automática guardada: id=%s clan=%s miembros=%s",
        captura.id, captura.nombre_clan, captura.total_miembros,
    )


async def capturar_guerra_periodicamente(cliente: ClashClient) -> None:
    """
    Tarea programada: guarda o actualiza el registro de la guerra actual.

    Si el clan no está en guerra, guardar_guerra_actual devuelve None y
    no hay nada que registrar; no es un error, así que solo se anota en
    el nivel debug para no llenar el log de líneas sin información.
    """
    async with FabricaSesion() as sesion:
        try:
            guerra = await servicio_guerras.guardar_guerra_actual(sesion, cliente)
        except ClashApiError as error:
            logger.error("Falló el sondeo de guerra: %s", error)
            return

    if guerra is None:
        logger.debug("Sondeo de guerra: el clan no está en guerra ahora mismo")
        return

    logger.info(
        "Guerra actualizada: id=%s estado=%s rival=%s estrellas=%s/%s",
        guerra.id, guerra.estado, guerra.rival_nombre, guerra.clan_estrellas, guerra.rival_estrellas,
    )


def crear_programador(cliente: ClashClient) -> AsyncIOScheduler:
    """
    Crea el programador con las tareas de captura ya registradas.

    No lo inicia: quien lo crea decide cuándo llamar a .start() y .shutdown().
    """
    programador = AsyncIOScheduler()
    programador.add_job(
        capturar_periodicamente,
        trigger=IntervalTrigger(minutes=settings.captura_intervalo_minutos),
        args=[cliente],
        id="captura_periodica",
        coalesce=True,
        max_instances=1,
    )
    programador.add_job(
        capturar_guerra_periodicamente,
        trigger=IntervalTrigger(minutes=settings.guerra_intervalo_minutos),
        args=[cliente],
        id="captura_guerra_periodica",
        coalesce=True,
        max_instances=1,
    )
    return programador