import pytest
from fastapi.testclient import TestClient


from Core.runner import test_setup
from DB.DAO import clear, get_db

client = TestClient(test_setup())


def test_add_product_to_receipt() -> None:
    con = get_db()
    cursor = con.cursor()
    cursor.execute("INSERT INTO receipts (id, status) VALUES ('r1', 'open');")
    cursor.execute("INSERT INTO receipts (id, status) VALUES ('r2', 'closed');")
    cursor.execute("INSERT INTO receipts (id, status) VALUES ('r3', 'open');")

    cursor.execute(
        "INSERT INTO products (id, unit_id, name, barcode, price) VALUES ('p1','u1','prod','barcode',  100);"
    )
    con.commit()
    product_request = {"id": "p1", "quantity": 2}
    response = client.post("/receipts/r1/products", json=product_request)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 200
    assert len(data["products"]) == 1
    assert data["products"][0]["id"] == "p1"
    assert data["products"][0]["total"] == 200


def test_get_sales_report() -> None:
    response = client.get("/sales")

    assert response.status_code == 200
    data = response.json()

    assert data == {"sales": {"n_receipts": 0, "revenue": 0}}
    update_data = {"status": "closed"}
    response = client.patch(f"/receipts/r1", json=update_data)
    assert response.status_code == 200
    response = client.get("/sales")
    assert response.status_code == 200
    data = response.json()
    assert data == {"sales": {"n_receipts": 1, "revenue": 200}}


def test_open_closed_receipt() -> None:
    update_data = {"status": "open"}
    response = client.patch(f"/receipts/r1", json=update_data)

    assert response.status_code == 404
    assert response.json() == {"detail": "Receipt with id<r1> is closed"}


def test_add_product_to_closed_receipt() -> None:
    product_request = {"id": "1", "quantity": 1}

    response = client.post("/receipts/r2/products", json=product_request)
    assert response.status_code == 404
    assert response.json() == {"detail": "Receipt by id<r2> is closed"}


def test_add_product_to_non_existent_receipt() -> None:
    product_request = {"id": "p1", "quantity": 1}
    response = client.post(
        "/receipts/nonexistent_receipt/products", json=product_request
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Receipt by id<nonexistent_receipt> does not exists"
    }


def test_add_non_existent_product() -> None:
    product_request = {"id": "nonexistent_product", "quantity": 1}
    response = client.post("/receipts/r3/products", json=product_request)

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product by id <nonexistent_product> does not exists"
    }


def test_clear() -> None:
    clear()
