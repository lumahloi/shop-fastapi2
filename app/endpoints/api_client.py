from fastapi import Query, HTTPException, APIRouter, Depends, Path
from sqlmodel import select
import sentry_sdk
from typing import  Annotated, Union
from datetime import datetime
import re
from ..models.model_client import Client, ClientCreate, ClientUpdate
from ..utils.session import SessionDep
from ..models.model_user import User
from ..utils.permissions import require_user_type

router = APIRouter()
   
@router.get(
    "/clients",
    response_model=list[Client],
    summary="Listar clientes",
    description="Retorna uma lista paginada de clientes cadastrados, podendo filtrar por nome e email.",
    response_description="Lista de clientes encontrados.",
    responses={
        200: {
            "description": "Lista de clientes encontrados.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "cli_id": 1,
                            "cli_name": "João da Silva",
                            "cli_email": "joao@email.com",
                            "cli_phone": "11999999999",
                            "cli_cpf": "12345678901",
                            "cli_createdat": "2024-06-01T12:00:00",
                            "cli_address": "Rua Exemplo, 123",
                            "cli_active": True
                        }
                    ]
                }
            }
        },
        401: {
            "description": "Erro ao resgatar clientes.",
            "content": {
                "application/json": {
                    "example": {"detail": "Erro ao resgatar clientes."}
                }
            }
        }
    }
)
def clients_get(
    session: SessionDep, 
    name: str = Query(None, alias="name", example="João da Silva"),
    email: str = Query(None, alias="email", example="joao@email.com"),
    num_page: Union[int | None] = Query(1, alias="num_page"),
    limit: Annotated[int, Query(le=10)] = 10,
    current_user: User = Depends(require_user_type([]))
):
    try: 
        offset = (num_page - 1) * limit
        
        query = select(Client)

        if name:
            query = query.where(Client.cli_name.ilike(f"%{name}%"))
            
        if email:
            query = query.where(Client.cli_email.ilike(f"%{email}%"))

        results = session.exec(query.offset(offset).limit(limit)).all()
        
        return results
    
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao resgatar clientes.")

  
  
@router.post(
    "/clients",
    response_model=Client,
    summary="Cadastrar novo cliente",
    description="Cria um novo cliente com os dados fornecidos. O email e CPF devem ser únicos.",
    response_description="Cliente cadastrado com sucesso.",
    responses={
        200: {
            "description": "Cliente cadastrado com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "cli_id": 1,
                        "cli_name": "João da Silva",
                        "cli_email": "joao@email.com",
                        "cli_cpf": "12345678901",
                        "cli_phone": "11999999999",
                        "cli_address": "Rua Exemplo, 123",
                        "cli_createdat": "2024-06-01T12:00:00",
                        "cli_active": True
                    }
                }
            }
        },
        401: {
            "description": "Erro ao cadastrar cliente.",
            "content": {
                "application/json": {
                    "example": {"detail": "Erro ao cadastrar cliente."}
                }
            }
        }
    }
) 
def clients_post(
    session: SessionDep, 
    data: ClientCreate, 
    current_user: User = Depends(require_user_type(["administrador", "gerente", "vendedor"]))
):
    try: 
        email_exists = session.exec(select(Client).where(Client.cli_email == data.cli_email)).first()

        if email_exists:
            raise HTTPException(status_code=401, detail="Já existe um cliente cadastrado com este email.")
        
        cpf_exists = session.exec(select(Client).where(Client.cli_cpf == data.cli_cpf)).first()

        if cpf_exists:
            raise HTTPException(status_code=401, detail="Já existe um cliente cadastrado com este CPF.")
        
        data.cli_phone = re.sub(r'\D', '', data.cli_phone)
        
        data.cli_cpf = re.sub(r'\D', '', data.cli_cpf)
        
        new_client = Client(
            **data.dict(),
            cli_createdat=datetime.utcnow(),
            cli_id = None,
        )
        
        session.add(new_client)
        session.commit()
        session.refresh(new_client)
        
        return new_client 
    
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao cadastrar cliente.")



