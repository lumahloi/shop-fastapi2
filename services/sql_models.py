from sqlmodel import SQLModel, Field
from datetime import datetime


class UserBase(SQLModel):
    usr_name: str = Field(max_length=40)
    usr_email: str = Field(max_length=20)
    usr_pass: str = Field(max_length=20)
    usr_type: str = Field(default='Funcionário', max_length=20)
    
class UserCreate(UserBase):
    pass

class User(UserBase, table=True):
    usr_id: int = Field(default= None, primary_key=True)
    usr_active: bool = True
    usr_createdat: datetime = Field(default_factory=datetime.utcnow)
    usr_lastupdate: datetime = Field(default_factory=datetime.utcnow)
    
    
######################################################################################
    
class ClientBase(SQLModel):
    cli_name: str = Field(max_length=20), Field(index=True)
    cli_email: str = Field(max_length=20), Field(index=True)
    cli_cpf: str = Field(max_length=11), Field(index=True)
    cli_phone: str = Field(max_length=11)
    cli_address: str = Field(max_length=100)
    
class ClientCreate(ClientBase):
    pass

class Client(ClientBase, table=True):
    cli_id: int = Field(default= None, primary_key=True)
    cli_createdat: datetime = Field(default_factory=datetime.utcnow)
    cli_active: bool = True

######################################################################################
    
class ProductBase(SQLModel):
    prod_id: int = Field(default= None, primary_key=True)
    prod_name: str = Field(max_length=100), Field(index=True)
    prod_desc: str = Field(max_length=100)
    prod_price: float = Field(index=True)
    prod_stock: int = Field(0, gt=0)
    # prod_size: list
    # prod_color: list
    prod_cat: str = Field(index=True)
    # prod_imgs: list
    prod_active: bool = Field(index=True)
    prod_barcode: str 
    prod_section: str 
    prod_dtval: str 
    prod_createdat: str
    prod_lastupdate: str
    
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
    order_typepay: str
    order_address: str = Field(max_length=100)
    order_section: str = Field(index=True)
    # order_prods: list
    
class OrderCreate(OrderBase):
    pass

class Order(OrderBase, table=True):
    order_id: int = Field(primary_key=True, index=True)
    order_period: str = Field(index=True)
    order_status: str = 'Em andamento'
    order_createdat: datetime = Field(default_factory=datetime.utcnow)