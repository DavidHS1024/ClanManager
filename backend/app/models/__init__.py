"""
Paquete de modelos.

Importar los modelos aquí garantiza que queden registrados en
Base.metadata cuando Alembic ejecuta `import app.models`.
"""

from app.models.captura import Captura, CapturaMiembro

__all__ = ["Captura", "CapturaMiembro"]