import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.core.product_service import get_product_by_id, list_products
from app.main import app
from app.models.product import ProductModel
from app.core.product_list_query import ProductListResponse
from app.core.database import get_mongodb
from pymongo import MongoClient

client = TestClient(app)

def mock_product_list_response():
    return ProductListResponse(
        data=[
            ProductModel(
                _id="682cbe0431d6a6922c7cf38f",
                name="Test Product",
                description="A test product",
                inventoryCount=10,
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

def mock_get_product_by_id_success():
    return ProductModel(
        _id="682cbe0431d6a6922c7cf38f",
        name="Test Product",
        description="A test product",
        inventoryCount=10,
        createdAt="2024-01-01T00:00:00Z"
    )

def mock_get_product_by_id_not_found():
    return None


def test_read_products_success():
    app.dependency_overrides[list_products] = mock_product_list_response
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert data["data"][0]["name"] == "Test Product"
    assert data["data"][0]["description"] == "A test product"
    assert data["data"][0]["inventoryCount"] == 10
    assert data["data"][0]["createdAt"] == "2024-01-01T00:00:00Z"
    assert data["meta"]["pagination"]["total"] == 1
    assert data["meta"]["pagination"]["page"] == 1
    assert data["meta"]["pagination"]["pageSize"] == 10
    assert data["meta"]["pagination"]["pageCount"] == 1
    app.dependency_overrides = {}

def test_read_product_success():
    app.dependency_overrides[get_product_by_id] = mock_get_product_by_id_success
    response = client.get("/api/v1/products/682cbe0431d6a6922c7cf38f")
    assert response.status_code == 200
    data = response.json()
    assert data["_id"] == "682cbe0431d6a6922c7cf38f"
    assert data["name"] == "Test Product"
    assert data["description"] == "A test product"
    assert data["inventoryCount"] == 10
    assert data["createdAt"] == "2024-01-01T00:00:00Z"
    app.dependency_overrides = {}

def test_read_product_not_found():
    app.dependency_overrides[get_product_by_id] = mock_get_product_by_id_not_found
    response = client.get("/api/v1/products/invalid_id")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Product not found"
    app.dependency_overrides = {}