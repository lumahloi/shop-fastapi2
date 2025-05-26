import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlmodel import Session
from datetime import datetime
from app.models.model_product import Product
from app.utils.session import get_session
from app.utils.database import create_db_and_tables
from app.utils.custom_types import SectionType

@pytest.fixture(autouse=True)
def setup_database():
    create_db_and_tables()

@pytest.fixture
def session():
    return next(get_session())

@pytest.fixture
def client():
    return TestClient(app)

def test_create_product_success(client, session: Session):
    data = {
            "prod_name":"Camiseta Teste",
            "prod_price":59.99,
            "prod_size":["M"],
            "prod_color":["Azul"],
            "prod_cat":"Feminino",
            "prod_section":"Blusas",
            "prod_initialstock":10,
            "prod_barcode":"1"*13,
    }
    response = client.post("/products", json=data)
    assert response.status_code == 200, response.text
    assert response.json()["prod_name"] == "Camiseta Teste"

@pytest.mark.parametrize("invalid_size", [["XG"], ["M", "XXG"]])
def test_create_product_invalid_size(client, invalid_size):
    data = {
        "prod_name": "Produto Inválido",
        "prod_price": 39.90,
        "prod_size": invalid_size,
        "prod_color": ["preto"],
        "prod_cat": "masculino",
        "prod_section": "blusas",
        "prod_initialstock": 5,
        "prod_barcode":"1"*13,
    }
    response = client.post("/products", json=data)
    assert response.status_code == 400, response.text
    assert "tamanho" in response.json()["detail"]["msg"].lower()

@pytest.mark.parametrize("invalid_color", [["roxo-neon"], ["verde", "inexistente"]])
def test_create_product_invalid_color(client, invalid_color):
    data = {
        "prod_name": "Produto Inválido",
        "prod_price": 79.90,
        "prod_size": ["m"],
        "prod_color": invalid_color,
        "prod_cat": "masculino",
        "prod_section": "blusas",
        "prod_initialstock": 3,
        "prod_barcode":"1"*13,
    }
    response = client.post("/products", json=data)
    assert response.status_code == 400, response.text
    assert "cor" in response.json()["detail"]["msg"].lower()

def test_get_product_by_id(client, session: Session):
    product = Product(
        prod_name="Produto Existente",
        prod_price=49.90,
        prod_size=["m"],
        prod_color=["azul"],
        prod_cat="feminino",
        prod_section="calças",
        prod_initialstock=15,
        prod_createdat=datetime.utcnow().replace(tzinfo=None),
        prod_lastupdate=datetime.utcnow().replace(tzinfo=None),
        prod_barcode="1"*13,
    )
    session.add(product)
    session.commit()
    session.refresh(product)

    response = client.get(f"/products/{product.prod_id}")
    assert response.status_code == 200, response.text
    assert response.json()["prod_name"] == "Produto Existente"

def test_update_product(client, session: Session):
    product = Product(
        prod_name="Produto Atualizar",
        prod_price=100,
        prod_size=["g"],
        prod_color=["branco"],
        prod_cat="masculino",
        prod_section="shorts",
        prod_initialstock=20,
        prod_createdat=datetime.utcnow().replace(tzinfo=None),
        prod_lastupdate=datetime.utcnow().replace(tzinfo=None),
        prod_barcode="1"*13,
    )
    session.add(product)
    session.commit()
    session.refresh(product)

    data = {"prod_price": 120}
    response = client.put(f"/products/{product.prod_id}", json=data)
    assert response.status_code == 200, response.text
    assert response.json()["prod_price"] == 120

def test_delete_product(client, session: Session):
    product = Product(
        prod_name="Produto Deletar",
        prod_price=80,
        prod_size=["p"],
        prod_color=["verde"],
        prod_cat="feminino",
        prod_section="vestidos",
        prod_initialstock=8,
        prod_createdat=datetime.utcnow().replace(tzinfo=None),
        prod_lastupdate=datetime.utcnow().replace(tzinfo=None),
        prod_barcode="1"*13,
    )
    session.add(product)
    session.commit()
    session.refresh(product)

    response = client.delete(f"/products/{product.prod_id}")
    assert response.status_code == 200, response.text
    assert response.json() == {"ok": True}
