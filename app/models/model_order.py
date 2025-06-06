from sqlmodel import SQLModel, Field, JSON
from sqlalchemy import Column, DateTime
from datetime import datetime
from typing import List, Optional
from ..utils.custom_types import SectionType, StatusType, PaymentType


class OrderBase(SQLModel):
    order_section: SectionType
    order_cli: int = Field(index=True)
    order_total: float
    order_typepay: PaymentType
    order_address: str = Field(min_length=8,max_length=100)
    order_prods: List[int] = Field(default_factory=list, sa_column=Column(JSON))
    
    
class OrderCreate(OrderBase):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "order_section": "blusas",
                    "order_cli": 1,
                    "order_total": 99.90,
                    "order_typepay": "crédito",
                    "order_address": "Rua das Palmeiras 15",
                    "order_prods": [1, 2]
                }
            ]
        }
    }
    pass


class OrderUpdate(SQLModel):
    order_status: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "order_status": "em andamento"
                }
            ]
        }
    }


class Order(OrderBase, table=True):
    order_id: Optional[int] = Field(primary_key=True, index=True)
    order_period: Optional[datetime] = Field(
        default_factory=datetime.utcnow(),
        sa_column=Column(DateTime, index=True, default=datetime.utcnow())
    )
    
    order_createdat: Optional[datetime] = Field(
        default_factory=datetime.utcnow(),
        sa_column=Column(DateTime, index=True, default=datetime.utcnow())
    )
    order_status: StatusType
    
    