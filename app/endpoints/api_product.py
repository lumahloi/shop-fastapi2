from fastapi import Query, HTTPException, APIRouter, Depends, UploadFile, File, Form, Path
from sqlmodel import select
import sentry_sdk, os, json
from uuid import uuid4
from typing import  Annotated, Union
from datetime import datetime
from ..models.model_product import Product
from ..utils.custom_types import VALID_SIZE_TYPES, VALID_COLOR_TYPES, VALID_CATEGORY_TYPES, VALID_SECTION_TYPES, CategoryType
from ..utils.services import to_str_lower, handle_upload_images, handle_delete_images
from ..utils.session import SessionDep
from ..models.model_user import User
from ..utils.permissions import require_user_type

router = APIRouter()



@router.get("/products", 
    response_model=list[Product], 
    summary="Lista produtos com filtros opcionais", 
    response_description="Lista de produtos conforme filtros aplicados.",  
    description="Retorna uma lista paginada de produtos. Permite filtrar por categoria, preço e disponibilidade em estoque.",
    responses={
        200: {
            "description": "Lista de produtos encontrados.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "prod_id": 1,
                            "prod_cat": "feminino",
                            "prod_price": 99.9,
                            "prod_desc": "Blusa de algodão",
                            "prod_barcode": "1234567890123",
                            "prod_section": "blusas",
                            "prod_initialstock": 10,
                            "prod_dtval": "2024-12-31T00:00:00",
                            "prod_name": "Blusa Branca",
                            "prod_size": ["p", "m"],
                            "prod_color": ["branco"],
                            "prod_imgs": ["/static/product_images/1.png"],
                            "prod_createdat": "2024-06-01T12:00:00",
                            "prod_lastupdate": "2024-06-01T12:00:00",
                            "prod_stock": 5
                        }
                    ]
                }
            }
        },
        401: {
            "description": "Erro ao buscar produtos.",
            "content": {
                "application/json": {
                    "example": {"detail": "Erro ao buscar produtos."}
                }
            }
        }
    }
) 
def products_get(
    session: SessionDep,
    category: Union[CategoryType | None] = Query(None, alias="category", example="feminino"),
    price: Union[float | None] = Query(None, alias="price", example=99.9),
    availability: Union[bool | None] = Query(None, alias="availability", example=True),
    num_page: Union[int | None] = Query(1, alias="num_page"),
    limit: Annotated[int, Query(le=10)] = 10,
    current_user: User = Depends(require_user_type([]))
):
    offset = (num_page - 1) * limit
    
    query = select(Product)

    if category:
        query = query.where(Product.prod_cat == category.lower())
        
    if price:
        query = query.where(Product.prod_price == price)

    if availability == False:
        query = query.where(Product.prod_stock == 0)
        
    if availability == True:
        query = query.where(Product.prod_stock != 1)

    results = session.exec(query.offset(offset).limit(limit)).all()
    
    return results




