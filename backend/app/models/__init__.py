"""
Paquete de modelos.

Importar los modelos aquí garantiza que queden registrados en
Base.metadata cuando Alembic ejecuta `import app.models`.
"""

from app.models.captura import Captura, CapturaMiembro
from app.models.guerra import Guerra, GuerraAtaque, GuerraMiembro

__all__ = ["Captura", "CapturaMiembro", "Guerra", "GuerraAtaque", "GuerraMiembro"]