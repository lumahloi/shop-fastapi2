from fastapi import FastAPI, Query, HTTPException
from sqlmodel import select
from typing import  Annotated, Union
from datetime import datetime
import re

from services.database import create_db_and_tables
from services.sql_models import User, Client, Product, Order
from services.sql_models import UserCreate, ClientCreate, ProductCreate, OrderCreate
from services.sql_models import ClientUpdate, ProductUpdate
from services.session import SessionDep



app = FastAPI()



# For production you would probably use a migration script that runs before you start your app. 🤓 SQLModel will have migration utilities wrapping Alembic, but for now, you can use Alembic directly.
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


################################### AUTH

# Autenticação de usuário.
@app.post("/auth/login") # POST
def auth_login(user: Annotated[User, Query()]):
    ...

# Registro de novo usuário.
@app.post("/auth/register", response_model=User) # POST
def auth_register(
    session: SessionDep,
    data: UserCreate
) -> User:
    email_exists = session.exec(select(User).where(User.usr_email == data.usr_email)).first()
    
    if email_exists:
        raise HTTPException(status_code=401, detail="Já existe um usuário cadastrado com este email.")
    
    new_user = User(
        **data.dict(),
        usr_active=True,
        usr_createdat=datetime.utcnow(),
        usr_lastupdate=datetime.utcnow()
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user  

#  Refresh de token JWT.    
@app.post("/auth/refresh-token") # POST
def auth_refresh_token():
    ...
    
################################### CLIENTS

# Listar todos os clientes, com suporte a paginação e filtro por nome e email.    
@app.get("/clients", response_model=list[Client]) # GET
def clients_get(
    session: SessionDep, 
    name: Union[str | None] = Query(None, alias="name"),
    email: Union[str | None] = Query(None, alias="email"),
    num_page: int = 1, 
    limit: Annotated[int, Query(le=10)] = 10,
):
    offset = (num_page - 1) * limit
    
    query = select(Client)

    if name:
        query = query.where(Client.name.ilike(f"%{name}%"))
    if email:
        query = query.where(Client.email.ilike(f"%{email}%"))

    results = session.exec(query.offset(offset).limit(limit)).all()
    
    return results

# Criar um novo cliente, validando email e CPF únicos.    
@app.post("/clients", response_model=Client) # POST
def clients_post(
    session: SessionDep,
    data: ClientCreate
) -> Client:
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
        usr_active=True,
        usr_createdat=datetime.utcnow()
    )
    
    session.add(new_client)
    session.commit()
    session.refresh(new_client)
    
    return new_client  

# Obter informações de um cliente específico.    
@app.get("/clients/{id}", response_model=Client) # GET
def clients_get(id: int, session: SessionDep):
    client = session.get(Client, id)
    if not client:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este cliente")
    return client

# Atualizar informações de um cliente específico.
@app.put("/clients/{id}", response_model=Client) # PUT
def clients_put(
    id: int,
    data: ClientUpdate,
    session: SessionDep
):
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
@app.delete("/clients/{id}") # DELETE
def clients_delete(id: int, session: SessionDep):
    client = session.get(Client, id)
    if not client:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este cliente")
    session.delete(client)
    session.commit()
    return {"ok": True}
    
################################### PRODUCTS

# Listar todos os produtos, com suporte a paginação e filtros por categoria, preço e disponibilidade.
@app.get("/products", response_model=list[Product]) # GET
def products_get(
    session: SessionDep,
    category: Union[str | None] = Query(None, alias="category"),
    price: Union[float | None] = Query(None, alias="price"),
    availability: Union[bool | None] = Query(None, alias="availability"),
    num_page: int = 1,
    limit: Annotated[int, Query(le=10)] = 10
):
    offset = (num_page - 1) * limit
    
    query = select(Product)

    if category:
        query = query.where(Product.category.ilike(f"%{category}%"))
    if price:
        query = query.where(Product.price.ilike(f"%{price}%"))
    if availability:
        query = query.where(Product.availability.ilike(f"%{availability}%"))

    results = session.exec(query.offset(offset).limit(limit)).all()
    
    return results
    
# Criar um novo produto, contendo os seguintes atributos: descrição, valor de venda, código de barras, seção, estoque inicial, e data de validade (quando aplicável) e imagens.    
@app.post("/products", response_model=Product) # POST
def products_post(
    session: SessionDep,
    data: ProductCreate
):
    new_product = Product(
        **data.dict(),
        prod_active=True,
        prod_createdat=datetime.utcnow(),
        prod_lastupdate=datetime.utcnow()
    )
    
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    
    return new_product  

# Obter informações de um produto específico.    
@app.get("/products/{id}", response_model=Product) # GET
def products_get(id: int, session: SessionDep) -> Product:
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este produto")
    return product

#  Atualizar informações de um produto específico.
@app.put("/products/{id}") # PUT
def products_put():
    ...

# Excluir um produto.    
@app.delete("/products/{id}") # DELETE
def products_delete(id: int, session: SessionDep):
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este produto")
    session.delete(product)
    session.commit()
    return {"ok": True}
    
################################### PEDIDOS

# Listar todos os pedidos, incluindo os seguintes filtros: período, seção dos produtos, id_pedido, status do pedido e cliente.
@app.get("/orders") # GET
def orders_get(
    order: Annotated[Order, Query()], 
    session: SessionDep, 
    offset: int = 0, 
    limit: Annotated[int, Query(le=10)] = 10
) -> list[Order]:
    orders = session.exec(select(Order).offset(offset).limit(limit)).all()
    return orders

# Criar um novo pedido contendo múltiplos produtos, validando estoque disponível.    
@app.post("/orders") # POST
def orders_post(
    order: Annotated[Order, Query()],
    order_cli: int,
    order_period: str,
    order_total: float,
    order_typepay: str,
    order_address: str,
    order_section: str,
    # order_prods: list,
    order_status: str = 'Concluído',
):
    ...

# Obter informações de um pedido específico.    
@app.get("/orders/{id}") # GET
def orders_get(id: int, session: SessionDep) -> Order:
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este pedido")
    return Order

# Atualizar informações de um pedido específico, incluindo status do pedido.
@app.put("/orders/{id}") # PUT
def orders_put():
    ...
    
# Excluir um pedido.
@app.delete("/orders/{id}") # DELETE
def orders_delete(id: int, session: SessionDep):
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este pedido")
    session.delete(order)
    session.commit()
    return {"ok": True}