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

    # Orígenes del frontend permitidos para llamar a esta API, separados
    # por coma. En desarrollo es la URL que usa Vite por defecto.
    frontend_origins: str = "http://localhost:5173"

    @property
    def frontend_origins_lista(self) -> list[str]:
        """Convierte frontend_origins en una lista limpia de URLs."""
        return [origen.strip() for origen in self.frontend_origins.split(",") if origen.strip()]

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

    # Minutos entre cada sondeo del fin de semana de asaltos. No tiene la
    # misma urgencia de último minuto que una guerra, así que un intervalo
    # más relajado es suficiente.
    asalto_intervalo_minutos: int = 30

    # Calendario semanal del Fin de Semana de Asaltos, en UTC. Los valores
    # por defecto corresponden al horario oficial confirmado por Supercell
    # y varias fuentes independientes: viernes 7:00 UTC a lunes 7:00 UTC.
    # Los días siguen la convención de Python, donde lunes es 0 y domingo
    # es 6. Ajustable por si observas un horario distinto en tu clan.
    asalto_inicio_dia_semana: int = 4  # viernes
    asalto_inicio_hora_utc: int = 7
    asalto_fin_dia_semana: int = 0  # lunes
    asalto_fin_hora_utc: int = 7

    # Minutos de margen después del fin calculado de la ventana, para
    # alcanzar a capturar los números ya asentados del último sondeo.
    asalto_captura_final_demora_minutos: int = 15


# Instancia única que el resto de la aplicación importa.
settings = Settings()
