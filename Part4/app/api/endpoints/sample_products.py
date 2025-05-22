from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from app.core.mongodb_connection import MongoDBConnection
import pymongo

router = APIRouter()


class Product(BaseModel):
    name: str
    price: float
    description: str
    category: str
    inventory_count: int


@router.get("/part4/products")
async def get_products(
    page: int = Query(1, alias="pagination[page]", ge=1),
    page_size: int = Query(10, alias="pagination[pageSize]", ge=1),
    category: Optional[str] = None,
):
    query = {}
    if category:
        query["category"] = category

    pipeline = [
        {
            "$match": {
                "category": {
                    "$regex": category if category else "",
                    "$options": "i"
                }
            } if category else {}
        },
        {
            "$sort": {
                "name": 1
            }
        },
        {
            "$facet": {
                "metadata": [
                    {"$count": "totalCount"}
                ],
                "data": [
                    {"$skip": (page - 1) * page_size},
                    {"$limit": page_size}
                ]
            }
        }
    ]

    async with MongoDBConnection.get_collection(
        "ecommercedb", "products"
    ) as collection:
        cursor = collection.aggregate(pipeline)
        agg_result = await cursor.to_list(length=None)
        if agg_result:
            metadata = agg_result[0].get("metadata", [])
            products = agg_result[0].get("data", [])
            total = metadata[0]["totalCount"] if metadata else 0
        else:
            products = []
            total = 0
        # Some quick workarounds to work with data types. Should be unrelated to the assignment
        for product in products:
            product["_id"] = str(product["_id"])
            product["lastUpdatedAt"] = None

    return {
        "meta": {
            "pagination": {
                "page": page,
                "pageSize": page_size,
                "total": total,
                "pageCount": (total + page_size - 1) // page_size if page_size else 0
            }
        },
        "products": products
        }
