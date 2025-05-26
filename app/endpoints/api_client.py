from fastapi import Query, HTTPException, APIRouter, Depends
from sqlmodel import select
from typing import  Annotated, Union
from datetime import datetime
import re
from ..models.model_client import Client, ClientCreate, ClientUpdate
from ..utils.session import SessionDep
from ..utils.dependencies import get_current_user
from ..models.model_user import User

router = APIRouter()

# Listar todos os clientes, com suporte a paginação e filtro por nome e email.    
@router.get("/clients", response_model=list[Client]) # GET
def clients_get(
    session: SessionDep, 
    name: str = Query(None, alias="name"),
    email: str = Query(None, alias="email"),
    num_page: Union[int | None] = Query(1, alias="num_page"),
    limit: Annotated[int, Query(le=10)] = 10,
    current_user: User = Depends(get_current_user)
):
    offset = (num_page - 1) * limit
    
    query = select(Client)

    if name:
        query = query.where(Client.cli_name.ilike(f"%{name}%"))
        
    if email:
        query = query.where(Client.cli_email.ilike(f"%{email}%"))

    results = session.exec(query.offset(offset).limit(limit)).all()
    
    return results

# Criar um novo cliente, validando email e CPF únicos.    
@router.post("/clients", response_model=Client) # POST
def clients_post(session: SessionDep, data: ClientCreate, current_user: User = Depends(get_current_user)):
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

# Obter informações de um cliente específico.    
@router.get("/clients/{id}", response_model=Client) # GET
def clients_get(id: int, session: SessionDep, current_user: User = Depends(get_current_user)):
    client = session.get(Client, id)
    
    if not client:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este cliente.")
    
    return client

# Atualizar informações de um cliente específico.
@router.put("/clients/{id}", response_model=Client) # PUT
def clients_put(id: int, data: ClientUpdate, session: SessionDep, current_user: User = Depends(get_current_user)):
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

# Excluir um cliente.    
@router.delete("/clients/{id}") # DELETE
def clients_delete(id: int, session: SessionDep, current_user: User = Depends(get_current_user)):
    client = session.get(Client, id)
    
    if not client:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este cliente.")
    
    session.delete(client)
    session.commit()
    
    return {"ok": True}