from datetime import datetime
from typing import List
from pydantic import BaseModel

from app.models.order import OrderItemModel, ShippingAddressModel
from app.models.py_object_id import PyObjectId


class CreateOrderCommand(BaseModel):
    customerId: PyObjectId
    orderItems: List[OrderItemModel]
    subtotal: float
    tax: float
    shippingCost: float
    total: float
    shippingAddress: ShippingAddressModel
    status: str
    createdAt: datetime