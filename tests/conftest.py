from fastapi.testclient import TestClient
import pytest
from datetime import datetime
from sqlmodel import Session
from app.utils.services import unique_email, unique_cpf
from app.utils.auth import get_password_hash
from app.models.model_client import Client
from app.models.model_order import Order
from app.utils.custom_types import StatusType, SectionType, PaymentType, VALID_USER_TYPES
from app.models.model_product import Product
from app.main import app
from app.models.model_user import User
from app.utils.auth import create_access_token
from app.utils.session import get_session
from app.utils.session import Session
from app.utils.database import create_tables



@pytest.fixture(autouse=True)
def setup_database():
    create_tables()
    
    
    
@pytest.fixture
def auth_headers(client):
    session = next(get_session())
    admin_email = "admin@admin.com"
    admin = session.exec(
        User.select().where(User.usr_email == admin_email)
    ).first() if hasattr(User, 'select') else session.query(User).filter_by(usr_email=admin_email).first()
    if not admin:
        admin = User(
            usr_name="admin",
            usr_email=admin_email,
            usr_pass=get_password_hash("admin123"),
            usr_type="administrador",
            usr_active=True,
            usr_createdat=datetime.utcnow(),
            usr_lastupdate=datetime.utcnow()
        )
        session.add(admin)
        session.commit()
        session.refresh(admin)
    session.close()
    login_data = {"usr_email": admin_email, "usr_pass": "admin123"}
    resp = client.post("/auth/login", json=login_data)
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}



@pytest.fixture
def client_data():
    return {
        "cli_name": "João Silva",
        "cli_email": unique_email(),
        "cli_cpf": unique_cpf(),
        "cli_phone": "(11) 98765-4321",
        "cli_address": "Rua Exemplo 123"
    }



@pytest.fixture
def client():
    return TestClient(app)



@pytest.fixture
def session():
    return next(get_session())



@pytest.fixture
def client_obj(session: Session):
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
def products_obj(session: Session):
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
def order_obj(
    client_obj, 
    products_obj, 
    session: Session
):
    order = Order(
        order_section=SectionType.blusas,
        order_cli=client_obj.cli_id,
        order_total=31.49,
        order_typepay=PaymentType.credito,
        order_address="Test Address 123",
        order_prods=[p.prod_id for p in products_obj],
        order_status=StatusType.andamento,
        order_createdat=datetime.utcnow().replace(tzinfo=None),
        order_period=datetime.utcnow().replace(tzinfo=None),
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    return order



@pytest.fixture
def create_product(session):
    product = Product(
        prod_cat="roupa",
        prod_price=10.0,
        prod_desc="Produto teste",
        prod_barcode="1234567890123",
        prod_section="masculino",
        prod_initialstock=10,
        prod_name="Camiseta Teste",
        prod_size=["m"],
        prod_color=["azul"],
        prod_imgs=[]
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    yield product
    session.delete(product)
    session.commit()



@pytest.fixture
def admin_user(session: Session):
    admin = User(
        usr_name="admin",
        usr_email="admin@admin.com",
        usr_pass=get_password_hash("admin"),
        usr_type="administrador",
        usr_createdat=datetime.utcnow().replace(tzinfo=None),
        usr_lastupdate=datetime.utcnow().replace(tzinfo=None),
        usr_active=True
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin



@pytest.fixture
def admin_auth_headers(admin_user):
    token = create_access_token({"sub": admin_user.usr_email})
    return {"Authorization": f"Bearer {token}"}



@pytest.fixture
def new_user_data():
    return {
        "usr_name": "testezinho",
        "usr_email": unique_email(),
        "usr_pass": "test1234",
        "usr_type": VALID_USER_TYPES[0]
    }
