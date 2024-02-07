from typing import Generic
from typing import TypeVar
from pydantic import BaseModel
from pydantic import Field
from typing import Optional


T = TypeVar("T")


class PagintationParams(BaseModel):
    limit: int = Field(ge=0, le=50, default=20)
    offset: int = Field(ge=0, default=0)


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    limit: int
    offset: int
    next_offset: Optional[int] = None
    items: list[T]
