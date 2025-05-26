from fastapi.testclient import TestClient
from app.main import app
from app.utils.services import unique_email, unique_cpf

client = TestClient(app)

def test_create_client(client_data, auth_headers):
    response = client.post("/clients", json=client_data, headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["cli_email"] == client_data["cli_email"]
    assert data["cli_name"] == client_data["cli_name"]

def test_create_client_duplicate_email(client_data, auth_headers):
    client.post("/clients", json=client_data, headers=auth_headers)
    client_data["cli_cpf"] = unique_cpf()
    response = client.post("/clients", json=client_data, headers=auth_headers)
    assert response.status_code == 401
    assert "email" in response.json()["detail"].lower()

def test_create_client_duplicate_cpf(client_data, auth_headers):
    client.post("/clients", json=client_data, headers=auth_headers)
    client_data["cli_email"] = unique_email()
    response = client.post("/clients", json=client_data, headers=auth_headers)
    assert response.status_code == 401
    assert "cpf" in response.json()["detail"].lower()

def test_get_clients(auth_headers):
    response = client.get("/clients", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_clients_with_filter(client_data, auth_headers):
    client.post("/clients", json=client_data, headers=auth_headers)
    response = client.get("/clients", params={"name": "João"}, headers=auth_headers)
    assert response.status_code == 200
    assert any("João" in c["cli_name"] for c in response.json())

def test_get_client_by_id(client_data, auth_headers):
    create_resp = client.post("/clients", json=client_data, headers=auth_headers)
    assert create_resp.status_code == 200, create_resp.text
    client_id = create_resp.json()["cli_id"]
    response = client.get(f"/clients/{client_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["cli_email"] == client_data["cli_email"]

def test_get_client_by_invalid_id(auth_headers):
    response = client.get("/clients/99999", headers=auth_headers)
    assert response.status_code == 404

def test_update_client(client_data, auth_headers):
    create_resp = client.post("/clients", json=client_data, headers=auth_headers)
    assert create_resp.status_code == 200, create_resp.text
    client_id = create_resp.json()["cli_id"]
    update_resp = client.put(f"/clients/{client_id}", json={"cli_name": "João Atualizado"}, headers=auth_headers)
    assert update_resp.status_code == 200, update_resp.text
    updated_data = update_resp.json()
    assert "cli_name" in updated_data, f"Resposta do PUT: {updated_data}"
    assert updated_data["cli_name"] == "João Atualizado"

def test_update_nonexistent_client(auth_headers):
    response = client.put(
        "/clients/99999",
        json={
            "cli_name": "Testeeeeeeeeeeee",
            "cli_email": unique_email(),
            "cli_cpf": unique_cpf(),
            "cli_phone": "12345678901",
            "cli_address": "Rua N 9"
        },
        headers=auth_headers
    )
    assert response.status_code == 404

def test_delete_client(client_data, auth_headers):
    create_resp = client.post("/clients", json=client_data, headers=auth_headers)
    assert create_resp.status_code == 200, create_resp.text
    client_id = create_resp.json()["cli_id"]
    delete_resp = client.delete(f"/clients/{client_id}", headers=auth_headers)
    assert delete_resp.status_code == 200
    assert delete_resp.json() == {"ok": True}

def test_delete_nonexistent_client(auth_headers):
    response = client.delete("/clients/99999", headers=auth_headers)
    assert response.status_code == 404