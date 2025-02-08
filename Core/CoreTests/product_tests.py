from typing import Any

import pytest
from fastapi.testclient import TestClient

from Core.runner import test_setup
from DB.DAO import clear

client = TestClient(test_setup())


@pytest.fixture
def sample_product() -> dict[str, Any]:
    return {
        "unit_id": "unit123",
        "name": "Test Product",
        "barcode": "123456789",
        "price": 100,
    }


def test_create_product(sample_product: dict[str, Any]) -> None:
    response = client.post("/products", json=sample_product)
    assert response.status_code == 201
    data = response.json()
    assert "product" in data
    assert data["product"]["name"] == sample_product["name"]
    assert data["product"]["barcode"] == sample_product["barcode"]
    assert data["product"]["price"] == sample_product["price"]

    resp = client.post("/products", json=sample_product)
    assert "already exists" in str(resp.json()["detail"])


def test_get_product() -> None:
    create_response = client.post(
        "/products",
        json={
            "unit_id": "unit123",
            "name": "Test Product",
            "barcode": "987654321",
            "price": 200,
        },
    )

    assert create_response.status_code == 201
    product_id = create_response.json()["product"]["id"]

    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["product"]["id"] == product_id

    resp = client.get(f"/products/{str(product_id)[0]}")
    assert "does not exist" in str(resp.json()["detail"])


def test_list_products() -> None:
    response = client.get("/products")
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert "products" in data
    assert isinstance(data["products"], list)
    assert len(data["products"]) > 0


def test_update_product() -> None:
    create_response = client.post(
        "/products",
        json={
            "unit_id": "unit999",
            "name": "Product Update Test",
            "barcode": "111222333",
            "price": 500,
        },
    )
    assert create_response.status_code == 201
    product_id = create_response.json()["product"]["id"]

    update_response = client.patch(f"/products/{product_id}", json={"price": 600})
    assert update_response.status_code == 200

    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 200
    assert get_response.json()["product"]["price"] == 600

    resp = client.patch(f"/products/{str(product_id)[0]}", json={"price": 600})

    assert "does not exist" in str(resp.json()["detail"])


# clears DB
def test_clear_products() -> None:
    clear()
