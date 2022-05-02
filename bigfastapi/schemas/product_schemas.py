
import datetime as dt
from pydoc import describe

from pydantic import BaseModel 
from pydantic import Field
from uuid import UUID
from typing import List, Optional

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    image: str

class Product(ProductBase):
    id: str
    discount: str
    created: dt.datetime

    class Config:
        orm_mode = True

class ProductCreate(ProductBase):
    discount: float
    business_id: str
    pass

class ProductUpdate(ProductBase):
    discount: str
    pass


class ShowProduct(ProductBase):
    created_by: str
    discount: float

    class Config:
        orm_mode = True
