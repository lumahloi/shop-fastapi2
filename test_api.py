import pytest
from fastapi.testclient import TestClient
from main import app

from services.custom_types import VALID_USER_TYPES

client = TestClient(app)

@pytest.fixture(autouse=True, scope="module")
def setup_database():
    from services.database import create_db_and_tables
    create_db_and_tables()


####################################################################### USER

def test_register_user():
    response = client.post(
        "/auth/register",
        json={"usr_email": "testuser@example.com", "usr_pass": "securepassword", "usr_name": "testuser", "usr_type": "Estoquista"}
    )
    assert response.status_code == 200
    assert response.json()["usr_email"] == "testuser@example.com"
    assert response.json()["usr_type"] in VALID_USER_TYPES

def test_register_user_duplicate():
    response = client.post(
        "/auth/register",
        json={"usr_email": "testuser@example.com", "usr_pass": "securepassword", "usr_name": "testuser", "usr_type": "Estoquista"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Já existe um usuário cadastrado com este email."

def test_change_user_type():
    user_resp = client.post(
        "/auth/register",
        json={
            "usr_name": "João Silva",
            "usr_email": "joao.silva@example.com",
            "usr_pass": "senha123",
            "usr_type": "Estoquista"
        }
    )
    assert user_resp.status_code == 200
    user_data = user_resp.json()
    user_id = user_data["usr_id"]

    update_resp = client.put(
        f"/auth/register/{user_id}",
        json={
            "usr_type": "Administrador"
        }
    )
    assert update_resp.status_code == 200
    updated_user = update_resp.json()

    assert updated_user["usr_type"] == "Administrador"
    assert updated_user["usr_id"] == user_id

####################################################################### CLIENT

def test_create_client():
    response = client.post(
        "/clients",
        json={
            "cli_name": "João Silva",
            "cli_email": "joao.silva@example.com",
            "cli_cpf": "12345678901",
            "cli_phone": "11987654321",
            "cli_address": "Rua das Rosas 395"
        }
    )
    assert response.status_code == 200
    assert response.json()["cli_name"] == "João Silva"

def test_get_all_clients():
    response = client.get("/clients")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_get_clients_by_name():
    client.post(
        "/clients",
        json={
            "cli_name": "João da Silva",
            "cli_email": "joao.silva@example.com",
            "cli_cpf": "12345678901",
            "cli_phone": "11999999999",
            "cli_address": "Rua A, 123"
        }
    )

    response = client.get("/clients?name=João")
    assert response.status_code == 200
    clients = response.json()
    assert any("João" in cli["cli_name"] for cli in clients)

def test_get_clients_by_email():
    client.post(
        "/clients",
        json={
            "cli_name": "Ana Maria",
            "cli_email": "ana.maria@example.com",
            "cli_cpf": "12312312399",
            "cli_phone": "11988888888",
            "cli_address": "Rua B, 456"
        }
    )

    response = client.get("/clients?email=ana.maria@example.com")
    assert response.status_code == 200
    clients = response.json()
    assert any("ana.maria@example.com" == cli["cli_email"] for cli in clients)

def test_get_clients_pagination():
    response = client.get("/clients?num_page=1&limit=2")
    assert response.status_code == 200
    clients = response.json()
    assert isinstance(clients, list)
    assert len(clients) > 0

def test_get_client_by_id():
    response = client.get("/clients/1")
    assert response.status_code == 200

def test_update_client():
    response = client.put(
        "/clients/1",
        json={"cli_name": "João Atualizado"}
    )
    assert response.status_code == 200
    assert response.json()["cli_name"] == "João Atualizado"

def test_delete_client():
    response = client.delete("/clients/1")
    assert response.status_code == 200
    assert response.json()["ok"] is True


####################################################################### PRODUCT

def test_create_product():
    response = client.post(
        "/products",
        json={
            "prod_size": ["PP", "P"],
            "prod_color": ["laranja", "vermelho"],
            "prod_imgs": [],
            "prod_name": "Camisa Polo",
            "prod_desc": "Camisa confortável para o dia a dia.",
            "prod_price": 99.90,
            "prod_stock": 10,
            "prod_cat": "Masculino",
            "prod_barcode": "1234567890123456789012345678901234567890123",
            "prod_section": "Blusas",
            "prod_dtval": None
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["prod_name"] == "Camisa Polo"
    assert data["prod_stock"] == 10

def test_get_products():
    response = client.get("/products")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_product_by_id():
    response = client.get("/products/1")
    assert response.status_code == 200
    assert response.json()["prod_name"] == "Camisa Polo"

def test_update_product():
    response = client.put(
        "/products/1",
        json={"prod_price": 89.90}
    )
    assert response.status_code == 200
    assert response.json()["prod_price"] == 89.90

def test_delete_product():
    response = client.delete("/products/1")
    assert response.status_code == 200
    assert response.json()["ok"] is True


####################################################################### ORDER

def test_create_order():
    # Cria cliente
    client_resp = client.post(
        "/clients",
        json={
            "cli_name": "Maria Souza",
            "cli_email": "maria.souza@example.com",
            "cli_cpf": "98765432100",
            "cli_phone": "11987654322",
            "cli_address": "Rua de Matheus 5"
        }
    )
    assert client_resp.status_code == 200
    cli_id = client_resp.json()["cli_id"]

    # Cria produto
    product_resp = client.post(
        "/products",
        json={
            "prod_name": "Calça Jeans",
            "prod_price": 149.90,
            "prod_stock": 5,
            "prod_cat": "Feminino",
            "prod_section": "Calças",
            "prod_barcode": "1234567890123456789012345678901234567890123",
            "prod_color": ["azul"],
            "prod_size": ["M"],
            "prod_desc": None,
            "prod_imgs": None,
            "prod_dtval": None
        }
    )
    assert product_resp.status_code == 200
    prod_id = product_resp.json()["prod_id"]

    # Cria pedido
    response = client.post(
        "/orders",
        json={
            "order_cli": cli_id,
            "order_prods": [prod_id],
            "order_total": 149.90,
            "order_typepay": "Crédito",
            "order_address": "Rua das Palmeiras, 456",
            "order_section": "Calças"
        }
    )
    assert response.status_code == 200

def test_get_orders():
    response = client.get("/orders")
    assert response.status_code == 200
    assert len(response.json()) > 0

# def test_get_order_by_id():
#     response = client.get("/orders/1")
#     assert response.status_code == 200
#     assert response.json()["order_cli"] == 1

def test_delete_order():
    response = client.delete("/orders/1")
    assert response.status_code == 200
    assert response.json()["ok"] is True
