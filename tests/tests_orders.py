import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime, date

from app.main import app
from app.models.model_client import Client
from app.models.model_product import Product
from app.models.model_order import Order
from app.utils.custom_types import StatusType, SectionType, PaymentType
from app.utils.database import create_db_and_tables
from app.utils.session import get_session
from app.utils.services import unique_cpf, unique_email

@pytest.fixture(autouse=True)
def setup_database():
    create_db_and_tables()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def session():
    return next(get_session())

# Fixtures para dados de teste
@pytest.fixture
def test_client(session: Session):
    client = Client(
        cli_name="Test Client",
        cli_email=unique_email(),
        cli_phone="1234567890",
        cli_address="Test Address 123",
        cli_cpf=unique_cpf()
    )
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

@pytest.fixture
def test_products(session: Session):
    products = [
        Product(
            prod_name="Product 1",
            prod_desc="Description 1",
            prod_price=10.99,
            prod_stock=10,
            prod_section=SectionType.blusas,
            prod_size=["M"],
            prod_color=["red"],
            prod_cat="masculino",
            prod_barcode=3*43,
            prod_initialstock=10
        ),
        Product(
            prod_name="Product 2",
            prod_desc="Description 2",
            prod_price=20.50,
            prod_stock=5,
            prod_section=SectionType.calças,
            prod_size=["L"],
            prod_color=["blue"],
            prod_cat="feminino",
            prod_barcode=3*43,
        )
    ]
    for product in products:
        session.add(product)
    session.commit()
    return products

@pytest.fixture
def test_order(test_client, test_products, session: Session):
    order = Order(
        order_section=SectionType.blusas,
        order_cli=test_client.cli_id,
        order_total=31.49,
        order_typepay=PaymentType.credito,
        order_address="Test Address 123",
        order_prods=[p.prod_id for p in test_products],
        order_status=StatusType.andamento,
        order_createdat=datetime.utcnow().replace(tzinfo=None),
        order_period=datetime.utcnow().replace(tzinfo=None),
    )
    
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

# Testes
def test_create_order(client: TestClient, test_client, test_products):
    order_data = {
        "order_section": "blusas",
        "order_cli": test_client.cli_id,
        "order_total": 31.49,
        "order_typepay": "crédito",
        "order_address": "Test Address 123",
        "order_prods": [p.prod_id for p in test_products]
    }
    
    response = client.post("/orders", json=order_data)
    data = response.json()
    
    assert response.status_code == 200
    assert data["order_cli"] == test_client.cli_id
    assert len(data["order_prods"]) == 2
    assert data["order_status"] == "em andamento"

def test_create_order_with_invalid_client(client: TestClient, test_products):
    order_data = {
        "order_section": "blusas",
        "order_cli": 999,  # ID inválido
        "order_total": 31.49,
        "order_typepay": "crédito",
        "order_address": "Test Address 123",
        "order_prods": [p.prod_id for p in test_products]
    }
    
    response = client.post("/orders", json=order_data)
    assert response.status_code == 404
    assert "Cliente não reconhecido" in response.json()["detail"]

def test_create_order_with_out_of_stock_product(client: TestClient, test_client, session: Session):
    # Criar produto com estoque zero
    out_of_stock_product = Product(
        prod_name="Out of Stock Product",
        prod_desc="Description",
        prod_price=15.99,
        prod_initialstock=0,
        prod_section=SectionType.blusas,
        prod_size=["M"],
        prod_color=["red"],
        prod_cat="masculino",
        prod_barcode="3"*43,
    )
    session.add(out_of_stock_product)
    session.commit()
    session.refresh(out_of_stock_product)
    
    order_data = {
        "order_section": "blusas",
        "order_cli": test_client.cli_id,
        "order_total": 15.99,
        "order_typepay": "crédito",
        "order_address": "Test Address 123",
        "order_prods": [out_of_stock_product.prod_id]
    }
    
    response = client.post("/orders", json=order_data)
    assert response.status_code == 400
    assert "está sem estoque" in response.json()["detail"]

def test_get_order(client: TestClient, test_order):
    response = client.get(f"/orders/{test_order.order_id}")
    data = response.json()
    
    assert response.status_code == 200
    assert data["order_id"] == test_order.order_id
    assert data["order_cli"] == test_order.order_cli

def test_get_nonexistent_order(client: TestClient):
    response = client.get("/orders/999")
    assert response.status_code == 404
    assert "Não foi possível encontrar este pedido" in response.json()["detail"]

def test_list_orders(client: TestClient, test_order):
    response = client.get("/orders")
    data = response.json()
    
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["order_id"] == test_order.order_id

def test_list_orders_with_filters(client: TestClient, test_order, test_client):
    # Filtro por cliente
    response = client.get(f"/orders?client={test_client.cli_id}")
    data = response.json()
    assert len(data) == 1
    
    # Filtro por seção
    response = client.get(f"/orders?section=blusas")
    data = response.json()
    assert len(data) == 1
    
    # Filtro por status
    response = client.get(f"/orders?status=em andamento")
    data = response.json()
    assert len(data) == 1
    
    # Filtro por data
    today = datetime.utcnow().isoformat()
    response = client.get(f"/orders?period={today}")
    data = response.json()
    assert len(data) == 1
    
    # Filtro que não deve retornar resultados
    response = client.get("/orders?status=cancelado")
    data = response.json()
    assert len(data) == 0

def test_update_order_status(client: TestClient, test_order):
    update_data = {"order_status": "pagamento confirmado"}
    response = client.put(f"/orders/{test_order.order_id}", json=update_data)
    data = response.json()
    
    assert response.status_code == 200
    assert data["order_status"] == "pagamento confirmado"

def test_update_nonexistent_order(client: TestClient):
    update_data = {"order_status": "pagamento confirmado"}
    response = client.put("/orders/999", json=update_data)
    assert response.status_code == 404
    assert "Não foi possível encontrar este pedido" in response.json()["detail"]

def test_delete_order(client: TestClient, test_order):
    response = client.delete(f"/orders/{test_order.order_id}")
    assert response.status_code == 200
    assert response.json()["ok"] == True
    
    # Verifica se o pedido foi realmente removido
    response = client.get(f"/orders/{test_order.order_id}")
    assert response.status_code == 404

def test_delete_nonexistent_order(client: TestClient):
    response = client.delete("/orders/999")
    assert response.status_code == 404
    assert "Não foi possível encontrar este pedido" in response.json()["detail"]

def test_pagination_in_orders_list(client: TestClient,  test_client, test_products, session: Session):
    # Criar múltiplos pedidos para testar paginação
    orders = []
    for i in range(15):
        order = Order(
            order_section=SectionType.blusas,
            order_cli=test_client.cli_id,
            order_total=10.99 * (i+1),
            order_typepay=PaymentType.credito,
            order_address=f"Test Address {i}",
            order_prods=[test_products[0].prod_id],
            order_status=StatusType.andamento,
            order_createdat=datetime.utcnow().replace(tzinfo=None),
            order_period=datetime.utcnow().replace(tzinfo=None)
        )
        session.add(order)
        orders.append(order)
    session.commit()
    
    # Primeira página deve ter 10 itens (limite padrão)
    response = client.get("/orders")
    data = response.json()
    assert len(data) == 10
    
    # Segunda página deve ter 5 itens (15 total - 10 na primeira página)
    response = client.get("/orders?num_page=2")
    data = response.json()
    assert len(data) == 5
    
    # Testar limite personalizado
    response = client.get("/orders?limit=5")
    data = response.json()
    assert len(data) == 5