"""Motor de base de datos y sesiones asíncronas."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# El motor administra el conjunto de conexiones a PostgreSQL. Se crea una
# sola vez y lo comparte toda la aplicación.
motor = create_async_engine(settings.database_url)

# Fábrica de sesiones. Con expire_on_commit=False los objetos siguen siendo
# legibles después de confirmar una transacción, algo necesario en código
# asíncrono, donde recargarlos de forma implícita provocaría un error.
FabricaSesion = async_sessionmaker(motor, expire_on_commit=False)


async def obtener_sesion() -> AsyncIterator[AsyncSession]:
    """Dependencia de FastAPI: entrega una sesión por petición y la cierra al terminar."""
    async with FabricaSesion() as sesion:
        yield sesion