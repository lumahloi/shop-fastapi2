import pytest, io, json
from sqlmodel import Session
from datetime import datetime
from app.models.model_product import Product

def test_create_product_success(
    client,
    auth_headers
):
    data = {
        "prod_name": "Camiseta Teste",
        "prod_price": 59.99,
        "prod_size": ["m"],
        "prod_color": ["azul"],
        "prod_cat": "feminino",
        "prod_section": "blusas",
        "prod_initialstock": 10,
        "prod_barcode": "1" * 13,
    }
    response = client.post(
        "/products",
        data={"data": json.dumps(data)},
        headers=auth_headers
    )
    assert response.status_code == 200, response.text
    assert response.json()["prod_name"] == "Camiseta Teste"
    
    
    

@pytest.mark.parametrize("invalid_size", [["XG"], ["M", "XXG"]])
def test_create_product_invalid_size(
    client,
    invalid_size,
    auth_headers
):
    data = {
        "prod_name": "Produto Inválido",
        "prod_price": 39.90,
        "prod_size": invalid_size,
        "prod_color": ["preto"],
        "prod_cat": "masculino",
        "prod_section": "blusas",
        "prod_initialstock": 5,
        "prod_barcode": "1" * 13,
    }
    response = client.post(
        "/products",
        data={"data": json.dumps(data)},
        headers=auth_headers
    )
    assert response.status_code == 400, response.text
    assert "tamanho" in response.json()["detail"]["msg"].lower() or "tamanhos" in response.json()["detail"]["msg"].lower()
    
    
    
    

@pytest.mark.parametrize("invalid_color", [["roxo-neon"], ["verde", "inexistente"]])
def test_create_product_invalid_color(
    client,
    invalid_color,
    auth_headers
):
    data = {
        "prod_name": "Produto Inválido",
        "prod_price": 79.90,
        "prod_size": ["m"],
        "prod_color": invalid_color,
        "prod_cat": "masculino",
        "prod_section": "blusas",
        "prod_initialstock": 3,
        "prod_barcode": "1" * 13,
    }
    response = client.post(
        "/products",
        data={"data": json.dumps(data)},
        headers=auth_headers
    )
    assert response.status_code == 400, response.text
    assert "cor" in response.json()["detail"]["msg"].lower() or "cores" in response.json()["detail"]["msg"].lower()
    
    
    
    

def test_get_product_by_id(
    client, 
    session: Session, 
    auth_headers
):
    product = Product(
        prod_name="Produto Existente",
        prod_price=49.90,
        prod_size=["m"],
        prod_color=["azul"],
        prod_cat="feminino",
        prod_section="calças",
        prod_initialstock=15,
        prod_createdat=datetime.utcnow().replace(tzinfo=None),
        prod_lastupdate=datetime.utcnow().replace(tzinfo=None),
        prod_barcode="1" * 13,
    )
    session.add(product)
    session.commit()
    session.refresh(product)

    response = client.get(f"/products/{product.prod_id}", headers=auth_headers)
    
    assert response.status_code == 200, response.text
    assert response.json()["prod_name"] == "Produto Existente"
    
    
    
    

def test_update_product(
    client,
    session: Session,
    auth_headers
):
    product = Product(
        prod_name="Produto Atualizar",
        prod_price=100,
        prod_size=["g"],
        prod_color=["branco"],
        prod_cat="masculino",
        prod_section="shorts",
        prod_initialstock=20,
        prod_createdat=datetime.utcnow().replace(tzinfo=None),
        prod_lastupdate=datetime.utcnow().replace(tzinfo=None),
        prod_barcode="1" * 13,
    )
    session.add(product)
    session.commit()
    session.refresh(product)

    data = {"prod_price": 120}
    response = client.put( 
        f"/products/{product.prod_id}",
        data={"data": json.dumps(data)},
        headers=auth_headers
    )
    assert response.status_code == 200, response.text
    assert response.json()["prod_price"] == 120
    
    
    
    

