"""Prueba manual del cliente: imprime el resumen del clan y sus miembros."""

import asyncio
from app.services.clash_client import ClashApiError, ClashClient, crear_cliente_http

async def main() -> None:
    async with crear_cliente_http() as http:
        cliente = ClashClient(http)

        try:
            clan = await cliente.obtener_clan()
        except ClashApiError as error:
            print(f"Error ({error.status_code}): {error}")
            return

        miembros = clan["memberList"]
        print(f"Clan: {clan['name']} - Nivel {clan['clanLevel']} - {len(miembros)} miembros")
        for miembro in miembros:
            print(f"  {miembro['name']:<22} {miembro['role']:<10} Donaciones: {miembro['donations']}")

if __name__ == "__main__":
    asyncio.run(main())