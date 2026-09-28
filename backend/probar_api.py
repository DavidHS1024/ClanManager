"""
probar_api.py

Primer script de ClanManager: comprueba que podemos leer los datos
básicos del clan desde Python, pasando por el proxy de RoyaleAPI.

Uso:
    python probar_api.py
"""

import os
import sys
from urllib.parse import quote

import httpx
from dotenv import load_dotenv

# URL base del proxy de RoyaleAPI, que reemplaza a api.clashofclans.com.
# Se define como constante para poder cambiarla en un solo lugar.
BASE_URL = "https://cocproxy.royaleapi.dev/v1"

# Segundos máximos de espera por la respuesta de la API.
TIMEOUT_SEGUNDOS = 10.0


def normalizar_tag(tag: str) -> str:
    """Devuelve el tag en mayúsculas y siempre con '#' al inicio."""
    tag = tag.strip().upper()
    return tag if tag.startswith("#") else f"#{tag}"


def cargar_configuracion() -> tuple[str, str]:
    """
    Lee el token y el tag del clan desde el archivo .env.

    Devuelve:
        Una tupla (token, tag) con el tag ya normalizado.

    Termina el programa con un mensaje claro si falta alguna variable.
    """
    load_dotenv()

    token = os.getenv("COC_TOKEN")
    tag = os.getenv("CLAN_TAG")

    # os.getenv devuelve None cuando la variable no existe. Validamos aquí
    # para fallar temprano y con un mensaje entendible.
    if not token or not tag:
        sys.exit("Error: faltan COC_TOKEN o CLAN_TAG en el archivo .env")

    return token, normalizar_tag(tag)


def obtener_clan(token: str, tag: str) -> dict:
    """
    Consulta los datos generales del clan en la API.

    Argumentos:
        token: token de la API de Supercell.
        tag: tag del clan con '#', sin codificar.

    Devuelve:
        Diccionario con la información del clan.
    """
    # El '#' marca el inicio del fragmento dentro de una URL, así que debe
    # viajar codificado como %23. La codificación se hace solo al armar la
    # URL, para conservar el tag limpio en el resto del programa.
    url = f"{BASE_URL}/clans/{quote(tag)}"
    encabezados = {"Authorization": f"Bearer {token}"}

    try:
        respuesta = httpx.get(url, headers=encabezados, timeout=TIMEOUT_SEGUNDOS)
    except httpx.RequestError as error:
        # No hubo respuesta: fallo de red, DNS o tiempo de espera agotado.
        sys.exit(f"Error de conexión con la API: {error}")

    if respuesta.status_code != 200:
        # La API sí respondió, pero rechazó o no pudo atender la petición.
        sys.exit(f"Error {respuesta.status_code} de la API: {respuesta.text}")

    return respuesta.json()


def main() -> None:
    """Punto de entrada: consulta el clan e imprime un resumen."""
    token, tag = cargar_configuracion()
    clan = obtener_clan(token, tag)

    print(f"Nombre:   {clan['name']}")
    print(f"Nivel:    {clan['clanLevel']}")
    print(f"Miembros: {clan['members']}")
    for miembro in clan["memberList"]:
        print(f"\t Miembro: {miembro['name']} - Nivel: {miembro['expLevel']} - Trofeos: {miembro['trophies']} - league: {miembro['league']['name']}")
    

if __name__ == "__main__":
    main()