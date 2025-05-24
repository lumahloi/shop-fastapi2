from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

################################### AUTH

# Autenticação de usuário.
@app.post("/auth/login") # POST
def auth_login(usr_email: str, usr_pass: str):
    ...

# Registro de novo usuário.
@app.post("/auth/register") # POST
def auth_register(usr_email: str, usr_pass: str):
    ...

#  Refresh de token JWT.    
@app.post("/auth/refresh-token") # POST
def auth_refresh_token():
    ...
    
################################### CLIENTS

# Listar todos os clientes, com suporte a paginação e filtro por nome e email.    
@app.get("/clients") # GET
def clients_get(num_page: Union[int, None], cli_name: Union[str, None], cli_email: Union[str, None]):
    ...

# Criar um novo cliente, validando email e CPF únicos.    
@app.post("/clients") # POST
def clients_post(cli_email: str, cli_cpf: str):
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
def products_get(num_page: Union[int, None], prod_cat: Union[str, None], prod_price: Union[float, None], prod_avail: Union[int, None]):
    ...
    
# Criar um novo produto, contendo os seguintes atributos: descrição, valor de venda, código de barras, seção, estoque inicial, e data de validade (quando aplicável) e imagens.    
@app.post("/products") # POST
def products_post(prod_desc: str, prod_price: float, prod_barcode: str, prod_section: str, prod_stock: int, prod_val: str, prod_imgs: str):
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
def orders_get(order_period: str, order_section: str, order_id: str, order_status: str, order_cli: str):
    ...

# Criar um novo pedido contendo múltiplos produtos, validando estoque disponível.    
@app.post("/orders") # POST
def orders_post(order_prods: list):
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