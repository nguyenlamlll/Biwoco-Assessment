from bson import ObjectId, Timestamp
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.models.mongo_timestamp import MongoTimestamp
from app.models.py_object_id import PyObjectId

class ProductModel(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str
    description: str
    shortDescription: Optional[str] = None
    thumbnails: Optional[List[str]] = None
    images: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    price: Optional[float] = None
    inventoryCount: int
    createdAt: datetime
    # lastUpdatedAt: MongoTimestamp

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}