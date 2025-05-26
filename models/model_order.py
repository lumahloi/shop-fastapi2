from sqlmodel import SQLModel, Field, JSON
from sqlalchemy import Column
from datetime import datetime
from typing import List, Union

from ..utils.custom_types import SectionType, StatusType, PaymentType

class OrderBase(SQLModel):
    order_section: SectionType
    order_cli: int = Field(index=True)
    order_total: float
    order_typepay: PaymentType
    order_address: str = Field(min_length=8,max_length=100)
    order_prods: List[int] = Field(default_factory=list, sa_column=Column(JSON))
    
class OrderCreate(OrderBase):
    pass

class OrderUpdate(SQLModel):
    order_status: StatusType

class Order(OrderBase, table=True):
    order_id: int = Field(primary_key=True, index=True)
    order_period: Union[datetime | datetime.utcnow] = Field(index=True)
    order_status: StatusType
    order_createdat: Union[datetime | datetime.utcnow]