@router.post("/products", 
    response_model=Product, 
    summary="Cria um novo produto", 
    response_description="Produto criado com sucesso.", 
    description="Cria um novo produto com os dados fornecidos e imagens opcionais. Apenas administradores, gerentes ou estoquistas podem realizar esta ação.",
    responses={
        200: {
            "description": "Produto criado com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "prod_id": 1,
                        "prod_cat": "feminino",
                        "prod_price": 99.9,
                        "prod_desc": "Blusa de algodão",
                        "prod_barcode": "1234567890123",
                        "prod_section": "blusas",
                        "prod_initialstock": 10,
                        "prod_dtval": "2024-12-31T00:00:00",
                        "prod_name": "Blusa Branca",
                        "prod_size": ["p", "m"],
                        "prod_color": ["branco"],
                        "prod_imgs": ["/static/product_images/1.png"],
                        "prod_createdat": "2024-06-01T12:00:00",
                        "prod_lastupdate": "2024-06-01T12:00:00",
                        "prod_stock": 10
                    }
                }
            }
        },
        400: {
            "description": "Erro de validação.",
            "content": {
                "application/json": {
                    "example": {
                        "msg": "Tipo(s) de tamanho inválido(s): ['xxl']",
                        "tipos_validos": ["p", "m", "g"]
                    }
                }
            }
        },
        401: {
            "description": "Erro ao criar produto.",
            "content": {
                "application/json": {
                    "example": {"detail": "Erro ao criar produto."}
                }
            }
        },
        500: {
            "description": "Erro interno ao criar produto.",
            "content": {
                "application/json": {
                    "example": {"detail": "Erro ao criar produto."}
                }
            }
        }
    }
)
def products_post(
    session: SessionDep,
    data: str = Form(...),
    files: list[UploadFile] = File(None),
    current_user: User = Depends(require_user_type(["administrador", "gerente", "estoquista"]))
):
    try:
        data = json.loads(data)

        data["prod_size"] = [s.lower() for s in data["prod_size"]]
        data["prod_color"] = [c.lower() for c in data["prod_color"]]
        data["prod_cat"] = to_str_lower(data["prod_cat"])
        data["prod_section"] = to_str_lower(data["prod_section"])

        if not all(size in VALID_SIZE_TYPES for size in data["prod_size"]):
            raise HTTPException(
                status_code=400,
                detail={
                    "msg": f"Tipo(s) de tamanho inválido(s): {data['prod_size']}",
                    "tipos_validos": VALID_SIZE_TYPES
                }
            )

        if not all(color in VALID_COLOR_TYPES for color in data["prod_color"]):
            raise HTTPException(
                status_code=400,
                detail={
                    "msg": f"Tipo(s) de cor inválida(s): {data['prod_color']}",
                    "tipos_validos": VALID_COLOR_TYPES
                }
            )

        if data["prod_cat"] not in VALID_CATEGORY_TYPES:
            raise HTTPException(
                status_code=400,
                detail={
                    "msg": f"Categoria inválida: '{data['prod_cat']}'",
                    "tipos_validos": VALID_CATEGORY_TYPES
                }
            )

        if data["prod_section"] not in VALID_SECTION_TYPES:
            raise HTTPException(
                status_code=400,
                detail={
                    "msg": f"Seção inválida: '{data['prod_section']}'",
                    "tipos_validos": VALID_SECTION_TYPES
                }
            )

        new_product = Product(
            **{k: v for k, v in data.items() if k != "prod_imgs"},
            prod_stock=data["prod_initialstock"],
            prod_createdat=datetime.utcnow(),
            prod_lastupdate=datetime.utcnow()
        )

        if files:
            handle_upload_images(new_product, files)

        session.add(new_product)
        session.commit()
        session.refresh(new_product)

        return new_product
    
    except HTTPException:
        raise
    
    except Exception as e:
        print("Erro ao criar produto:", e)
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Erro ao criar produto.")




@router.get("/products/{id}", 
    response_model=Product, 
    summary="Obtém detalhes de um produto", 
    response_description="Detalhes do produto solicitado.",  
    description="Retorna os detalhes de um produto específico pelo ID.",
    responses={
        200: {
            "description": "Detalhes do produto encontrado.",
            "content": {
                "application/json": {
                    "example": {
                        "prod_id": 1,
                        "prod_cat": "feminino",
                        "prod_price": 99.9,
                        "prod_desc": "Blusa de algodão",
                        "prod_barcode": "1234567890123",
                        "prod_section": "blusas",
                        "prod_initialstock": 10,
                        "prod_dtval": "2024-12-31T00:00:00",
                        "prod_name": "Blusa Branca",
                        "prod_size": ["p", "m"],
                        "prod_color": ["branco"],
                        "prod_imgs": ["/static/product_images/1.png"],
                        "prod_createdat": "2024-06-01T12:00:00",
                        "prod_lastupdate": "2024-06-01T12:00:00",
                        "prod_stock": 5
                    }
                }
            }
        },
        404: {
            "description": "Produto não encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Não foi possível encontrar este produto"}
                }
            }
        },
        401: {
            "description": "Erro ao resgatar produto.",
            "content": {
                "application/json": {
                    "example": {"detail": "Erro ao resgatar produto."}
                }
            }
        }
    }
)
def products_get(
    session: SessionDep, 
    current_user: User = Depends(require_user_type([])), 
    id: int = Path(..., example=1, description="ID do produto")
):
    try:
    
        product = session.get(Product, id)
        
        if not product:
            raise HTTPException(status_code=404, detail="Não foi possível encontrar este produto")
        
        return product
    
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao resgatar produto.")
    


