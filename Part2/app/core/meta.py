from pydantic import BaseModel


class Pagination(BaseModel):
    page: int
    pageSize: int
    pageCount: int
    total: int

class Meta(BaseModel):
    pagination: Pagination