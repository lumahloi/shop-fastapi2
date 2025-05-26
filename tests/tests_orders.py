import pytest
from fastapi.testclient import TestClient
from main import app 
from sqlmodel import SQLModel, Session

from utils.session import get_session

from models.model_client import Client
from models.model_product import Product

from ..utils.database import engine

# Fixture para sessão de teste
@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

# Fixture para o client com override da sessão
@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_override():
        return session
    app.dependency_overrides[get_session] = get_override
    return TestClient(app)

def create_client(session: Session):
    client = Client(cli_name="João", cli_email="joao@email.com", cli_cpf="12345678901", cli_phone="11999999999")
    session.add(client)
    session.commit()
    return client

def create_product(session: Session):
    product = Product(prod_name="Camisa", prod_desc="Algodão", prod_price=50.0, prod_stock=10, prod_size=["M"], prod_color=["preto"], prod_cat="Masculino", prod_barcode="123456789", prod_section="Blusas")
    session.add(product)
    session.commit()
    return product

def test_create_order(client: TestClient, session: Session):
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

def test_list_orders(client: TestClient, session: Session):
    response = client.get("/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_order_by_id(client: TestClient, session: Session):
    client_obj = create_client(session)
    product = create_product(session)

    order = client.post("/orders", json={
        "order_cli": client_obj.cli_id,
        "order_prods": [product.prod_id]
    }).json()

    response = client.get(f"/orders/{order['order_id']}")
    assert response.status_code == 200
    assert response.json()["order_id"] == order["order_id"]

def test_update_order_status(client: TestClient, session: Session):
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

def test_delete_order(client: TestClient, session: Session):
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
