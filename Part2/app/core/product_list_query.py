from typing import Dict, List
from pydantic import BaseModel

from app.core.meta import Meta
from app.models.product import ProductModel


class ProductListResponse(BaseModel):
    data: List[ProductModel]
    meta: Meta
