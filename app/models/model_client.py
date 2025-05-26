from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Union

class ClientBase(SQLModel):
    cli_name: str = Field(min_length=10,max_length=30,index=True)
    cli_email: str = Field(min_length=10,max_length=25,index=True, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    cli_cpf: str = Field(min_length=11,max_length=14,index=True)
    cli_phone: str = Field(min_length=11,max_length=15)
    cli_address: Union[str | None] = Field(min_length=6,max_length=100)
    
class ClientCreate(ClientBase):
    pass

class ClientUpdate(SQLModel):
    cli_name: Union[str | None] = Field(default=None,min_length=10,max_length=20)
    cli_email: Union[str | None] = Field(default=None,min_length=10,max_length=25,index=True, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    cli_address: Union[str | None] = Field(default=None,min_length=6,max_length=100)
    cli_phone: Union[str | None] = Field(default=None,min_length=11,max_length=15)

class Client(ClientBase, table=True):
    cli_id: int = Field(default=None, primary_key=True)
    cli_createdat: Union[datetime, None] = Field(default=datetime.utcnow)
    cli_active: bool = Field(default=True)