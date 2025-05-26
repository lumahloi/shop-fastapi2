from sqlmodel import SQLModel, Field
from datetime import datetime
from ..utils.custom_types import UserType


class UserBase(SQLModel):
    usr_name: str = Field(min_length=3, max_length=20, index=True)
    usr_email: str = Field(min_length=10,max_length=25,index=True, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    usr_type: UserType
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "usr_name": "João da Silva",
                    "usr_email": "joao@email.com",
                    "usr_type": "administrador",
                    "usr_pass": "senha1234"
                }
            ]
        }
    }
    
    
class UserCreate(UserBase):
    usr_pass: str = Field(min_length=6, max_length=25)


class UserUpdate(SQLModel):
    usr_type: UserType
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "usr_type": "administrador"
                }
            ]
        }
    }


class User(UserBase, table=True):
    usr_id: int = Field(default= None, primary_key=True)
    usr_active: bool = True
    usr_createdat: datetime = Field(default=datetime.utcnow())
    usr_lastupdate: datetime = Field(default=datetime.utcnow())
    usr_pass: str = Field(max_length=128)
    
    
class UserLogin(SQLModel):
    usr_email: str = Field(min_length=10, max_length=25, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    usr_pass: str = Field(min_length=6, max_length=25)
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "usr_email": "joao@email.com",
                    "usr_pass": "senha1234"
                }
            ]
        }
    }
    
    