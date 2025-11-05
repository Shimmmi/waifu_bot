"""
Pagination utility for database queries
"""
from typing import TypeVar, Generic, List, Tuple
from sqlalchemy.orm import Query
from pydantic import BaseModel

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Параметры пагинации из запроса"""
    page: int = 1
    limit: int = 20
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginationInfo(BaseModel):
    """Информация о пагинации"""
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Пагинированный ответ"""
    items: List[T]
    pagination: PaginationInfo


def paginate_query(
    query: Query,
    page: int = 1,
    limit: int = 20,
    max_limit: int = 100
) -> Tuple[List, PaginationInfo]:
    """
    Применить пагинацию к SQLAlchemy запросу
    
    Args:
        query: SQLAlchemy запрос
        page: Номер страницы (начиная с 1)
        limit: Размер страницы
        max_limit: Максимальный размер страницы
    
    Returns:
        (items, pagination_info)
    """
    # Ограничиваем максимальный размер страницы
    limit = min(limit, max_limit)
    page = max(1, page)
    
    # Получаем общее количество записей
    total = query.count()
    
    # Применяем пагинацию
    items = query.offset((page - 1) * limit).limit(limit).all()
    
    # Вычисляем информацию о пагинации
    total_pages = (total + limit - 1) // limit if limit > 0 else 0  # Округление вверх
    
    pagination_info = PaginationInfo(
        page=page,
        limit=limit,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )
    
    return items, pagination_info
