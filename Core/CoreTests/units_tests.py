from fastapi.testclient import TestClient

from Core.runner import test_setup
from DB.DAO import clear

client = TestClient(test_setup())


def test_create_unit() -> None:
    response = client.post("/units", json={"name": "TestUnit"})
    assert response.status_code == 201
    assert "unit" in response.json()
    assert response.json()["unit"]["name"] == "TestUnit"


def test_create_duplicate_unit() -> None:
    client.post("/units", json={"name": "TestUnit"})

    response = client.post("/units", json={"name": "TestUnit"})
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_get_unit() -> None:
    resp = client.post("/units", json={"name": "Unit"})

    response = client.get(f"/units/{resp.json()["unit"]["id"]}")
    assert response.status_code == 200
    assert response.json()["unit"]["id"] == resp.json()["unit"]["id"]
    assert response.json()["unit"]["name"] == "Unit"


def test_get_nonexistent_unit() -> None:
    response = client.get("/units/non-existent-id")
    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"]


def test_list_units() -> None:
    response = client.get("/units")
    assert response.status_code == 200
    assert len(response.json()["units"]) == 2


def test_clean() -> None:
    clear()
