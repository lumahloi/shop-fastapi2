from typing import Union, Annotated
from fastapi import FastAPI, Query, Depends, HTTPException
from sqlmodel import SQLModel, create_engine, Session, select, Field


app = FastAPI()


################################### database

postgresql_file_name = ".db"
postgresql_url = f"postgresql:///{postgresql_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(postgresql_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# For production you would probably use a migration script that runs before you start your app. 🤓 SQLModel will have migration utilities wrapping Alembic, but for now, you can use Alembic directly.
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


################################### baseModels

class User(SQLModel, table=True):
    usr_id: int = Field(primary_key=True)
    usr_name: str = Query(max_length=40)
    usr_email: str = Query(max_length=20)
    usr_pass: str = Query(max_length=20)
    usr_type: int
    usr_active: bool
    usr_createdat: str
    usr_lastupdate: str
    
class Client(SQLModel, table=True):
    cli_id: int = Field(primary_key=True)
    cli_name: str = Query(max_length=20), Field(index=True)
    cli_email: str = Query(max_length=20), Field(index=True)
    cli_cpf: str = Query(max_length=11), Field(index=True)
    cli_phone: str = Query(max_length=11)
    cli_address: str = Query(max_length=100)
    cli_createdat: str
    cli_active: bool
    
class Product(SQLModel, table=True):
    prod_id: int = Field(primary_key=True)
    prod_name: str = Query(max_length=100), Field(index=True)
    prod_desc: str = Query(max_length=100)
    prod_price: float = Field(index=True)
    prod_stock: int = Field(0, gt=0)
    prod_size: list
    prod_color: list
    prod_cat: str = Field(index=True)
    prod_imgs: list
    prod_active: bool = Field(index=True)
    prod_barcode: str 
    prod_section: str 
    prod_dtval: str 
    prod_createdat: str
    prod_lastupdate: str
    
class Order(SQLModel, table=True):
    order_id: int = Field(primary_key=True, index=True)
    order_cli: int = Field(index=True)
    order_period: str = Field(index=True)
    order_status: str = Field(index=True)
    order_total: float
    order_typepay: str
    order_address: str = Query(max_length=100)
    order_section: str = Field(index=True)
    order_prods: list
    order_createdat: str



################################### AUTH

# Autenticação de usuário.
@app.post("/auth/login") # POST
def auth_login(user: Annotated[User, Query()]):
    ...

# Registro de novo usuário.
@app.post("/auth/register") # POST
def auth_register(user: Annotated[User, Query()]):
    ...

#  Refresh de token JWT.    
@app.post("/auth/refresh-token") # POST
def auth_refresh_token():
    ...
    
################################### CLIENTS

# Listar todos os clientes, com suporte a paginação e filtro por nome e email.    
@app.get("/clients") # GET
def clients_get(client: Annotated[Client, Query()], num_page: Union[int, 1], session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=10)] = 10) -> list[Client]:
    clients = session.exec(select(Client).offset(offset).limit(limit)).all()
    return clients
    ...

# Criar um novo cliente, validando email e CPF únicos.    
@app.post("/clients") # POST
def clients_post(client: Annotated[Client, Query()]):
    ...

# Obter informações de um cliente específico.    
@app.get("/clients/{id}") # GET
def clients_get(id: int, session: SessionDep) -> Client:
    client = session.get(Client, id)
    if not client:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este cliente")
    return Client

# Atualizar informações de um cliente específico.
@app.put("/clients/{id}") # PUT
def clients_put():
    ...

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
@app.get("/products") # GET
def products_get(product: Annotated[Product, Query()], num_page: Union[int, 1], session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=10)] = 10) -> list[Product]:
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    return products
    
# Criar um novo produto, contendo os seguintes atributos: descrição, valor de venda, código de barras, seção, estoque inicial, e data de validade (quando aplicável) e imagens.    
@app.post("/products") # POST
def products_post(product: Annotated[Product, Query()]):
    ...

# Obter informações de um produto específico.    
@app.get("/products/{id}") # GET
def products_get(id: int, session: SessionDep) -> Product:
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este produto")
    return Product

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
def orders_get(order: Annotated[Order, Query()], session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=10)] = 10) -> list[Order]:
    orders = session.exec(select(Order).offset(offset).limit(limit)).all()
    return orders

# Criar um novo pedido contendo múltiplos produtos, validando estoque disponível.    
@app.post("/orders") # POST
def orders_post(order: Annotated[Order, Query()]):
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