from typing import Dict, Any, Optional

from bson import ObjectId
from fastapi import Body, Depends, Query
from app.core.create_order_command import CreateOrderCommand
from app.core.dependencies import get_mongodb_repo
from app.core.order_list_query import OrderListResponse
from app.models.order import OrderModel
from app.repository.order_repository import OrderRepository

def get_order_by_id(
    order_id: str,
    order_repository: OrderRepository = Depends(get_mongodb_repo(OrderRepository))
):
    """
    Get an order by its ID.

    Args:
        order_id (str): The ID of the order to retrieve.

    Returns:
        The order data if found, otherwise None.
    """
    return order_repository.get_by_id(order_id)

def list_orders(
    page: int = Query(1, alias="pagination[page]", ge=1),
    page_size: int = Query(10, alias="pagination[pageSize]", ge=1),
    sort: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    order_repository: OrderRepository = Depends(get_mongodb_repo(OrderRepository))
):
    """
    List orders with optional filtering, pagination, and sorting.

    Returns:
        Orders data array matching the criteria and metadata about pagination.
    """
    filter_query: Dict[str, Any] = {}
    if status:
        filter_query["status"] = status
    if customer_id:
        filter_query["customerId"] = ObjectId(customer_id)

    sort_query = None
    if sort:
        pairs = sort.split(",")
        sort_query = []
        for pair in pairs:
            if ":" in pair:
                field, direction = pair.split(":")
                if direction.lstrip('+-').isdigit():
                    sort_query.append((field, int(direction)))
                elif direction.lower() == "asc":
                    sort_query.append((field, 1))
                elif direction.lower() == "desc":
                    sort_query.append((field, -1))
            else:
                field = pair
                sort_query.append((field, 1))

    skip = (page - 1) * page_size
    limit = page_size

    orders, total = order_repository.get_all(
        filter=filter_query,
        skip=skip,
        limit=limit,
        sort=sort_query
    )

    page_count = (total + page_size - 1) // page_size if page_size else 0

    return OrderListResponse(
        data=orders,
        meta={
            "pagination": {
                "page": page,
                "pageSize": page_size,
                "pageCount": page_count,
                "total": total
            }
        }
    )

def create_order(
    command: CreateOrderCommand = Body(..., ),
    order_repository: OrderRepository = Depends(get_mongodb_repo(OrderRepository))
):
    """
    Create a new order.

    Args:
        command (CreateOrderCommand): The order data to insert.

    Returns:
        The created order.
    """
    new_order = OrderModel(
        customerId=ObjectId(command.customerId),
        orderItems=command.orderItems,
        subtotal=command.subtotal,
        tax=command.tax,
        shipping_cost=command.shippingCost,
        total=command.total,
        shipping_address=command.shippingAddress,
        status=command.status,
        createdAt=command.createdAt,
    )
    return order_repository.create_new_order(new_order)

def get_orders_by_customer_id(
    customer_id: str,
    order_repository: OrderRepository = Depends(get_mongodb_repo(OrderRepository))
):
    """
    Get all orders for a specific customer by their ID.

    Args:
        customer_id (str): The ID of the customer.

    Returns:
        List of orders for the specified customer.
    """
    return order_repository.get_orders_by_customer_id(customer_id)