@router.put("/products/{id}", 
    response_model=Product, 
    summary="Atualiza um produto existente", 
    response_description="Produto atualizado com sucesso.", 
    description="Atualiza os dados de um produto existente, incluindo imagens se fornecidas. Apenas administradores, gerentes ou estoquistas podem realizar esta ação.",
    responses={
        200: {
            "description": "Produto atualizado com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "prod_id": 1,
                        "prod_cat": "feminino",
                        "prod_price": 99.9,
                        "prod_desc": "Blusa de algodão",
                        "prod_barcode": "1234567890123",
                        "prod_section": "blusas",
                        "prod_initialstock": 10,
                        "prod_dtval": "2024-12-31T00:00:00",
                        "prod_name": "Blusa Branca",
                        "prod_size": ["p", "m"],
                        "prod_color": ["branco"],
                        "prod_imgs": ["/static/product_images/1.png"],
                        "prod_createdat": "2024-06-01T12:00:00",
                        "prod_lastupdate": "2024-06-01T12:00:00",
                        "prod_stock": 8
                    }
                }
            }
        },
        400: {
            "description": "Erro de validação.",
            "content": {
                "application/json": {
                    "example": {
                        "msg": "Tamanhos inválidos: ['xxl']",
                        "tipos_validos": ["p", "m", "g"]
                    }
                }
            }
        },
        404: {
            "description": "Produto não encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Não foi possível encontrar este produto."}
                }
            }
        },
        401: {
            "description": "Erro ao editar produto.",
            "content": {
                "application/json": {
                    "example": {"detail": "Erro ao editar produto."}
                }
            }
        }
    }
) 
def products_put(
    session: SessionDep,
    data: str = Form(...),
    files: list[UploadFile] = File(None),
    current_user: User = Depends(require_user_type(["administrador", "gerente", "estoquista"])),
    id: int = Path(..., example=1, description="ID do produto")
):
    try: 
        product = session.get(Product, id)

        if not product:
            raise HTTPException(status_code=404, detail="Não foi possível encontrar este produto.")

        update_data = json.loads(data)

        if "prod_size" in update_data:
            if not all(size in VALID_SIZE_TYPES for size in update_data["prod_size"]):
                raise HTTPException(status_code=400, detail={
                    "msg": f"Tamanhos inválidos: {update_data['prod_size']}",
                    "tipos_validos": VALID_SIZE_TYPES
                })

        if "prod_color" in update_data:
            if not all(color in VALID_COLOR_TYPES for color in update_data["prod_color"]):
                raise HTTPException(status_code=400, detail={
                    "msg": f"Cores inválidas: {update_data['prod_color']}",
                    "tipos_validos": VALID_COLOR_TYPES
                })

        if "prod_cat" in update_data:
            if update_data["prod_cat"] not in VALID_CATEGORY_TYPES:
                raise HTTPException(status_code=400, detail={
                    "msg": f"Categoria inválida: {update_data['prod_cat']}",
                    "tipos_validos": VALID_CATEGORY_TYPES
                })

        if "prod_section" in update_data:
            if update_data["prod_section"] not in VALID_SECTION_TYPES:
                raise HTTPException(status_code=400, detail={
                    "msg": f"Seção inválida: {update_data['prod_section']}",
                    "tipos_validos": VALID_SECTION_TYPES
                })

        if files:
            handle_delete_images(product)
            handle_upload_images(product, files)

        for key, value in update_data.items():
            setattr(product, key, value)

        session.add(product)
        session.commit()
        session.refresh(product)

        return product
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao editar produto.")



