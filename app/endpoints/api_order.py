from fastapi import Query, HTTPException, APIRouter, Depends
from sqlmodel import select
from typing import  Annotated, Union
from datetime import datetime, date
from ..models.model_client import Client
from ..models.model_product import Product
from ..models.model_order import Order, OrderCreate, OrderUpdate
from ..utils.custom_types import StatusType
from ..utils.session import SessionDep
from ..models.model_user import User
from ..utils.permissions import require_user_type
from ..utils.services import to_str_lower


router = APIRouter()

@router.get("/orders", response_model=list[Order])
def orders_get( 
    session: SessionDep,
    period: Union[date | None] = Query(None, alias="period"),
    section: Union[str | None] = Query(None, alias="section"),
    id: Union[int | None] = Query(None, alias="id"),
    status: Union[StatusType | None] = Query(None, alias="status"),
    client: Union[int | None] = Query(None, alias="client"),
    num_page: int = 1,
    limit: Annotated[int, Query(le=10)] = 10,
    current_user: User = Depends(require_user_type([]))
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
    
   
@router.post("/orders", response_model=Order)
def orders_post(session: SessionDep, data: OrderCreate, current_user: User = Depends(require_user_type(["administrador", "gerente", "vendedor", "atendente"]))):
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
 

@router.get("/orders/{id}", response_model=Order) 
def orders_get(id: int, session: SessionDep, current_user: User = Depends(require_user_type([]))):
    order = session.get(Order, id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este pedido")
    
    return order



@router.put("/orders/{id}")
def orders_put(id: int, session: SessionDep, data: OrderUpdate, current_user: User = Depends(require_user_type(["administrador", "gerente"]))):
    data.order_status = to_str_lower(data.order_status)
    
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
    
    
    
@router.delete("/orders/{id}") 
def orders_delete(id: int, session: SessionDep, current_user: User = Depends(require_user_type(["administrador", "gerente"]))):
    order = session.get(Order, id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar este pedido")
    
    session.delete(order)
    session.commit()
    
    return {"ok": True}