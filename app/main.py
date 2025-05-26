from fastapi import FastAPI
from .endpoints import api_client, api_order, api_product, api_user
import sentry_sdk

# sentry_sdk.init(
#     dsn="https://<sua-chave>@o123456.ingest.sentry.io/1234567",
#     traces_sample_rate=1.0,  # coleta de performance (ajuste se necessário)
#     environment="production",  # ou "development"
# )

sentry_sdk.init(
    dsn="https://1bb6b62726383444e29c95c0143c4206@o4509390158495744.ingest.us.sentry.io/4509390159806465",
    send_default_pii=True,
)

app = FastAPI()

@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0

app.include_router(api_client.router)
app.include_router(api_order.router)
app.include_router(api_product.router)
app.include_router(api_user.router)