@router.get(
    "/clients/{id}",
    response_model=Client,
    summary="Obter cliente por ID",
    description="Retorna os dados de um cliente específico a partir do seu ID.",
    response_description="Dados do cliente encontrado.",
    responses={
        200: {
            "description": "Dados do cliente encontrado.",
            "content": {
                "application/json": {
                    "example": {
                        "cli_id": 1,
                        "cli_name": "João da Silva",
                        "cli_email": "joao@email.com",
                        "cli_cpf": "12345678901",
                        "cli_phone": "11999999999",
                        "cli_address": "Rua Exemplo, 123",
                        "cli_createdat": "2024-06-01T12:00:00",
                        "cli_active": True
                    }
                }
            }
        },
        404: {
            "description": "Cliente não encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Não foi possível encontrar este cliente."}
                }
            }
        },
        401: {
            "description": "Erro ao resgatar cliente.",
            "content": {
                "application/json": {
                    "example": {"detail": "Erro ao resgatar cliente."}
                }
            }
        }
    }
)
def clients_get(
    session: SessionDep, 
    current_user: User = Depends(require_user_type([])), 
    id: int = Path(..., example=1, description="ID do cliente")
):
    try: 
        client = session.get(Client, id)
        
        if not client:
            raise HTTPException(status_code=404, detail="Não foi possível encontrar este cliente.")
        
        return client
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao resgatar cliente.")



@router.put(
    "/clients/{id}",
    response_model=Client,
    summary="Atualizar cliente",
    description="Atualiza os dados de um cliente existente pelo ID.",
    response_description="Cliente atualizado com sucesso.",
    responses={
        200: {
            "description": "Cliente atualizado com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "cli_id": 1,
                        "cli_name": "João da Silva",
                        "cli_email": "joao@email.com",
                        "cli_cpf": "12345678901",
                        "cli_phone": "11999999999",
                        "cli_address": "Rua Exemplo, 123",
                        "cli_createdat": "2024-06-01T12:00:00",
                        "cli_active": True
                    }
                }
            }
        },
        404: {
            "description": "Cliente não encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Não foi possível encontrar este cliente."}
                }
            }
        },
        401: {
            "description": "Erro ao editar cliente.",
            "content": {
                "application/json": {
                    "example": {"detail": "Erro ao editar cliente."}
                }
            }
        }
    }
)
def clients_put(
    data: ClientUpdate, 
    session: SessionDep, 
    id: int = Path(..., example=1, description="ID do cliente"), 
    current_user: User = Depends(require_user_type(["administrador", "gerente", "vendedor"]))
):
    try: 
        client = session.get(Client, id)
        
        if not client:
            raise HTTPException(status_code=404, detail="Não foi possível encontrar este cliente.")
        
        client_data = data.dict(exclude_unset=True)
        
        for key, value in client_data.items():
            setattr(client, key, value)
                
        session.add(client)
        session.commit()
        session.refresh(client)

        return client
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao editar cliente.")


  
@router.delete(
    "/clients/{id}",
    summary="Deletar cliente",
    description="Remove um cliente do sistema pelo seu ID.",
    response_description="Confirmação de remoção do cliente.",
    responses={
        200: {
            "description": "Cliente removido com sucesso.",
            "content": {
                "application/json": {
                    "example": {"ok": True}
                }
            }
        },
        404: {
            "description": "Cliente não encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Não foi possível encontrar este cliente."}
                }
            }
        },
        401: {
            "description": "Erro ao deletar cliente.",
            "content": {
                "application/json": {
                    "example": {"detail": "Erro ao deletar cliente."}
                }
            }
        }
    }
)
def clients_delete(
    session: SessionDep, 
    current_user: User = Depends(require_user_type(["administrador", "gerente"])), 
    id: int = Path(..., example=1, description="ID do cliente")
):
    try: 
        client = session.get(Client, id)
        
        if not client:
            raise HTTPException(status_code=404, detail="Não foi possível encontrar este cliente.")
        
        session.delete(client)
        session.commit()
        
        return {"ok": True}
    
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao deletar cliente.")


