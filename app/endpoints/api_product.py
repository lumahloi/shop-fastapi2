from fastapi import Query, HTTPException, APIRouter, Depends
from sqlmodel import select
from typing import  Annotated, Union
from datetime import datetime
from ..models.model_product import Product, ProductCreate, ProductUpdate
from ..utils.custom_types import VALID_SIZE_TYPES, VALID_COLOR_TYPES, VALID_CATEGORY_TYPES, VALID_SECTION_TYPES, CategoryType
from ..utils.services import to_str_lower
from ..utils.session import SessionDep
from ..models.model_user import User
from ..utils.permissions import require_user_type

router = APIRouter()

@router.get("/products", response_model=list[Product]) 
def products_get(
    session: SessionDep,
    category: Union[CategoryType | None] = Query(None, alias="category"),
    price: Union[float | None] = Query(None, alias="price"),
    availability: Union[bool | None] = Query(None, alias="availability"),
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
    
    
    
@router.post("/products", response_model=Product) 
def products_post(session: SessionDep, data: ProductCreate, current_user: User = Depends(require_user_type(["administrador", "gerente", "estoquista"]))):
    data.prod_size = [s.lower() for s in data.prod_size]
    data.prod_color = [c.lower() for c in data.prod_color]
    data.prod_cat = to_str_lower(data.prod_cat)
    data.prod_section = to_str_lower(data.prod_section)
    
    if not all(size in VALID_SIZE_TYPES for size in data.prod_size):
        raise HTTPException(
            status_code=400,
            detail={
                "msg": f"Tipo(s) de tamanho inválido(s): {data.prod_size}",
                "tipos_validos": VALID_SIZE_TYPES
            }
        )

    if not all(color in VALID_COLOR_TYPES for color in data.prod_color):
        raise HTTPException(
            status_code=400,
            detail={
                "msg": f"Tipo(s) de cor inválida(s): {data.prod_color}",
                "tipos_validos": VALID_COLOR_TYPES
            }
        )

    if data.prod_cat not in VALID_CATEGORY_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "msg": f"Categoria inválida: '{data.prod_cat}'",
                "tipos_validos": VALID_CATEGORY_TYPES
            }
        )

    if data.prod_section not in VALID_SECTION_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "msg": f"Seção inválida: '{data.prod_section}'",
                "tipos_validos": VALID_SECTION_TYPES
            }
        )

    new_product = Product(
        **data.dict(),
        prod_stock = data.prod_initialstock,
        prod_createdat=datetime.utcnow(),
        prod_lastupdate=datetime.utcnow()
    )

    session.add(new_product)
    session.commit()
    session.refresh(new_product)

    return new_product
 
 

@router.get("/products/{id}", response_model=Product)
def products_get(id: int, session: SessionDep, current_user: User = Depends(require_user_type([]))):
    
    product = session.get(Product, id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este produto")
    
    return product



@router.put("/products/{id}", response_model=Product) 
def products_put(id: int, data: ProductUpdate, session: SessionDep, current_user: User = Depends(require_user_type(["administrador", "gerente", "estoquista"]))):
    product = session.get(Product, id)

    if not product:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este produto.")

    update_data = data.dict(exclude_unset=True)

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

    for key, value in update_data.items():
        setattr(product, key, value)

    session.add(product)
    session.commit()
    session.refresh(product)

    return product



@router.delete("/products/{id}")
def products_delete(id: int, session: SessionDep, current_user: User = Depends(require_user_type(["administrador", "gerente"]))):
    
    product = session.get(Product, id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este produto")
    
    session.delete(product)
    session.commit()
    
    return {"ok": True}
 