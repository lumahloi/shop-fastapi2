from sqlmodel import SQLModel, Field
from datetime import datetime

from ..utils.custom_types import UserType

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
    usr_createdat: datetime = Field(default=datetime.utcnow)
    usr_lastupdate: datetime = Field(default=datetime.utcnow)