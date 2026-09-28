"""
Punto de entrada de la API de ClanManager.

Para ejecutarla en desarrollo, desde la carpeta backend:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import miembros
from app.services.clash_client import ClashApiError

app = FastAPI(
    title="ClanManager API",
    description="API para consultar y analizar la actividad de un clan de Clash of Clans.",
    version="0.1.0",
)

app.include_router(miembros.router, prefix="/api")


@app.exception_handler(ClashApiError)
async def manejar_error_clash(_: Request, error: ClashApiError) -> JSONResponse:
    """
    Traduce los errores de la API de Supercell a una respuesta HTTP propia.

    Se usa 502 (Bad Gateway) porque nuestro servidor funcionó, pero falló
    el servicio externo del que depende. Devolver el 403 o el 404 original
    confundiría al frontend, que pensaría que el problema es suyo.
    """
    return JSONResponse(
        status_code=502,
        content={"detalle": str(error), "estado_origen": error.status_code},
    )


@app.get("/salud", tags=["sistema"])
async def salud() -> dict:
    """Comprobación de vida del servicio, útil luego para el despliegue."""
    return {"estado": "ok"}