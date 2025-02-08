import pytest
from fastapi.testclient import TestClient

from Core.runner import test_setup
from DB.DAO import clear

client = TestClient(test_setup())


@pytest.fixture
def sample_receipt() -> dict[str, str]:
    return {"status": "open"}


def test_create_receipt(sample_receipt: dict[str, str]) -> None:
    response = client.post("/receipts")
    assert response.status_code == 201
    data = response.json()
    assert "receipt" in data
    assert "id" in data["receipt"]
    assert data["receipt"]["status"] == "open"
    assert data["receipt"]["products"] == []
    assert data["receipt"]["total"] == 0


def test_close_receipt() -> None:
    create_response = client.post("/receipts")
    assert create_response.status_code == 201
    receipt_id = create_response.json()["receipt"]["id"]

    update_data = {"status": "closed"}
    response = client.patch(f"/receipts/{receipt_id}", json=update_data)
    assert response.status_code == 200

    non_existing_id = "non_existing_id"

    resp = client.patch(f"/receipts/{non_existing_id}", json=update_data)
    assert "does not exists" in str(resp.json()["detail"])


def test_get_receipt() -> None:
    create_response = client.post("/receipts")
    assert create_response.status_code == 201
    receipt_id = create_response.json()["receipt"]["id"]

    response = client.get(f"/receipts/{receipt_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == receipt_id
    assert "status" in data
    assert "products" in data
    assert "total" in data

    non_existing_id = "non_existing_id"
    resp = client.get(f"/receipts/{non_existing_id}")
    assert "does not exists" in str(resp.json()["detail"])


def test_delete_receipt() -> None:
    create_response = client.post("/receipts")
    assert create_response.status_code == 201
    receipt_id = create_response.json()["receipt"]["id"]

    response = client.delete(f"/receipts/{receipt_id}")
    assert response.status_code == 200

    resp = client.delete(f"/receipts/{receipt_id}")
    assert "does not exists" in str(resp.json()["detail"])

    create_response = client.post("/receipts")
    receipt_id = create_response.json()["receipt"]["id"]
    client.patch(f"/receipts/{receipt_id}", json={"status": "closed"})

    resp = client.delete(f"/receipts/{receipt_id}")
    assert "is closed" in str(resp.json()["detail"])

    non_existing_id = "non_existing_id"
    resp = client.delete(f"/receipts/{non_existing_id}")
    assert "does not exists" in str(resp.json()["detail"])


def test_clean() -> None:
    clear()
