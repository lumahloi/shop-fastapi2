from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

################################### AUTH

@app.post("/auth/login") # POST
def auth_login():
    ...

@app.post("/auth/register") # POST
def auth_register():
    ...
    
@app.post("/auth/refresh-token") # POST
def auth_refresh_token():
    ...
    
################################### CLIENTS
    
@app.get("/clients") # GET
def clients_get():
    ...
    
@app.post("/clients") # POST
def clients_post():
    ...
    
@app.get("/clients/{id}") # GET
def clients_get():
    ...

@app.put("/clients/{id}") # PUT
def clients_put():
    ...
    
@app.delete("/clients/{id}") # DELETE
def clients_delete():
    ...
    
################################### PRODUCTS

@app.get("/products") # GET
def products_get():
    ...
    
@app.post("/products") # POST
def products_post():
    ...
    
@app.get("/products/{id}") # GET
def products_get():
    ...

@app.put("/products/{id}") # PUT
def products_put():
    ...
    
@app.delete("/products/{id}") # DELETE
def products_delete():
    ...
    
################################### PEDIDOS

@app.get("/orders") # GET
def orders_get():
    ...
    
@app.post("/orders") # POST
def orders_post():
    ...
    
@app.get("/orders/{id}") # GET
def orders_get():
    ...

@app.put("/orders/{id}") # PUT
def orders_put():
    ...
    
@app.delete("/orders/{id}") # DELETE
def orders_delete():
    ...