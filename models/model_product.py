from sqlmodel import SQLModel, Field, JSON
from sqlalchemy import Column
from datetime import datetime
from typing import List, Union

from ..utils.custom_types import SizeType, ColorType, CategoryType, SectionType

class ProductBase(SQLModel):
    prod_cat: CategoryType
    prod_price: float = Field(index=True)
    prod_desc: Union[str | None] = Field(max_length=100)
    prod_barcode: str = Field(min_length=43,max_length=43)
    prod_section: SectionType
    prod_initialstock = Union[int | 0] = Field(gt=-1)
    prod_dtval: Union[datetime | None]
    prod_name: str = Field(min_length=3,max_length=50,index=True)
    prod_size: List[SizeType] = Field(default_factory=list, sa_column=Column(JSON))
    prod_color: List[ColorType] = Field(default_factory=list, sa_column=Column(JSON))
    prod_imgs: List[str] | None = Field(default_factory=list, sa_column=Column(JSON))
    
class ProductCreate(ProductBase):
    pass

class ProductUpdate(SQLModel):
    prod_cat: Union[CategoryType | None] = Field(default=None)
    prod_price: Union[float | None] = Field(default=None, gt=0)
    prod_desc: Union[str | None] = Field(default=None, max_length=100)
    prod_section: Union[SectionType | None] = Field(default=None)
    prod_dtval: Union[datetime | None] = Field(default=None)
    prod_name: Union[str | None] = Field(default=None, min_length=3, max_length=50)
    prod_size: Union[List[SizeType] | None] = Field(default=None, sa_column=Column(JSON))
    prod_color: Union[List[ColorType] | None] | None = Field(default=None, sa_column=Column(JSON))
    prod_imgs: Union[List[str] | None] = Field(default=None, sa_column=Column(JSON))


class Product(ProductBase, table=True):
    prod_id: int = Field(default=None, primary_key=True)
    prod_createdat: datetime = Field(default_factory=datetime.utcnow)
    prod_lastupdate: datetime = Field(default_factory=datetime.utcnow)
    prod_stock: int = Field(default=0, gt=-1)