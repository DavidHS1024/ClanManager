"""Programador de capturas automáticas del clan."""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.db.sesion import FabricaSesion
from app.services import capturas as servicio_capturas
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


def crear_programador(cliente: ClashClient) -> AsyncIOScheduler:
    """
    Crea el programador con la tarea de captura ya registrada.

    No lo inicia: quien lo crea decide cuándo llamar a .start() y .shutdown().
    """
    programador = AsyncIOScheduler()
    programador.add_job(
        capturar_periodicamente,
        trigger=IntervalTrigger(minutes=settings.captura_intervalo_minutos),
        args=[cliente],
        id="captura_periodica",
        # Si el servidor estuvo apagado y se pasó la hora, ejecuta una sola
        # vez al reanudar en vez de encadenar varias capturas atrasadas.
        coalesce=True,
        # Evita que una captura que tarda mucho se solape con la siguiente.
        max_instances=1,
    )
    return programador