def test_delete_product(
    client,
    session: Session,
    auth_headers
):
    product = Product(
        prod_name="Produto Deletar",
        prod_price=80,
        prod_size=["p"],
        prod_color=["verde"],
        prod_cat="feminino",
        prod_section="vestidos",
        prod_initialstock=8,
        prod_createdat=datetime.utcnow().replace(tzinfo=None),
        prod_lastupdate=datetime.utcnow().replace(tzinfo=None),
        prod_barcode="1" * 13,
    )
    session.add(product)
    session.commit()
    session.refresh(product)

    response = client.delete(f"/products/{product.prod_id}", headers=auth_headers)
    assert response.status_code == 200, response.text
    assert response.json() == {"ok": True}
    
    
    
    

def test_upload_product_image_success(
    create_product,
    client,
    auth_headers
):
    product = create_product
    files = [
        ("files", ("img1.png", io.BytesIO(b"fake image data 1"), "image/png")),
        ("files", ("img2.jpg", io.BytesIO(b"fake image data 2"), "image/jpeg")),
    ]
    response = client.post(
        f"/products/{product.prod_id}/upload-image",
        files=files,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "prod_imgs" in data
    assert len(data["prod_imgs"]) == 2
    assert data["prod_imgs"][0].endswith(".png") or data["prod_imgs"][0].endswith(".jpg")
    
    
    
    

def test_upload_product_image_not_found(
    client,
    auth_headers
):
    files = [
        ("files", ("img1.png", io.BytesIO(b"fake image data 1"), "image/png")),
    ]
    response = client.post(
        "/products/999999/upload-image",
        files=files,
        headers=auth_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não encontrado."
    
    
    
    

def test_update_product_images_success(
    create_product,
    client,
    auth_headers
):
    product = create_product
    files = [
        ("files", ("img1.png", io.BytesIO(b"fake image data 1"), "image/png")),
        ("files", ("img2.jpg", io.BytesIO(b"fake image data 2"), "image/jpeg")),
    ]
    response = client.put(
        f"/products/{product.prod_id}/update-images",
        files=files,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "prod_imgs" in data
    assert len(data["prod_imgs"]) == 2
    assert data["prod_imgs"][0].endswith(".png") or data["prod_imgs"][0].endswith(".jpg")
    
    
    
    

def test_update_product_images_not_found(
    client,
    auth_headers
):
    files = [
        ("files", ("img1.png", io.BytesIO(b"fake image data 1"), "image/png")),
    ]
    response = client.put(
        "/products/999999/update-images",
        files=files,
        headers=auth_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não encontrado."
    
    
    
    

def test_delete_product_image_success(
    create_product,
    client,
    auth_headers
):
    product = create_product
    files = [
        ("files", ("img1.png", io.BytesIO(b"fake image data 1"), "image/png")),
    ]
    upload_resp = client.post(
        f"/products/{product.prod_id}/upload-image",
        files=files,
        headers=auth_headers
    )
    assert upload_resp.status_code == 200
    img_path = upload_resp.json()["prod_imgs"][0]
    filename = img_path.split("/")[-1]

    delete_resp = client.delete(
        f"/products/{product.prod_id}/delete-image?filename={filename}",
        headers=auth_headers
    )
    assert delete_resp.status_code == 200
    data = delete_resp.json()
    assert filename not in [img.split("/")[-1] for img in data["prod_imgs"]]
    
    
    

def test_delete_product_image_not_found(
    client,
    create_product,
    auth_headers
):
    product = create_product
    resp = client.delete(
        f"/products/{product.prod_id}/delete-image?filename=nao_existe.png",
        headers=auth_headers
    )
    assert resp.status_code == 404
    assert "Imagem não encontrada" in resp.json()["detail"]
    
    
    

def test_delete_product_image_product_not_found(
    client,
    auth_headers
):
    resp = client.delete(
        "/products/999999/delete-image?filename=img1.png",
        headers=auth_headers
    )
    assert resp.status_code == 404
    assert "Produto não encontrado" in resp.json()["detail"]
    
    
    