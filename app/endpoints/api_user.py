from fastapi import HTTPException, APIRouter, Header, Depends
from sqlmodel import select
import sentry_sdk
from datetime import datetime
from ..models.model_user import User, UserCreate, UserUpdate, UserLogin
from ..utils.custom_types import VALID_USER_TYPES
from ..utils.session import SessionDep
from ..utils.auth import verify_password, create_access_token, decode_token, get_password_hash
from ..models.model_user import User
from ..utils.permissions import require_user_type

router = APIRouter()

@router.post(
    "/auth/login",
    summary="Login do usuário",
    description="Realiza a autenticação do usuário e retorna um token JWT válido.",
    response_description="Token de acesso JWT para autenticação."
)
def auth_login(session: SessionDep, data: UserLogin):
    try: 
        user = session.exec(select(User).where(User.usr_email == data.usr_email)).first()

        if not user or not verify_password(data.usr_pass, user.usr_pass):
            raise HTTPException(status_code=401, detail="Credenciais inválidas.")
        
        token = create_access_token({"sub": user.usr_email})
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao fazer login.")


@router.post(
    "/auth/register",
    response_model=User,
    summary="Registrar novo usuário",
    description="Cria um novo usuário no sistema. Apenas administradores ou gerentes podem registrar novos usuários.",
    response_description="Usuário registrado com sucesso."
)
def auth_register(session: SessionDep, data: UserCreate, current_user: User = Depends(require_user_type(["administrador", "gerente"]))):
    try: 
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
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao registrar usuário.")


@router.put(
    "/auth/register/{id}",
    response_model=User,
    summary="Atualizar tipo de usuário",
    description="Atualiza o tipo de usuário (perfil) de um usuário existente pelo ID.",
    response_description="Usuário atualizado com sucesso."
) 
def change_user_type(session: SessionDep, data: UserUpdate, id: int, current_user: User = Depends(require_user_type(["administrador", "gerente"]))):
    try:
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
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao editar tipo de usuário.")


 
@router.post(
    "/auth/refresh-token",
    summary="Renovar token JWT",
    description="Gera um novo token JWT válido a partir de um token expirado ou prestes a expirar.",
    response_description="Novo token de acesso JWT."
)
def auth_refresh_token(authorization: str = Header(...)):
    try: 
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)

        if not payload:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado.")

        new_token = create_access_token({"sub": payload.get("sub")})
        return {"access_token": new_token, "token_type": "bearer"}
    
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao realizar refresh JWT.")