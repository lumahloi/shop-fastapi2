from fastapi import FastAPI
import sentry_sdk
from .endpoints import api_client, api_order, api_product, api_user

sentry_sdk.init(
    dsn="https://1bb6b62726383444e29c95c0143c4206@o4509390158495744.ingest.us.sentry.io/4509390159806465",
    send_default_pii=True,
#     traces_sample_rate=1.0,  # coleta de performance
#     environment="production",  # ou "development"
)

app = FastAPI()

@app.get(
    "/sentry-debug",
    responses={
        200: {
            "description": "Endpoint para testar integração com Sentry.",
            "content": {
                "application/json": {
                    "example": {"message": "Sentry debug endpoint"}
                }
            }
        },
        404: {
            "description": "Recurso não encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Not Found"}
                }
            }
        }
    }
)
async def trigger_error():
    division_by_zero = 1 / 0

app.include_router(api_client.router)
app.include_router(api_order.router)
app.include_router(api_product.router)
app.include_router(api_user.router)
