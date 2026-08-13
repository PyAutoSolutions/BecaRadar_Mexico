from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")

class ErrorResponse(BaseModel):
    error: bool = True
    detail: str
    status_code: int

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int