"""Clase base de la que heredan todos los modelos de la base de datos."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base declarativa de SQLAlchemy.

    Cada modelo que herede de esta clase queda registrado en Base.metadata,
    el catálogo de tablas que Alembic compara contra la base de datos real
    para generar las migraciones.
    """