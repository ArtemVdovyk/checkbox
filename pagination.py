import math
from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=50, ge=1)


T = TypeVar("T")


class PagedResponseSchema(BaseModel, Generic[T]):
    total_results: int
    page: int
    pages: int
    size: int
    results: List[T]


def paginate(page_params: PageParams, query, ResponseSchema: BaseModel):

    paginated_query = query.offset(
        (page_params.page - 1) * page_params.size).limit(page_params.size).all()

    return PagedResponseSchema(
        total_results=query.count(),
        page=page_params.page,
        pages=math.ceil(query.count() / page_params.size),
        size=page_params.size,
        results=[ResponseSchema.model_validate(
            item) for item in paginated_query],
    )
