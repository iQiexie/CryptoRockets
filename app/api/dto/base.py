from typing import Generic, TypeVar

from fastapi import Query
from pydantic import ConfigDict, Field

from app.init.base_models import BaseModel

T = TypeVar("T")


def snake_to_camel(string: str) -> str:
    result = string.split("_")
    return result[0] + "".join(word.capitalize() for word in result[1:])


class BaseRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=snake_to_camel)


class BaseResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True, alias_generator=snake_to_camel)


class PaginatedRequest(BaseModel):
    page: int | None = Query(default=1, ge=1, le=100)
    limit: int | None = Query(default=100, ge=1, le=100)


class PaginatedResponse(BaseModel, Generic[T]):
    page: int | None = Field(default=1, description="На какой мы сейчас странице")
    limit: int = Field(..., description="Количество элементов на странице")
    total: int = Field(..., description="Сколько вообще элементов")
    items: list[T]
