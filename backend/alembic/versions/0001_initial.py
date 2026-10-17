"""Migración inicial — crea todo el esquema a partir de los modelos.

Esta primera revisión materializa `Base.metadata` completo (todas las tablas
definidas en app/models). Las revisiones siguientes deberían generarse con
`alembic revision --autogenerate -m "..."` para capturar cambios incrementales.

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-22
"""
from alembic import op

from app.db.base import Base
import app.models  # noqa: F401  (registra los modelos en Base.metadata)

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
