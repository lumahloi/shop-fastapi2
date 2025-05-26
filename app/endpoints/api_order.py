from fastapi import Query, HTTPException, APIRouter, Depends, Path
from sqlmodel import select
import sentry_sdk
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

@router.get(
    "/orders",
    response_model=list[Order],
    summary="Listar pedidos",
    description="Retorna uma lista paginada de pedidos cadastrados, com filtros opcionais por período, seção, status, cliente ou ID.",
    response_description="Lista de pedidos encontrados."
)
def orders_get( 
    session: SessionDep,
    period: Union[date | None] = Query(None, alias="period", example="2023-12-31"),
    section: Union[str | None] = Query(None, alias="section", example="Feminino"),
    id: Union[int | None] = Path(..., example=1, description="ID do pedido"),
    status: Union[StatusType | None] = Query(None, alias="status", example="em andamento"),
    client: Union[int | None] = Query(None, alias="client", example=1),
    num_page: int = 1,
    limit: Annotated[int, Query(le=10)] = 10,
    current_user: User = Depends(require_user_type([]))
):
    try: 
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
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao resgatar pedidos.")
    
    
   
@router.post(
    "/orders",
    response_model=Order,
    summary="Criar novo pedido",
    description="Cria um novo pedido para um cliente, com os produtos e informações fornecidas.",
    response_description="Pedido criado com sucesso."
)
def orders_post(
    session: SessionDep, 
    data: OrderCreate, 
    current_user: User = Depends(require_user_type(["administrador", "gerente", "vendedor", "atendente"]))
):
    try: 
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
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao criar pedido.")



@router.get(
    "/orders/{id}",
    response_model=Order,
    summary="Obter pedido por ID",
    description="Retorna os dados de um pedido específico a partir do seu ID.",
    response_description="Dados do pedido encontrado."
)
def orders_get(
    session: SessionDep, 
    current_user: User = Depends(require_user_type([])), 
    id: int = Path(..., example=1, description="ID do pedido")
):
    try: 
        order = session.get(Order, id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Não foi possível encontrar este pedido")
        
        return order
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao resgatar pedido.")



@router.put(
    "/orders/{id}",
    summary="Atualizar pedido",
    description="Atualiza o status de um pedido existente pelo ID.",
    response_description="Pedido atualizado com sucesso."
)
def orders_put(
    session: SessionDep, 
    data: OrderUpdate, 
    current_user: User = Depends(require_user_type(["administrador", "gerente"])), 
    id: int = Path(..., example=1, description="ID do pedido"),
):
    try: 
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
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao editar pedido.")
    
    
    
@router.delete(
    "/orders/{id}",
    summary="Deletar pedido",
    description="Remove um pedido do sistema pelo seu ID.",
    response_description="Confirmação de remoção do pedido."
)
def orders_delete(
    session: SessionDep, 
    current_user: User = Depends(require_user_type(["administrador", "gerente"])), 
    id: int = Path(..., example=1, description="ID do pedido"),
):
    try: 
        order = session.get(Order, id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Não foi possível encontrar este pedido")
        
        session.delete(order)
        session.commit()
        
        return {"ok": True}
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Erro ao deletar pedido.")
    
    
    