from typing import List
from pydantic import BaseModel

from app.core.meta import Meta
from app.models.order import OrderModel


class OrderListResponse(BaseModel):
    data: List[OrderModel]
    meta: Meta
