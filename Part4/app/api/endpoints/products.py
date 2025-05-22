from fastapi import APIRouter, Depends, HTTPException, status
from app.core.error import ErrorModel
from app.core.product_list_query import ProductListResponse
from app.core.product_service import get_product_by_id, list_products
from app.models.product import ProductModel

router = APIRouter()

@router.get("/products",
            response_model=ProductListResponse,
            )
def read_products(
    productsResponse = Depends(list_products)
):
    """
    Endpoint to get a list of products with pagination and filtering.
    You can filter by name or exact category.
    You can also sort by multiple fields, separated by commas. (e.g. "name:asc,price:desc" or "name:1,price:-1").

    Returns:
        Products data array matching the criteria and metadata about pagination.
    """
    return productsResponse

@router.get("/products/{product_id}",
            response_model=ProductModel,
            responses= {
                404: {
                    "description": "Product not found",
                    "model": ErrorModel,
                },
                400: {
                    "description": "Invalid product_id format",
                    "model": ErrorModel,
                }
            }
            )
def read_product(
    productResponse = Depends(get_product_by_id)
):
    """
    Endpoint to get a single product by its ID.
    """
    if not productResponse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return productResponse