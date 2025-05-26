from fastapi import HTTPException, APIRouter, Header, Depends, Path
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
    response_description="Token de acesso JWT para autenticação.",
    responses={
        200: {
            "description": "Login realizado com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Credenciais inválidas ou erro ao fazer login.",
            "content": {
                "application/json": {
                    "example": {"detail": "Credenciais inválidas."}
                }
            }
        }
    }
)
def auth_login(
    session: SessionDep, 
    data: UserLogin
):
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
    response_description="Usuário registrado com sucesso.",
    responses={
        200: {
            "description": "Usuário registrado com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "usr_id": 1,
                        "usr_name": "João da Silva",
                        "usr_email": "joao@email.com",
                        "usr_type": "administrador",
                        "usr_active": True,
                        "usr_createdat": "2024-06-01T12:00:00",
                        "usr_lastupdate": "2024-06-01T12:00:00",
                        "usr_pass": "hash_senha"
                    }
                }
            }
        },
        400: {
            "description": "Tipo de usuário inválido.",
            "content": {
                "application/json": {
                    "example": {
                        "msg": "Tipo de usuário inválido: 'invalido'",
                        "tipos_validos": ["administrador", "gerente", "vendedor", "estoquista", "atendente"]
                    }
                }
            }
        },
        401: {
            "description": "Erro ao registrar usuário ou email já cadastrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Já existe um usuário cadastrado com este email."}
                }
            }
        }
    }
)
def auth_register(
    session: SessionDep, 
    data: UserCreate, 
    current_user: User = Depends(require_user_type(["administrador", "gerente"]))
):
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


 
@router.post(
    "/auth/refresh-token",
    summary="Renovar token JWT",
    description="Gera um novo token JWT válido a partir de um token expirado ou prestes a expirar.",
    response_description="Novo token de acesso JWT.",
    responses={
        200: {
            "description": "Token renovado com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Token inválido ou erro ao realizar refresh JWT.",
            "content": {
                "application/json": {
                    "example": {"detail": "Token inválido ou expirado."}
                }
            }
        }
    }
)
def auth_refresh_token(
    authorization: str = Header(...)
):
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
    
    
    
@router.put(
    "/auth/register/{id}",
    response_model=User,
    summary="Atualizar tipo de usuário",
    description="Atualiza o tipo de usuário (perfil) de um usuário existente pelo ID.",
    response_description="Usuário atualizado com sucesso.",
    responses={
        200: {
            "description": "Usuário atualizado com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "usr_id": 1,
                        "usr_name": "João da Silva",
                        "usr_email": "joao@email.com",
                        "usr_type": "gerente",
                        "usr_active": True,
                        "usr_createdat": "2024-06-01T12:00:00",
                        "usr_lastupdate": "2024-06-01T12:10:00",
                        "usr_pass": "hash_senha"
                    }
                }
            }
        },
        401: {
            "description": "Usuário não encontrado ou erro ao editar tipo de usuário.",
            "content": {
                "application/json": {
                    "example": {"detail": "Não foi possível encontrar este usuário."}
                }
            }
        }
    }
) 
def change_user_type(
    session: SessionDep, 
    data: UserUpdate, 
    id: int = Path(..., example=1, description="ID do cliente"), 
    current_user: User = Depends(require_user_type(["administrador", "gerente"]))
):
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


