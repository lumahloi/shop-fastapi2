from sqlmodel import SQLModel, Field
from datetime import datetime
from pydantic import constr


class UserBase(SQLModel):
    usr_name: str = Field(min_length=3, max_length=20, index=True)
    usr_email: str = Field(min_length=10,max_length=25,index=True, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    usr_pass: str = Field(min_length=8,max_length=20)
    usr_type: str = Field(min_length=5,default='Funcionário', max_length=20)
    
class UserCreate(UserBase):
    pass

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

class Client(ClientBase, table=True):
    cli_id: int = Field(default= None, primary_key=True)
    cli_createdat: datetime = Field(default_factory=datetime.utcnow)
    cli_active: bool = True

######################################################################################
    
class ProductBase(SQLModel):
    prod_name: str = Field(min_length=3,max_length=50,index=True)
    prod_desc: str = Field(max_length=100)
    prod_price: float = Field(index=True)
    prod_stock: int = Field(default=0, gt=0)
    # prod_size: list
    # prod_color: list
    prod_cat: str = Field(min_length=7,index=True)
    # prod_imgs: list
    prod_barcode: str = Field(min_length=43,max_length=43)
    prod_section: str = Field(min_length=7,index=True)
    prod_dtval: str = datetime
    
class ProductCreate(ProductBase):
    pass

class Product(ProductBase, table=True):
    prod_id: int = Field(default= None, primary_key=True)
    prod_active: bool = True
    prod_createdat: datetime = Field(default_factory=datetime.utcnow)
    prod_lastupdate: datetime = Field(default_factory=datetime.utcnow)

######################################################################################
    
class OrderBase(SQLModel):
    order_cli: int = Field(index=True)
    order_total: float
    order_typepay: str = Field(min_length=3,max_length=20),
    order_address: str = Field(min_length=8,max_length=100)
    order_section: str = Field(min_length=7,max_length=15,index=True)
    # order_prods: list
    
class OrderCreate(OrderBase):
    pass

class Order(OrderBase, table=True):
    order_id: int = Field(primary_key=True, index=True)
    order_period: str = Field(index=True)
    order_status: str = Field(default="Em andamento",min_length=3,max_length=20)
    order_createdat: datetime = Field(default_factory=datetime.utcnow)