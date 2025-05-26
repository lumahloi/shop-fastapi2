from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app
from app.models.model_user import User
from app.utils.auth import get_password_hash, create_access_token
from app.utils.custom_types import VALID_USER_TYPES
from app.utils.session import Session

client = TestClient(app)

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