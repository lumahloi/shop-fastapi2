from sqlmodel import SQLModel, Field, JSON
from sqlalchemy import Column
from datetime import datetime
from typing import List
from .custom_types import UserType, SizeType, ColorType, CategoryType, SectionType, StatusType, PaymentType



class UserBase(SQLModel):
    usr_name: str = Field(min_length=3, max_length=20, index=True)
    usr_email: str = Field(min_length=10,max_length=25,index=True, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    usr_pass: str = Field(min_length=8,max_length=20)
    usr_type: UserType
    
class UserCreate(UserBase):
    pass

class UserUpdate(SQLModel):
    usr_type: UserType

class User(UserBase, table=True):
    usr_id: int = Field(default= None, primary_key=True)
    usr_active: bool = True
    usr_createdat: datetime = Field(default_factory=datetime.utcnow)
    usr_lastupdate: datetime = Field(default_factory=datetime.utcnow)
    
    
######################################################################################
    
class ClientBase(SQLModel):
    cli_name: str = Field(min_length=3,max_length=20,index=True)
    cli_email: str = Field(min_length=10,max_length=25,index=True, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    cli_cpf: str = Field(min_length=11,max_length=14,index=True)
    cli_phone: str = Field(min_length=11,max_length=15)
    cli_address: str = Field(min_length=8,max_length=100)
    
class ClientCreate(ClientBase):
    pass

class ClientUpdate(SQLModel):
    cli_name: str | None = None, Field(min_length=3,max_length=20)
    cli_email: str | None = None, Field(min_length=10,max_length=25,index=True, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    cli_address: str | None = None, Field(min_length=8,max_length=100)
    cli_phone: str | None = None, Field(min_length=11,max_length=15)

class Client(ClientBase, table=True):
    cli_id: int = Field(default= None, primary_key=True)
    cli_createdat: datetime = Field(default_factory=datetime.utcnow)
    cli_active: bool = True

######################################################################################


class ProductBase(SQLModel):
    prod_size: List[SizeType] = Field(default_factory=list, sa_column=Column(JSON))
    prod_color: List[ColorType] = Field(default_factory=list, sa_column=Column(JSON))
    prod_imgs: List[str] | None = Field(default_factory=list, sa_column=Column(JSON))
    prod_name: str = Field(min_length=3,max_length=50,index=True)
    prod_desc: str | None = Field(max_length=100)
    prod_price: float = Field(index=True)
    prod_stock: int = Field(default=0, gt=0)
    prod_cat: CategoryType
    prod_barcode: str = Field(min_length=43,max_length=43)
    prod_section: SectionType
    prod_dtval: datetime | None
    
class ProductCreate(ProductBase):
    pass

class ProductUpdate(SQLModel):
    prod_name: str | None = Field(default=None, min_length=3, max_length=50)
    prod_desc: str | None = Field(default=None, max_length=100)
    prod_price: float | None = Field(default=None)
    prod_stock: int | None = Field(default=None, gt=0)
    prod_size: List[SizeType] | None = Field(default=None, sa_column=Column(JSON))
    prod_color: List[ColorType] | None = Field(default=None, sa_column=Column(JSON))
    prod_imgs: List[str] | None = Field(default=None, sa_column=Column(JSON))
    prod_cat: CategoryType | None = None
    prod_barcode: str | None = Field(default=None, min_length=43, max_length=43)
    prod_section: str | None = Field(default=None, min_length=7)
    prod_dtval: datetime | None = None


class Product(ProductBase, table=True):
    prod_id: int = Field(default= None, primary_key=True)
    prod_active: bool = True
    prod_createdat: datetime = Field(default_factory=datetime.utcnow)
    prod_lastupdate: datetime = Field(default_factory=datetime.utcnow)

######################################################################################
    
class OrderBase(SQLModel):
    order_cli: int = Field(index=True)
    order_total: float
    order_typepay: PaymentType
    order_address: str = Field(min_length=8,max_length=100)
    order_section: SectionType
    order_prods: List[int] = Field(default_factory=list, sa_column=Column(JSON))
    
class OrderCreate(OrderBase):
    pass

class OrderUpdate(SQLModel):
    order_status: StatusType

class Order(OrderBase, table=True):
    order_id: int = Field(primary_key=True, index=True)
    order_period: str = Field(index=True)
    order_status: StatusType
    order_createdat: datetime = Field(default_factory=datetime.utcnow)