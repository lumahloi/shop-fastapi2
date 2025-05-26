from fastapi import HTTPException, APIRouter, Header, Depends
from sqlmodel import select
from datetime import datetime
from ..models.model_user import User, UserCreate, UserUpdate
from ..utils.custom_types import VALID_USER_TYPES
from ..utils.session import SessionDep
from ..utils.auth import verify_password, create_access_token, decode_token, get_password_hash
from ..utils.dependencies import get_current_user
from ..models.model_user import User
router = APIRouter()

# Autenticação de usuário.
@router.post("/auth/login")
def auth_login(session: SessionDep, data: UserCreate): 
    user = session.exec(select(User).where(User.usr_email == data.usr_email)).first()

    if not user or not verify_password(data.usr_pass, user.usr_pass):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")
    
    token = create_access_token({"sub": user.usr_email})
    return {"access_token": token, "token_type": "bearer"}


# Registro de novo usuário.
@router.post("/auth/register", response_model=User) # POST
def auth_register(session: SessionDep, data: UserCreate):
    
    if data.usr_type not in VALID_USER_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "msg": f"Tipo de usuário inválido: '{data.usr_type}'",
                "tipos_validos": VALID_USER_TYPES
            }
        )

    email_exists = session.exec(select(User).where(User.usr_email == data.usr_email)).first()
    
    if email_exists:
        raise HTTPException(status_code=401, detail="Já existe um usuário cadastrado com este email.")
    
    new_user = User(
        **data.dict(exclude={"usr_pass"}),
        usr_pass=get_password_hash(data.usr_pass),
        usr_active=True,
        usr_createdat=datetime.utcnow(),
        usr_lastupdate=datetime.utcnow()
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user

# Mudar tipo do usuário
@router.put("/auth/register/{id}", response_model=User) # PUT
def change_user_type(session: SessionDep, data: UserUpdate, id: int, current_user: User = Depends(get_current_user)):
    
    user = session.get(User, id)
    
    if not user:
        raise HTTPException(status_code=401, detail="Não foi possível encontrar este usuário.")

    user_new_type = data.dict(exclude_unset=True)
    
    for key, value in user_new_type.items():
        setattr(user, key, value)
            
    session.add(user)
    session.commit()
    session.refresh(user)

    return user

# Refresh de token JWT.    
@router.post("/auth/refresh-token")
def auth_refresh_token(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")

    new_token = create_access_token({"sub": payload.get("sub")})
    return {"access_token": new_token, "token_type": "bearer"}