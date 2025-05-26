import pytest, random
from fastapi.testclient import TestClient
from app.main import app
from app.utils.database import create_db_and_tables
from app.utils.services import unique_email, unique_cpf

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    create_db_and_tables()

@pytest.fixture
def client_data():
    return {
        "cli_name": "João Silva",
        "cli_email": unique_email(),
        "cli_cpf": unique_cpf(),
        "cli_phone": "(11) 98765-4321",
        "cli_address": "Rua Exemplo 123"
    }

def test_create_client(client_data):
    response = client.post("/clients", json=client_data)
    assert response.status_code == 200
    data = response.json()
    assert data["cli_email"] == client_data["cli_email"]
    assert data["cli_name"] == client_data["cli_name"]

def test_create_client_duplicate_email(client_data):
    # cria o primeiro
    client.post("/clients", json=client_data)
    # tenta criar o segundo com mesmo e-mail
    client_data["cli_cpf"] = "00011122233"
    response = client.post("/clients", json=client_data)
    assert response.status_code == 401
    assert "email" in response.json()["detail"].lower()

def test_create_client_duplicate_cpf(client_data):
    # cria o primeiro
    client.post("/clients", json=client_data)
    # tenta criar o segundo com mesmo cpf
    client_data["cli_email"] = "outro@example.com"
    response = client.post("/clients", json=client_data)
    assert response.status_code == 401
    assert "cpf" in response.json()["detail"].lower()

def test_get_clients():
    response = client.get("/clients")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_clients_with_filter(client_data):
    client.post("/clients", json=client_data)
    response = client.get("/clients", params={"name": "João"})
    assert response.status_code == 200
    assert any("João" in c["cli_name"] for c in response.json())

def test_get_client_by_id(client_data):
    create_resp = client.post("/clients", json=client_data)
    assert create_resp.status_code == 200, create_resp.text
    client_id = create_resp.json()["cli_id"]
    response = client.get(f"/clients/{client_id}")
    assert response.status_code == 200
    assert response.json()["cli_email"] == client_data["cli_email"]

def test_get_client_by_invalid_id():
    response = client.get("/clients/99999")
    assert response.status_code == 404

def test_update_client(client_data):
    create_resp = client.post("/clients", json=client_data)
    assert create_resp.status_code == 200, create_resp.text
    client_id = create_resp.json()["cli_id"]
    update_resp = client.put(f"/clients/{client_id}", json={"cli_name": "João Atualizado"})
    assert create_resp.status_code == 200, create_resp.text
    updated_data = update_resp.json()
    assert "cli_name" in updated_data, f"Resposta do PUT: {updated_data}"
    assert updated_data["cli_name"] == "João Atualizado"

def test_update_nonexistent_client():
    response = client.put("/clients/99999", json={"cli_name": "Testeeeeeeeeeeee", "cli_email": "teste@gmail.com", "cli_cpf": "12345678901", "cli_phone": "12345678901", "cli_address":"Rua N 9"})
    assert response.status_code == 404

def test_delete_client(client_data):
    create_resp = client.post("/clients", json=client_data)
    assert create_resp.status_code == 200, create_resp.text
    client_id = create_resp.json()["cli_id"]
    delete_resp = client.delete(f"/clients/{client_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json() == {"ok": True}

def test_delete_nonexistent_client():
    response = client.delete("/clients/99999")
    assert response.status_code == 404
