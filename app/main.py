from fastapi import FastAPI
import sentry_sdk
from app.endpoints import api_client, api_order, api_product, api_user
from app.models.model_user import User
from app.models.model_client import Client
from app.models.model_product import Product
from app.models.model_order import Order
from app.utils.database import get_db
from contextlib import asynccontextmanager
from app.utils.database import create_tables

sentry_sdk.init(
    dsn="https://1bb6b62726383444e29c95c0143c4206@o4509390158495744.ingest.us.sentry.io/4509390159806465",
    send_default_pii=True,
#     traces_sample_rate=1.0,  # coleta de performance
#     environment="production",  # ou "development"
)

create_tables()

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_gen = get_db()
    db = next(db_gen)
    try:
        if not db.query(User).first():
            admin = User(
                usr_name="administrador",
                usr_email="admin@example.com",
                user_type="administrador"
            )
            db.add(admin)
            db.flush()

            client1 = Client(
                cli_address="Rua das Flores, 45",
                cli_cpf="12345678901",
                cli_email="joao@email.com",
                cli_name="João da Silva",
                cli_phone="11999999999"
            )
            db.add(client1)
            db.flush()

            product1 = Product(
                prod_cat="feminino",
                prod_price=99.9,
                prod_desc="Blusa de algodão",
                prod_barcode="1234567890123",
                prod_section="blusas",
                prod_initialstock=10,
                prod_name="Blusa Branca",
                prod_size=["p", "m"],
                prod_color=["branco"],
                prod_imgs=["/static/product_images/1.png"]
            )
            db.add(product1)
            db.flush()  

            product_id = product1.id
            if not product_id:
                raise Exception("ID do produto não gerado corretamente.")

            order1 = Order(
                order_section="blusas",
                order_cli=client1.id,
                order_total=99.9,
                order_typepay="crédito",
                order_address="Rua das Flores, 45",
                order_prods=[product_id], 
                order_status="em andamento"
            )
            db.add(order1)

            db.commit()
            print("Dados iniciais criados com sucesso!")
    except Exception as e:
        db.rollback()
        print(f"Erro ao criar dados iniciais: {str(e)}")
        raise
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass
    yield


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
