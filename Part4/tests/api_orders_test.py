import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.order import OrderModel, ShippingAddressModel
from app.core.order_list_query import OrderListResponse
from app.core.order_service import list_orders, get_order_by_id, get_orders_by_customer_id, create_order

client = TestClient(app)

def mock_order_list_response():
    return OrderListResponse(
        data=[
            OrderModel(
                _id="682cbe0431d6a6922c7cf38f",
                customerId="777cbe0431d6a6922c7cf38f",
                orderItems=[
                    {
                        "productId": "123456",
                        "productName": "Test Product",
                        "quantity": 2,
                        "unitPrice": 50.0,
                        "totalPrice": 100.0
                    }
                ],
                subtotal=100.0,
                tax=10.0,
                shipping_cost=0.0,
                total=110.0,
                status="pending",
                shipping_address=
                    ShippingAddressModel(
                        customerName="John Doe",
                        addressLine1="123 Main St",
                        addressLine2="Apt 4B",
                        city="New York",
                        country="USA"
                    )
                ,
                createdAt="2024-01-01T00:00:00Z"
            )
        ],
        meta={
            "pagination": {
                "page": 1,
                "pageSize": 10,
                "pageCount": 1,
                "total": 1
            }
        }
    )

def mock_get_order_by_id_success():
    return OrderModel(
        _id="682cbe0431d6a6922c7cf38f",
        customerId="777cbe0431d6a6922c7cf38f",
        orderItems=[
            {
                "productId": "123456",
                "productName": "Test Product",
                "quantity": 2,
                "unitPrice": 50.0,
                "totalPrice": 100.0
            }
        ],
        subtotal=100.0,
        tax=10.0,
        shipping_cost=0.0,
        total=110.0,
        status="pending",
        shipping_address=
            ShippingAddressModel(
                customerName="John Doe",
                addressLine1="123 Main St",
                addressLine2="Apt 4B",
                city="New York",
                country="USA"
            )
        ,
        createdAt="2024-01-01T00:00:00Z"
    )

def mock_get_order_by_id_not_found():
    return None

def mock_get_orders_by_customer_id_success():
    return [
        OrderModel(
            _id="682cbe0431d6a6922c7cf38f",
            customerId="777cbe0431d6a6922c7cf38f",
            orderItems=[
                {
                    "productId": "123456",
                    "productName": "Test Product",
                    "quantity": 2,
                    "unitPrice": 50.0,
                    "totalPrice": 100.0
                }
            ],
            subtotal=100.0,
            tax=10.0,
            shipping_cost=0.0,
            total=110.0,
            status="pending",
            shipping_address=
                ShippingAddressModel(
                    customerName="John Doe",
                    addressLine1="123 Main St",
                    addressLine2="Apt 4B",
                    city="New York",
                    country="USA"
                )
            ,
            createdAt="2024-01-01T00:00:00Z"
        )
    ]

def mock_get_orders_by_customer_id_not_found():
    return []

def mock_create_order():
    return OrderModel(
        _id="682cbe0431d6a6922c7cf38f",
        customerId="777cbe0431d6a6922c7cf38f",
        orderItems=[
            {
                "productId": "123456",
                "productName": "Test Product",
                "quantity": 2,
                "unitPrice": 50.0,
                "totalPrice": 100.0
            }
        ],
        subtotal=100.0,
        tax=10.0,
        shipping_cost=0.0,
        total=110.0,
        status="pending",
        shipping_address=
            ShippingAddressModel(
                customerName="John Doe",
                addressLine1="123 Main St",
                addressLine2="Apt 4B",
                city="New York",
                country="USA"
            )
        ,
        createdAt="2024-01-02T00:00:00Z"
    )

def test_read_orders_success():
    app.dependency_overrides[list_orders] = mock_order_list_response
    response = client.get("/api/v1/orders")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert data["data"][0]["_id"] == "682cbe0431d6a6922c7cf38f"
    assert data["data"][0]["customerId"] == "777cbe0431d6a6922c7cf38f"
    assert data["meta"]["pagination"]["total"] == 1
    app.dependency_overrides = {}

def test_read_order_success():
    app.dependency_overrides[get_order_by_id] = mock_get_order_by_id_success
    response = client.get("/api/v1/orders/order123")
    assert response.status_code == 200
    data = response.json()
    assert data["_id"] == "682cbe0431d6a6922c7cf38f"
    assert data["customerId"] == "777cbe0431d6a6922c7cf38f"
    app.dependency_overrides = {}

def test_read_order_not_found():
    app.dependency_overrides[get_order_by_id] = mock_get_order_by_id_not_found
    response = client.get("/api/v1/orders/invalid_id")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Order not found"
    app.dependency_overrides = {}

def test_read_orders_by_customer_success():
    app.dependency_overrides[get_orders_by_customer_id] = mock_get_orders_by_customer_id_success
    response = client.get("/api/v1/customers/cust1/orders")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["customerId"] == "777cbe0431d6a6922c7cf38f"
    app.dependency_overrides = {}

def test_read_orders_by_customer_not_found():
    from app.core.order_service import get_orders_by_customer_id
    app.dependency_overrides[get_orders_by_customer_id] = mock_get_orders_by_customer_id_not_found
    response = client.get("/api/v1/customers/unknown/orders")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "No orders found for this customer"
    app.dependency_overrides = {}

def test_create_new_order_success():
    app.dependency_overrides[create_order] = mock_create_order
    response = client.post("/api/v1/orders")
    assert response.status_code == 201
    data = response.json()
    assert data["_id"] == "682cbe0431d6a6922c7cf38f"
    assert data["customerId"] == "777cbe0431d6a6922c7cf38f"
    app.dependency_overrides = {}