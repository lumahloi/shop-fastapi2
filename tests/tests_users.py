import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app
from app.models.model_user import User
from app.utils.auth import get_password_hash, create_access_token
from app.utils.custom_types import VALID_USER_TYPES
from app.utils.session import SessionDep
from app.utils.database import create_db_and_tables

client = TestClient(app)

@pytest.fixture(autouse=True, scope="module")
def setup_database():
    create_db_and_tables()

@pytest.fixture
def new_user_data():
    return {
        "usr_email": "test@example.com",
        "usr_password": "test123",
        "usr_type": VALID_USER_TYPES[0]
    }

def test_register_user_success(session: SessionDep, override_session, new_user_data):
    response = client.post("/auth/register", json=new_user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["usr_email"] == new_user_data["usr_email"]

def test_register_user_duplicate_email(session: SessionDep, override_session, new_user_data):
    session.add(User(
        usr_email=new_user_data["usr_email"],
        usr_password=get_password_hash(new_user_data["usr_password"]),
        usr_type=new_user_data["usr_type"],
        usr_createdat=datetime.utcnow().replace(tzinfo=None),
        usr_lastupdate=datetime.utcnow().replace(tzinfo=None),
        usr_active=True
    ))
    session.commit()

    response = client.post("/auth/register", json=new_user_data)
    assert response.status_code == 401
    assert "Já existe um usuário" in response.json()["detail"]

def test_login_success(session: SessionDep, override_session, new_user_data):
    hashed_password = get_password_hash(new_user_data["usr_password"])
    session.add(User(
        usr_email=new_user_data["usr_email"],
        usr_password=hashed_password,
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

def test_login_invalid_credentials(session: SessionDep, override_session, new_user_data):
    wrong_data = {"usr_email": "wrong@example.com", "usr_password": "wrongpass", "usr_type": new_user_data["usr_type"]}
    response = client.post("/auth/login", json=wrong_data)
    assert response.status_code == 401

def test_refresh_token_success(session: SessionDep, override_session, new_user_data):
    token = create_access_token({"sub": new_user_data["usr_email"]})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/auth/refresh-token", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_refresh_token_invalid(session: SessionDep, override_session):
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = client.post("/auth/refresh-token", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Token inválido ou expirado."

def test_change_user_type_success(session: SessionDep, override_session, new_user_data):
    user = User(
        usr_email=new_user_data["usr_email"],
        usr_password=get_password_hash(new_user_data["usr_password"]),
        usr_type=new_user_data["usr_type"],
        usr_createdat=datetime.utcnow().replace(tzinfo=None),
        usr_lastupdate=datetime.utcnow().replace(tzinfo=None),
        usr_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    update_data = {"usr_type": VALID_USER_TYPES[-1]}
    response = client.put(f"/auth/register/{user.usr_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["usr_type"] == VALID_USER_TYPES[-1]
