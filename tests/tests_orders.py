import pytest
from fastapi.testclient import TestClient

from app.utils.session import SessionDep

from app.models.model_client import Client
from app.models.model_product import Product

from app.utils.database import create_db_and_tables

@pytest.fixture(autouse=True, scope="module")
def setup_database():
    create_db_and_tables()

def create_client(session: SessionDep):
    client = Client(cli_name="João", cli_email="joao@email.com", cli_cpf="12345678901", cli_phone="11999999999")
    session.add(client)
    session.commit()
    return client

def create_product(session: SessionDep):
    product = Product(prod_name="Camisa", prod_desc="Algodão", prod_price=50.0, prod_stock=10, prod_size=["M"], prod_color=["preto"], prod_cat="Masculino", prod_barcode="123456789", prod_section="Blusas")
    session.add(product)
    session.commit()
    return product

def test_create_order(client: TestClient, session: SessionDep):
    client_obj = create_client(session)
    product = create_product(session)

    response = client.post("/orders", json={
        "order_cli": client_obj.cli_id,
        "order_prods": [product.prod_id]
    })

    assert response.status_code == 200
    data = response.json()
    assert data["order_cli"] == client_obj.cli_id
    assert data["order_status"] == "Em andamento"
    assert product.prod_stock == 9  # estoque decrementado

def test_list_orders(client: TestClient, session: SessionDep):
    response = client.get("/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_order_by_id(client: TestClient, session: SessionDep):
    client_obj = create_client(session)
    product = create_product(session)

    order = client.post("/orders", json={
        "order_cli": client_obj.cli_id,
        "order_prods": [product.prod_id]
    }).json()

    response = client.get(f"/orders/{order['order_id']}")
    assert response.status_code == 200
    assert response.json()["order_id"] == order["order_id"]

def test_update_order_status(client: TestClient, session: SessionDep):
    client_obj = create_client(session)
    product = create_product(session)

    order = client.post("/orders", json={
        "order_cli": client_obj.cli_id,
        "order_prods": [product.prod_id]
    }).json()

    response = client.put(f"/orders/{order['order_id']}", json={
        "order_status": "Entregue"
    })

    assert response.status_code == 200
    assert response.json()["order_status"] == "Entregue"

def test_delete_order(client: TestClient, session: SessionDep):
    client_obj = create_client(session)
    product = create_product(session)

    order = client.post("/orders", json={
        "order_cli": client_obj.cli_id,
        "order_prods": [product.prod_id]
    }).json()

    response = client.delete(f"/orders/{order['order_id']}")
    assert response.status_code == 200
    assert response.json()["ok"] is True

    response = client.get(f"/orders/{order['order_id']}")
    assert response.status_code == 404
