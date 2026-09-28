"""
Cliente asíncrono para la API de Clash of Clans.

Todo el código que necesite datos del clan pasa por esta clase, de modo que
la URL base, la autenticación y el manejo de errores viven en un solo lugar.
"""

from urllib.parse import quote

import httpx

from app.config import settings


class ClashApiError(Exception):
    """Error al contactar la API de Clash of Clans o devuelto por ella."""

    def __init__(self, mensaje: str, status_code: int | None = None) -> None:
        super().__init__(mensaje)
        self.status_code = status_code


def normalizar_tag(tag: str) -> str:
    """Devuelve el tag en mayúsculas y siempre con '#' al inicio."""
    tag = tag.strip().upper()
    return tag if tag.startswith("#") else f"#{tag}"


class ClashClient:
    """Cliente para consultar la API de Clash of Clans a través del proxy."""

    def __init__(self) -> None:
        self._clan_tag = normalizar_tag(settings.clan_tag)
        self._encabezados = {"Authorization": f"Bearer {settings.coc_token}"}

    async def _get(self, ruta: str) -> dict:
        """
        Hace una petición GET a la API y devuelve el JSON de la respuesta.

        Lanza ClashApiError si no hay conexión o si la API responde con error.
        """
        url = f"{settings.coc_base_url}{ruta}"

        try:
            async with httpx.AsyncClient(timeout=settings.coc_timeout) as cliente:
                respuesta = await cliente.get(url, headers=self._encabezados)
        except httpx.RequestError as error:
            raise ClashApiError(f"No se pudo conectar con la API: {error}") from error

        if respuesta.status_code != 200:
            raise ClashApiError(
                f"La API respondió con error: {respuesta.text}",
                status_code=respuesta.status_code,
            )

        return respuesta.json()

    async def obtener_clan(self) -> dict:
        """
        Detalle completo del clan: datos generales y lista de miembros.

        Una sola llamada trae tanto las estadísticas del clan como
        memberList, con la liga actual de cada miembro, de modo que todo
        proviene del mismo instante.
        """
        return await self._get(f"/clans/{quote(self._clan_tag)}")