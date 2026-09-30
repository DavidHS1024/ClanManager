"""
Configuración central de la aplicación.

Todos los valores que dependen del entorno se declaran aquí una sola vez.
El resto del código importa el objeto `settings` y nunca lee variables de
entorno por su cuenta.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Ajustes de la aplicación, cargados desde variables de entorno o .env."""

    # Archivo desde el que se leen los valores durante el desarrollo local.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Token de la API de Supercell. No tiene valor por defecto, por lo que
    # es obligatorio: si falta, la aplicación no arranca.
    coc_token: str

    # Tag del clan, con o sin '#'. Se normaliza en el cliente.
    clan_tag: str

    # URL base del proxy de RoyaleAPI, que reemplaza a api.clashofclans.com.
    coc_base_url: str = "https://cocproxy.royaleapi.dev/v1"

    # Segundos máximos de espera por la respuesta de la API.
    coc_timeout: float = 10.0

    # URL de conexión a PostgreSQL, con el formato
    # dialecto+controlador://usuario:clave@host:puerto/basedatos
    database_url: str

    # Minutos entre cada captura automática del clan.
    captura_intervalo_minutos: int = 60

    # Minutos entre cada sondeo de la guerra actual. Más corto que el de
    # miembros porque durante una guerra conviene notar los ataques pronto.
    guerra_intervalo_minutos: int = 10

    # Minutos de margen después de que termina la guerra antes de hacer la
    # captura final garantizada, para dar tiempo a que Supercell termine de
    # asentar los ataques de último minuto antes de consultarlos.
    guerra_captura_final_demora_minutos: int = 2

    # Minutos entre cada sondeo de la Liga de Guerras de Clanes (CWL).
    # Es más espaciado que el de guerra clásica porque, mientras haya
    # rondas nuevas por resolver, cada sondeo puede implicar varias
    # llamadas a la API en vez de una sola.
    liga_intervalo_minutos: int = 30


# Instancia única que el resto de la aplicación importa.
settings = Settings()
