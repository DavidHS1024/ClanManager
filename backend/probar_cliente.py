"""Prueba manual del cliente: imprime el resumen del clan y sus miembros."""

import asyncio

from app.services.clash_client import ClashApiError, ClashClient


async def main() -> None:
    cliente = ClashClient()

    try:
        clan = await cliente.obtener_clan()
        miembros = await cliente.obtener_miembros()
    except ClashApiError as error:
        print(f"Error ({error.status_code}): {error}")
        return

    print(f"Clan: {clan['name']} - Nivel {clan['clanLevel']} - {len(miembros)} miembros")
    for miembro in miembros:
        print(f"  {miembro['name']:<22} {miembro['role']:<10} Donaciones: {miembro['donations']}")


if __name__ == "__main__":
    asyncio.run(main())