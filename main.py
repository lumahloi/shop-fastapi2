from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

################################### AUTH

@app.get("/auth/login") # POST
def auth_login():
    ...

@app.get("/auth/register") # POST
def auth_register():
    ...
    
@app.get("/auth/refresh-token") # POST
def auth_refresh_token():
    ...
    
################################### CLIENTS
    
@app.get("/clients") # GET
def clients_get():
    ...
    
@app.get("/clients") # POST
def clients_post():
    ...
    
@app.get("/clients/{id}") # GET
def clients_get():
    ...

@app.get("/clients/{id}") # PUT
def clients_put():
    ...
    
@app.get("/clients/{id}") # DELETE
def clients_delete():
    ...
    
################################### PRODUCTS

@app.get("/products") # GET
def products_get():
    ...
    
@app.get("/products") # POST
def products_post():
    ...
    
@app.get("/products/{id}") # GET
def products_get():
    ...

@app.get("/products/{id}") # PUT
def products_put():
    ...
    
@app.get("/products/{id}") # DELETE
def products_delete():
    ...
    
################################### PEDIDOS

@app.get("/orders") # GET
def orders_get():
    ...
    
@app.get("/orders") # POST
def orders_post():
    ...
    
@app.get("/orders/{id}") # GET
def orders_get():
    ...

@app.get("/orders/{id}") # PUT
def orders_put():
    ...
    
@app.get("/orders/{id}") # DELETE
def orders_delete():
    ...