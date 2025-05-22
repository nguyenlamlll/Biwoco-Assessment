from typing import Dict, Any, List, Optional

from bson import ObjectId
from fastapi import Depends, HTTPException, Query, status
from app.core.dependencies import get_mongodb_repo
from app.core.meta import Meta
from app.core.product_list_query import ProductListResponse
from app.repository.product_repository import ProductRepository

def validate_object_id(product_id: str):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product_id format. Must be a valid ObjectId."
        )
    return product_id


def get_product_by_id(
    product_id: str,
    product_repository: ProductRepository = Depends(get_mongodb_repo(ProductRepository))
):
    """
    Get a product by its ID.

    Args:
        product_id (str): The ID of the product to retrieve.

    Returns:
        The product data if found, otherwise None.
    """
    validate_object_id(product_id)
    return product_repository.get_by_id(product_id)

def list_products(
    page: int = Query(1, alias="pagination[page]", ge=1),
    page_size: int = Query(10, alias="pagination[pageSize]", ge=1),
    sort: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    product_repository: ProductRepository = Depends(get_mongodb_repo(ProductRepository))
):
    """
    List products with optional filtering, pagination, and sorting.

    Returns:
        Products data array matching the criteria and metadata about pagination.
    """
    filter_query: Dict[str, Any] = {}
    if name:
        filter_query["name"] = {"$regex": name, "$options": "i"}
    if category:
        filter_query["categories"] = category

    sort_query = None
    if sort:
        # First split by comma to get multiple sort fields
        # Then split each field by colon to get field and direction
        pairs = sort.split(",")
        sort_query = []
        for pair in pairs:
            if ":" in pair:
                field, direction = pair.split(":")
                # If direction is 1 or -1, use it as is
                # Otherwise, check if it's "asc" or "desc"
                if direction.lstrip('+-').isdigit():
                    sort_query.append((field, int(direction)))
                elif direction.lower() == "asc":
                    sort_query.append((field, 1))
                elif direction.lower() == "desc":
                    sort_query.append((field, -1))
            else:
                # Default to ascending if no direction is specified
                field = pair
                sort_query.append((field, 1))

    skip = (page - 1) * page_size
    limit = page_size

    products, total = product_repository.get_all(
        filter=filter_query,
        skip=skip,
        limit=limit,
        sort=sort_query
    )

    page_count = (total + page_size - 1) // page_size if page_size else 0

    return ProductListResponse(
        data=products,
        meta=Meta(
            pagination={
                "page": page,
                "pageSize": page_size,
                "pageCount": page_count,
                "total": total
            }
        )
    )