from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime
from app.models.model_product import Product
from app.models.model_order import Order
from app.utils.custom_types import StatusType, SectionType, PaymentType

def test_create_order(
    client: TestClient,
    client_obj,
    products_obj,
    auth_headers
):
    order_data = {
        "order_section": "blusas",
        "order_cli": client_obj.cli_id,
        "order_total": 31.49,
        "order_typepay": "crédito",
        "order_address": "Test Address 123",
        "order_prods": [p.prod_id for p in products_obj]
    }
    response = client.post("/orders", json=order_data, headers=auth_headers)
    data = response.json()
    assert response.status_code == 200
    assert data["order_cli"] == client_obj.cli_id
    assert len(data["order_prods"]) == 2
    assert data["order_status"] == "em andamento"
    
    
    
    

def test_create_order_with_invalid_client(
    client: TestClient,
    products_obj,
    auth_headers
):
    order_data = {
        "order_section": "blusas",
        "order_cli": 999,
        "order_total": 31.49,
        "order_typepay": "crédito",
        "order_address": "Test Address 123",
        "order_prods": [p.prod_id for p in products_obj]
    }
    response = client.post("/orders", json=order_data, headers=auth_headers)
    assert response.status_code == 404
    assert "Cliente não reconhecido" in response.json()["detail"]
    
    
    
    

def test_create_order_with_out_of_stock_product(
    client: TestClient,
    client_obj,
    session: Session,
    auth_headers
):
    out_of_stock_product = Product(
        prod_name="Out of Stock Product",
        prod_desc="Description",
        prod_price=15.99,
        prod_initialstock=0,
        prod_section=SectionType.blusas,
        prod_size=["m"],
        prod_color=["red"],
        prod_cat="masculino",
        prod_barcode="3"*43,
    )
    session.add(out_of_stock_product)
    session.commit()
    session.refresh(out_of_stock_product)
    order_data = {
        "order_section": "blusas",
        "order_cli": client_obj.cli_id,
        "order_total": 15.99,
        "order_typepay": "crédito",
        "order_address": "Test Address 123",
        "order_prods": [out_of_stock_product.prod_id]
    }
    response = client.post("/orders", json=order_data, headers=auth_headers)
    assert response.status_code == 400
    assert "está sem estoque" in response.json()["detail"]
    
    
    

def test_get_order(
    client: TestClient,
    order_obj,
    auth_headers
):
    response = client.get(f"/orders/{order_obj.order_id}", headers=auth_headers)
    data = response.json()
    assert response.status_code == 200
    assert data["order_id"] == order_obj.order_id
    assert data["order_cli"] == order_obj.order_cli
    
    
    

def test_get_nonexistent_order(
    client: TestClient,
    auth_headers
):
    response = client.get("/orders/999", headers=auth_headers)
    assert response.status_code == 404
    assert "Não foi possível encontrar este pedido" in response.json()["detail"]




def test_list_orders(
    client: TestClient,
    order_obj,
    auth_headers
):
    response = client.get("/orders", headers=auth_headers)
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["order_id"] == order_obj.order_id




def test_list_orders_with_filters(
    client: TestClient,
    client_obj,
    auth_headers
):
    response = client.get(f"/orders?client={client_obj.cli_id}", headers=auth_headers)
    data = response.json()
    assert len(data) == 1

    response = client.get(f"/orders?section=Blusas", headers=auth_headers)
    data = response.json()
    assert len(data) == 1

    response = client.get(f"/orders?status=Em Andamento", headers=auth_headers)
    data = response.json()
    assert len(data) == 1

    today = datetime.utcnow().date().isoformat()
    response = client.get(f"/orders?period={today}", headers=auth_headers)
    data = response.json()
    assert isinstance(data, list)

    response = client.get("/orders?status=Cancelado", headers=auth_headers)
    data = response.json()
    assert len(data) == 0




def test_update_order_status(
    client: TestClient,
    order_obj,
    auth_headers
):
    update_data = {"order_status": "Pagamento Confirmado"}
    response = client.put(f"/orders/{order_obj.order_id}", json=update_data, headers=auth_headers)
    data = response.json()
    assert response.status_code == 200
    assert data["order_status"] == "pagamento confirmado"
    
    
    

def test_update_nonexistent_order(
    client: TestClient,
    auth_headers
):
    update_data = {"order_status": "Pagamento Confirmado"}
    response = client.put("/orders/999", json=update_data, headers=auth_headers)
    assert response.status_code == 404
    assert "Não foi possível encontrar este pedido" in response.json()["detail"]



def test_delete_order(
    client: TestClient,
    order_obj,
    auth_headers
):
    response = client.delete(f"/orders/{order_obj.order_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["ok"] == True

    response = client.get(f"/orders/{order_obj.order_id}", headers=auth_headers)
    assert response.status_code == 404
    
    
    

def test_delete_nonexistent_order(
    client: TestClient,
    auth_headers
):
    response = client.delete("/orders/999", headers=auth_headers)
    assert response.status_code == 404
    assert "Não foi possível encontrar este pedido" in response.json()["detail"]




def test_pagination_in_orders_list(
    client: TestClient,  
    client_obj, 
    products_obj, 
    session: Session, auth_headers
):
    orders = []
    for i in range(15):
        order = Order(
            order_section=SectionType.blusas,
            order_cli=client_obj.cli_id,
            order_total=10.99 * (i+1),
            order_typepay=PaymentType.credito,
            order_address=f"Test Address {i}",
            order_prods=[products_obj[0].prod_id],
            order_status=StatusType.andamento,
            order_createdat=datetime.utcnow().replace(tzinfo=None),
            order_period=datetime.utcnow().replace(tzinfo=None)
        )
        session.add(order)
        orders.append(order)
    session.commit()

    response = client.get("/orders", headers=auth_headers)
    data = response.json()
    assert len(data) == 10

    response = client.get("/orders?num_page=2", headers=auth_headers)
    data = response.json()
    assert len(data) == 5

    response = client.get("/orders?limit=5", headers=auth_headers)
    data = response.json()
    assert len(data) == 5
    
    
    
    