@router.delete("/products/{id}", 
    summary="Remove um produto", 
    response_description="Produto removido com sucesso.", 
    description="Remove um produto do sistema, incluindo suas imagens. Apenas administradores ou gerentes podem realizar esta ação.",
    responses={
        200: {
            "description": "Produto removido com sucesso.",
            "content": {
                "application/json": {
                    "example": {"ok": True}
                }
            }
        },
        404: {
            "description": "Produto não encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Não foi possível encontrar este produto"}
                }
            }
        },
        401: {
            "description": "Erro ao deletar produto.",
            "content": {
                "application/json": {
                    "example": {"detail": "Erro ao deletar produto."}
                }
            }
        }
    }
)
def products_delete(
    session: SessionDep,
    current_user: User = Depends(require_user_type(["administrador", "gerente"])),
    id: int = Path(..., example=1, description="ID do produto")
):
    try: 
        product = session.get(Product, id)
        
        if not product:
            raise HTTPException(status_code=404, detail="Não foi possível encontrar este produto")
        
        handle_delete_images(product)
        
        session.delete(product)
        session.commit()
        
        return {"ok": True}
    
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao deletar produto.")
    



@router.put("/products/{id}/update-images", 
    response_model=Product, 
    summary="Atualiza todas as imagens de um produto", 
    response_description="Produto com imagens substituídas.",  
    description="Remove todas as imagens atuais do produto e faz upload de novas imagens. Apenas administradores, gerentes ou estoquistas podem realizar esta ação.",
    responses={
        200: {
            "description": "Imagens do produto atualizadas com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "prod_id": 1,
                        "prod_cat": "feminino",
                        "prod_price": 99.9,
                        "prod_desc": "Blusa de algodão",
                        "prod_barcode": "1234567890123",
                        "prod_section": "blusas",
                        "prod_initialstock": 10,
                        "prod_dtval": "2024-12-31T00:00:00",
                        "prod_name": "Blusa Branca",
                        "prod_size": ["p", "m"],
                        "prod_color": ["branco"],
                        "prod_imgs": ["/static/product_images/2.png"],
                        "prod_createdat": "2024-06-01T12:00:00",
                        "prod_lastupdate": "2024-06-01T12:10:00",
                        "prod_stock": 8
                    }
                }
            }
        },
        404: {
            "description": "Produto não encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Produto não encontrado."}
                }
            }
        },
        500: {
            "description": "Erro ao atualizar imagens do produto.",
            "content": {
                "application/json": {
                    "example": {"detail": "Erro ao atualizar imagens do produto."}
                }
            }
        }
    }
)
def update_product_images(
    session: SessionDep,
    files: list[UploadFile] = File(...),
    current_user: User = Depends(require_user_type(["administrador", "gerente", "estoquista"])),
    id: int = Path(..., example=1, description="ID do produto"),
):
    try:
        product = session.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Produto não encontrado.")

        images_dir = os.path.join("static", "product_images")
        os.makedirs(images_dir, exist_ok=True)

        product.prod_imgs = []

        for file in files:
            ext = os.path.splitext(file.filename)[1]
            filename = f"{uuid4().hex}{ext}"
            file_path = os.path.join(images_dir, filename)

            with open(file_path, "wb") as image_file:
                image_file.write(file.file.read())

            product.prod_imgs.append(f"/static/product_images/{filename}")

        product.prod_lastupdate = datetime.utcnow()
        session.add(product)
        session.commit()
        session.refresh(product)

        return product
    except HTTPException as e:
        raise e
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Erro ao atualizar imagens do produto.")



