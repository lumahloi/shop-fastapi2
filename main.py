from pydantic import BaseModel, Field
from typing import Union, Annotated
from fastapi import FastAPI, Query

################################### baseModels

class User(BaseModel):
    usr_email: str = Query(max_length=20)
    usr_pass: str = Query(max_length=20)
    
class Client(BaseModel):
    cli_name: Union[str, None] = Query(max_length=20)
    cli_email: Union[str, None] = Query(max_length=20)
    cli_cpf: Union[str, None] = Query(max_length=11)
    
class Product(BaseModel):
    prod_cat: Union[str, None]
    prod_price: Union[float, None]
    prod_avail: Union[bool, None]
    prod_desc: str = Query(max_length=100)
    prod_price: float
    prod_barcode: str
    prod_section: str
    prod_stock: int = Field(0, gt=0)
    prod_val: str
    prod_imgs: str
    
class Order(BaseModel):
    order_period: Union[str, None]
    order_section: Union[str, None]
    order_id: Union[str, None]
    order_status: Union[str, None]
    order_cli: Union[str, None]
    order_prods: list


app = FastAPI()

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