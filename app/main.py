from fastapi import FastAPI
from .endpoints import api_client, api_order, api_product, api_user

app = FastAPI()

app.include_router(api_client.router)
app.include_router(api_order.router)
app.include_router(api_product.router)
app.include_router(api_user.router)