@router.post("/products/{id}/upload-image", 
    response_model=Product, 
    summary="Faz upload de imagens para um produto", 
    response_description="Produto atualizado com as novas imagens.",  
    description="Adiciona uma ou mais imagens ao produto especificado pelo ID. Apenas administradores, gerentes ou estoquistas podem realizar esta ação.",
    responses={
        200: {
            "description": "Imagens adicionadas ao produto com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "prod_id": 1,
                        "prod_cat": "feminino",
                        "prod_price": 99.9,
                        "prod_desc": "Blusa de algodão",
                        "prod_barcode": "1234567890123",
                        "prod_section": "blusas",
                        "prod_initialstock": 10,
                        "prod_dtval": "2024-12-31T00:00:00",
                        "prod_name": "Blusa Branca",
                        "prod_size": ["p", "m"],
                        "prod_color": ["branco"],
                        "prod_imgs": ["/static/product_images/1.png", "/static/product_images/3.png"],
                        "prod_createdat": "2024-06-01T12:00:00",
                        "prod_lastupdate": "2024-06-01T12:15:00",
                        "prod_stock": 8
                    }
                }
            }
        },
        404: {
            "description": "Produto não encontrado.",
            "content": {
                "application/json": {
                    "example": {"detail": "Produto não encontrado."}
                }
            }
        },
        500: {
            "description": "Erro ao fazer upload das imagens.",
            "content": {
                "application/json": {
                    "example": {"detail": "Erro ao fazer upload das imagens."}
                }
            }
        }
    }
)
def upload_product_image(
    session: SessionDep,
    files: list[UploadFile] = File(
        ...,
        description="Arquivos de imagem do produto"
    ),
    current_user: User = Depends(require_user_type(["administrador", "gerente", "estoquista"])),
    id: int = Path(..., example=1, description="ID do produto"),
):
    try:
        product = session.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Produto não encontrado.")

        images_dir = os.path.join("static", "product_images")
        os.makedirs(images_dir, exist_ok=True)

        if not product.prod_imgs:
            product.prod_imgs = []

        for file in files:
            ext = os.path.splitext(file.filename)[1]
            filename = f"{uuid4().hex}{ext}"
            file_path = os.path.join(images_dir, filename)

            with open(file_path, "wb") as image_file:
                image_file.write(file.file.read())

            product.prod_imgs.append(f"/static/product_images/{filename}")

        product.prod_lastupdate = datetime.utcnow()
        session.add(product)
        session.commit()
        session.refresh(product)

        return product
    except HTTPException as e:
        raise e
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Erro ao fazer upload das imagens.")




@router.delete("/products/{id}/delete-image", 
    response_model=Product, 
    summary="Remove uma imagem específica de um produto", 
    response_description="Produto atualizado sem a imagem removida.",  
    description="Remove uma imagem específica do produto pelo nome do arquivo. Apenas administradores, gerentes ou estoquistas podem realizar esta ação.",
    responses={
        200: {
            "description": "Imagem removida do produto com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "prod_id": 1,
                        "prod_cat": "feminino",
                        "prod_price": 99.9,
                        "prod_desc": "Blusa de algodão",
                        "prod_barcode": "1234567890123",
                        "prod_section": "blusas",
                        "prod_initialstock": 10,
                        "prod_dtval": "2024-12-31T00:00:00",
                        "prod_name": "Blusa Branca",
                        "prod_size": ["p", "m"],
                        "prod_color": ["branco"],
                        "prod_imgs": ["/static/product_images/1.png"],
                        "prod_createdat": "2024-06-01T12:00:00",
                        "prod_lastupdate": "2024-06-01T12:20:00",
                        "prod_stock": 8
                    }
                }
            }
        },
        404: {
            "description": "Produto ou imagem não encontrada.",
            "content": {
                "application/json": {
                    "example": {"detail": "Imagem não encontrada para este produto."}
                }
            }
        },
        500: {
            "description": "Erro ao deletar imagem do produto.",
            "content": {
                "application/json": {
                    "example": {"detail": "Erro ao deletar imagem do produto."}
                }
            }
        }
    }
)
def delete_product_image(
    session: SessionDep,
    filename: str = Query(example="1.png"),
    current_user: User = Depends(require_user_type(["administrador", "gerente", "estoquista"])),
    id: int = Path(..., example=1, description="ID do produto"),
):
    try:
        product = session.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Produto não encontrado.")

        image_path = f"/static/product_images/{filename}"

        if image_path not in product.prod_imgs:
            raise HTTPException(status_code=404, detail="Imagem não encontrada para este produto.")

        imgs = product.prod_imgs.copy()
        imgs.remove(image_path)
        product.prod_imgs = imgs

        file_path = os.path.join("static", "product_images", filename)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass

        product.prod_lastupdate = datetime.utcnow()
        session.add(product)
        session.commit()
        session.refresh(product)

        return product
    except HTTPException as e:
        raise e
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Erro ao deletar imagem do produto.")


