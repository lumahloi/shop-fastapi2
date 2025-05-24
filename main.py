from pydantic import BaseModel, Field
from typing import Union, Annotated
from fastapi import FastAPI, Query, Depends
from sqlmodel import SQLModel, create_engine, Session


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

class User(BaseModel, SQLModel, table=True):
    usr_id: int = Field(primary_key=True)
    usr_email: str = Query(max_length=20)
    usr_pass: str = Query(max_length=20)
    
class Client(BaseModel, SQLModel, table=True):
    cli_id: int = Field(default=None, primary_key=True)
    cli_name: Union[str, None] = Query(max_length=20), Field(index=True)
    cli_email: Union[str, None] = Query(max_length=20), Field(index=True)
    cli_cpf: Union[str, None] = Query(max_length=11), Field(index=True)
    
class Product(BaseModel, SQLModel, table=True):
    prod_id: int = Field(default=None, primary_key=True)
    prod_cat: str | None  = Field(index=True)
    prod_price: float = Field(index=True)
    prod_avail: bool  = Field(index=True)
    prod_desc: str | None = Query(max_length=100)
    prod_price: float
    prod_barcode: str | None 
    prod_section: str | None 
    prod_stock: int = Field(0, gt=0)
    prod_dtval: str | None 
    prod_imgs: str
    
class Order(BaseModel, SQLModel, table=True):
    order_id: int = Field(default=None, primary_key=True, index=True)
    order_period: Union[str, None] = Field(index=True)
    order_section: Union[str, None] = Field(index=True)
    order_status: Union[str, None] = Field(index=True)
    order_cli: Union[str, None] = Field(index=True)
    order_prods: list


@app.get("/")
def read_root():
    return {"Hello": "World"}

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
def clients_get(client: Annotated[Client, Query()], num_page: Union[int, 1]):
    ...

# Criar um novo cliente, validando email e CPF únicos.    
@app.post("/clients") # POST
def clients_post(client: Annotated[Client, Query()]):
    ...

# Obter informações de um cliente específico.    
@app.get("/clients/{id}") # GET
def clients_get():
    ...

# Atualizar informações de um cliente específico.
@app.put("/clients/{id}") # PUT
def clients_put():
    ...

# Excluir um cliente.    
@app.delete("/clients/{id}") # DELETE
def clients_delete():
    ...
    
################################### PRODUCTS

# Listar todos os produtos, com suporte a paginação e filtros por categoria, preço e disponibilidade.
@app.get("/products") # GET
def products_get(product: Annotated[Product, Query()], num_page: Union[int, 1]):
    ...
    
# Criar um novo produto, contendo os seguintes atributos: descrição, valor de venda, código de barras, seção, estoque inicial, e data de validade (quando aplicável) e imagens.    
@app.post("/products") # POST
def products_post(product: Annotated[Product, Query()]):
    ...

# Obter informações de um produto específico.    
@app.get("/products/{id}") # GET
def products_get():
    ...

#  Atualizar informações de um produto específico.
@app.put("/products/{id}") # PUT
def products_put():
    ...

# Excluir um produto.    
@app.delete("/products/{id}") # DELETE
def products_delete():
    ...
    
################################### PEDIDOS

# Listar todos os pedidos, incluindo os seguintes filtros: período, seção dos produtos, id_pedido, status do pedido e cliente.
@app.get("/orders") # GET
def orders_get(order: Annotated[Order, Query()]):
    ...

# Criar um novo pedido contendo múltiplos produtos, validando estoque disponível.    
@app.post("/orders") # POST
def orders_post(order: Annotated[Order, Query()]):
    ...

# Obter informações de um pedido específico.    
@app.get("/orders/{id}") # GET
def orders_get():
    ...

# Atualizar informações de um pedido específico, incluindo status do pedido.
@app.put("/orders/{id}") # PUT
def orders_put():
    ...
    
# Excluir um pedido.
@app.delete("/orders/{id}") # DELETE
def orders_delete():
    ...