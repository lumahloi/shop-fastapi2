import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app
from app.models.model_user import User
from app.utils.auth import get_password_hash, create_access_token
from app.utils.custom_types import VALID_USER_TYPES
from app.utils.session import get_session
from app.utils.session import Session
from app.utils.database import create_db_and_tables
from app.utils.services import unique_email

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    create_db_and_tables()
    
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
def session():
    return next(get_session())

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

def test_register_user_success(session: Session, new_user_data, admin_auth_headers):
    response = client.post("/auth/register", json=new_user_data, headers=admin_auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["usr_email"] == new_user_data["usr_email"]

def test_register_user_duplicate_email(session: Session, new_user_data, admin_auth_headers):
    session.add(User(
        usr_name=new_user_data["usr_name"],
        usr_email=new_user_data["usr_email"],
        usr_pass=get_password_hash(new_user_data["usr_pass"]),
        usr_type=new_user_data["usr_type"],
        usr_createdat=datetime.utcnow().replace(tzinfo=None),
        usr_lastupdate=datetime.utcnow().replace(tzinfo=None),
        usr_active=True
    ))
    session.commit()

    response = client.post("/auth/register", json=new_user_data, headers=admin_auth_headers)
    assert response.status_code == 401
    assert "Já existe um usuário" in response.json()["detail"]

def test_login_success(session: Session, new_user_data):
    hashed_password = get_password_hash(new_user_data["usr_pass"])
    session.add(User(
        usr_name=new_user_data["usr_name"],
        usr_email=new_user_data["usr_email"],
        usr_pass=hashed_password,
        usr_type=new_user_data["usr_type"],
        usr_createdat=datetime.utcnow().replace(tzinfo=None),
        usr_lastupdate=datetime.utcnow().replace(tzinfo=None),
        usr_active=True
    ))
    session.commit()

    response = client.post("/auth/login", json=new_user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_invalid_credentials(session: Session, new_user_data):
    wrong_data = {"usr_name": "testezinho", "usr_email": "wrong@example.com", "usr_pass": "wrongpass", "usr_type": new_user_data["usr_type"]}
    response = client.post("/auth/login", json=wrong_data)
    assert response.status_code == 401

def test_refresh_token_success(session: Session, new_user_data):
    token = create_access_token({"sub": new_user_data["usr_email"]})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/auth/refresh-token", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_refresh_token_invalid(session: Session):
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = client.post("/auth/refresh-token", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Token inválido ou expirado."

def test_change_user_type_success(session: Session, new_user_data, admin_auth_headers):
    user = User(
        usr_name=new_user_data["usr_name"],
        usr_email=new_user_data["usr_email"],
        usr_pass=get_password_hash(new_user_data["usr_pass"]),
        usr_type=new_user_data["usr_type"],
        usr_createdat=datetime.utcnow().replace(tzinfo=None),
        usr_lastupdate=datetime.utcnow().replace(tzinfo=None),
        usr_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    update_data = {"usr_type": VALID_USER_TYPES[-1]}
    response = client.put(f"/auth/register/{user.usr_id}", json=update_data, headers=admin_auth_headers)
    assert response.status_code == 200
    assert response.json()["usr_type"] == VALID_USER_TYPES[-1]