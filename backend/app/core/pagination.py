"""Utilidades de paginación por página (sección 3.2 del contrato)."""
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

from app.core.config import settings

T = TypeVar("T")


class PageParams:
    """Dependencia con los parámetros de paginación estándar."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Número de página (desde 1)."),
        page_size: int = Query(
            settings.DEFAULT_PAGE_SIZE,
            ge=1,
            le=settings.MAX_PAGE_SIZE,
            description=f"Elementos por página (máx. {settings.MAX_PAGE_SIZE}).",
        ),
    ) -> None:
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class Page(BaseModel, Generic[T]):
    """Sobre de respuesta paginada."""

    items: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int

    @classmethod
    def create(cls, items: list[T], total: int, params: PageParams) -> "Page[T]":
        total_pages = (total + params.page_size - 1) // params.page_size if total else 0
        return cls(
            items=items,
            page=params.page,
            page_size=params.page_size,
            total=total,
            total_pages=total_pages,
        )
