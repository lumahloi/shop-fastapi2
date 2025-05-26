import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from datetime import datetime

from app.main import app  # ajuste conforme a localização da sua instância FastAPI
from app.models.model_product import Product

# Cria banco de dados em memória para testes
from ..utils.database import engine

@pytest.fixture
def session():
    with Session(engine) as session:
        yield session

@pytest.fixture
def client(session, monkeypatch):
    def override_get_session():
        yield session
    app.dependency_overrides = {}
    app.dependency_overrides["app.services.session.SessionDep"] = override_get_session
    return TestClient(app)

def test_create_product_success(client, session):
    data = {
        "prod_name": "Camiseta Teste",
        "prod_price": 59.99,
        "prod_size": ["M"],
        "prod_color": ["preto"],
        "prod_cat": "Masculino",
        "prod_section": "Blusas",
        "prod_initialstock": 10,
    }
    response = client.post("/products", json=data)
    assert response.status_code == 200
    assert response.json()["prod_name"] == "Camiseta Teste"

@pytest.mark.parametrize("invalid_size", [["XG"], ["M", "XXG"]])
def test_create_product_invalid_size(client, invalid_size):
    data = {
        "prod_name": "Produto Inválido",
        "prod_price": 39.90,
        "prod_size": invalid_size,
        "prod_color": ["preto"],
        "prod_cat": "Masculino",
        "prod_section": "Blusas",
        "prod_initialstock": 5,
    }
    response = client.post("/products", json=data)
    assert response.status_code == 400
    assert "tamanho" in response.json()["detail"]["msg"].lower()

@pytest.mark.parametrize("invalid_color", [["roxo-neon"], ["verde", "inexistente"]])
def test_create_product_invalid_color(client, invalid_color):
    data = {
        "prod_name": "Produto Inválido",
        "prod_price": 79.90,
        "prod_size": ["M"],
        "prod_color": invalid_color,
        "prod_cat": "Masculino",
        "prod_section": "Blusas",
        "prod_initialstock": 3,
    }
    response = client.post("/products", json=data)
    assert response.status_code == 400
    assert "cor" in response.json()["detail"]["msg"].lower()

def test_get_product_by_id(client, session):
    product = Product(
        prod_name="Produto Existente",
        prod_price=49.90,
        prod_size=["M"],
        prod_color=["azul"],
        prod_cat="Feminino",
        prod_section="Calças",
        prod_initialstock=15,
        prod_stock=15,
        prod_createdat=datetime.utcnow(),
        prod_lastupdate=datetime.utcnow(),
    )
    session.add(product)
    session.commit()
    session.refresh(product)

    response = client.get(f"/products/{product.prod_id}")
    assert response.status_code == 200
    assert response.json()["prod_name"] == "Produto Existente"

def test_update_product(client, session):
    product = Product(
        prod_name="Produto Atualizar",
        prod_price=100,
        prod_size=["G"],
        prod_color=["branco"],
        prod_cat="Masculino",
        prod_section="Shorts",
        prod_initialstock=20,
        prod_stock=20,
        prod_createdat=datetime.utcnow(),
        prod_lastupdate=datetime.utcnow(),
    )
    session.add(product)
    session.commit()
    session.refresh(product)

    data = {"prod_price": 120}
    response = client.put(f"/products/{product.prod_id}", json=data)
    assert response.status_code == 200
    assert response.json()["prod_price"] == 120

def test_delete_product(client, session):
    product = Product(
        prod_name="Produto Deletar",
        prod_price=80,
        prod_size=["P"],
        prod_color=["verde"],
        prod_cat="Feminino",
        prod_section="Vestidos",
        prod_initialstock=8,
        prod_stock=8,
        prod_createdat=datetime.utcnow(),
        prod_lastupdate=datetime.utcnow(),
    )
    session.add(product)
    session.commit()
    session.refresh(product)

    response = client.delete(f"/products/{product.prod_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}
