from typing import List
from fastapi import APIRouter, Depends, Body, HTTPException, status
from app.core.order_list_query import OrderListResponse
from app.core.order_service import get_order_by_id, get_orders_by_customer_id, list_orders, create_order
from app.models.order import OrderModel

router = APIRouter()

@router.get("/orders",
            response_model=OrderListResponse,
            )
def read_orders(
    ordersResponse = Depends(list_orders)
):
    """
    Endpoint to get a list of orders with pagination and filtering.
    """
    return ordersResponse

@router.get("/orders/{order_id}",
            response_model=OrderModel,
            )
def read_order(
    orderResponse = Depends(get_order_by_id)
):
    """
    Endpoint to get a single order by its ID.
    """
    if not orderResponse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return orderResponse

@router.get("/customers/{customer_id}/orders",
            response_model=List[OrderModel],
            )
def read_orders_by_customer(
    ordersResponse = Depends(get_orders_by_customer_id)
):
    """
    Endpoint to get all orders for a specific customer by their ID.
    """
    if not ordersResponse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No orders found for this customer")
    return ordersResponse

@router.post("/orders", status_code=status.HTTP_201_CREATED,
             response_model=OrderModel,
            )
def create_new_order(
    orderResponse = Depends(create_order)
):
    """
    Endpoint to create a new order.
    """
    return orderResponse