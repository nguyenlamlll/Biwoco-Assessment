from bson import ObjectId, Timestamp
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.models.mongo_timestamp import MongoTimestamp
from app.models.py_object_id import PyObjectId

class OrderItemModel(BaseModel):
    productId: str
    productName: str
    quantity: int
    unitPrice: float
    totalPrice: float

class ShippingAddressModel(BaseModel):
    customerName: str
    addressLine1: str
    addressLine2: Optional[str] = None
    city: str
    country: str

class OrderModel(BaseModel):
    id: PyObjectId = Field(alias="_id", default_factory=PyObjectId)
    customerId: PyObjectId
    orderItems: List[OrderItemModel]
    subtotal: float
    tax: float
    shipping_cost: float
    total: float
    shipping_address: ShippingAddressModel
    status: str
    createdAt: datetime
    #lastUpdatedAt: MongoTimestamp

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, Timestamp: lambda v: v.as_datetime()}
