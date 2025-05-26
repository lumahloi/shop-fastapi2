from fastapi import Query, HTTPException, APIRouter
from sqlmodel import select
from typing import  Annotated, Union
from datetime import datetime, date

from ..models.model_client import Client
from ..models.model_product import Product
from ..models.model_order import Order, OrderCreate, OrderUpdate

from ..utils.custom_types import StatusType

from utils.session import SessionDep

router = APIRouter()

# Listar todos os pedidos, incluindo os seguintes filtros: período, seção dos produtos, id_pedido, status do pedido e cliente.
@router.get("/orders", response_model=list[Order]) # GET
def orders_get( 
    session: SessionDep,
    period: Union[date | None] = Query(None, alias="period"),
    section: Union[str | None] = Query(None, alias="section"),
    id: Union[int | None] = Query(None, alias="id"),
    status: Union[StatusType | None] = Query(None, alias="status"),
    client: Union[int | None] = Query(None, alias="client"),
    num_page: int = 1,
    limit: Annotated[int, Query(le=10)] = 10
):
    offset = (num_page - 1) * limit
    
    query = select(Order)

    if period:
        query = query.where(Order.order_period == period)
        
    if id:
        query = query.where(Order.order_id == id)
        
    if status:
        query = query.where(Order.order_status == status.lower())
        
    if section:
        query = query.where(Order.order_section == section.lower())
        
    if client:
        query = query.where(Order.order_cli == client)

    results = session.exec(query.offset(offset).limit(limit)).all()
    
    return results
    

# Criar um novo pedido contendo múltiplos produtos, validando estoque disponível.    
@router.post("/orders", response_model=Order)
def orders_post(session: SessionDep, data: OrderCreate):
    client = session.exec(select(Client).where(Client.cli_id == data.order_cli)).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não reconhecido.")

    products = session.exec(select(Product).where(Product.prod_id.in_(data.order_prods))).all()
    
    if len(products) != len(data.order_prods):
        raise HTTPException(status_code=404, detail="Um ou mais produtos não foram encontrados.")
    
    for prod in products:
        if prod.prod_stock < 1:
            raise HTTPException(status_code=400, detail=f"Produto '{prod.prod_name}' está sem estoque.")
    
    for prod in products:
        prod.prod_stock -= 1
        session.add(prod)

    new_order = Order(
        **data.dict(),
        order_period=datetime.utcnow(),
        order_status=StatusType.andamento,
        order_createdat=datetime.utcnow(),
    )

    session.add(new_order)
    session.commit()
    session.refresh(new_order)

    return new_order
 
    
    

# Obter informações de um pedido específico.    
@router.get("/orders/{id}", response_model=Order) # GET
def orders_get(id: int, session: SessionDep):
    order = session.get(Order, id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este pedido")
    
    return order

# Atualizar informações de um pedido específico, incluindo status do pedido.
@router.put("/orders/{id}") # PUT
def orders_put(id: int, session: SessionDep, data: OrderUpdate):
    order = session.get(Order, id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este pedido")
    
    order_data = data.dict(exclude_unset=True)
    
    for key, value in order_data.items():
        setattr(order, key, value)
            
    session.add(order)
    session.commit()
    session.refresh(order)

    return order   
    
    
    
# Excluir um pedido.
@router.delete("/orders/{id}") # DELETE
def orders_delete(id: int, session: SessionDep):
    order = session.get(Order, id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este pedido")
    
    session.delete(order)
    session.commit()
    
    return {"ok": True}