"""Dependencias reutilizables para los endpoints de FastAPI."""

from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.sesion import obtener_sesion
from app.services.clash_client import ClashClient


def obtener_cliente_clash(request: Request) -> ClashClient:
    """Entrega el cliente de Clash of Clans creado al arrancar el servidor."""
    return request.app.state.clash


# Alias que permiten declarar cada dependencia con una sola palabra en los
# parámetros de un endpoint: `cliente: ClienteClash`, `sesion: SesionBD`.
ClienteClash = Annotated[ClashClient, Depends(obtener_cliente_clash)]
SesionBD = Annotated[AsyncSession, Depends(obtener_sesion)]