
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
    images: str

class Product(ProductBase):
    id: str
    discount: str
    created: dt.datetime
    business_id: str

    class Config:
        orm_mode = True

class ProductCreate(ProductBase):
    discount: float
    business_id: str
    pass

class ProductUpdate(ProductBase):
    discount: str
    pass


class ShowProduct(Product):
    created_by: str

    class Config:
        orm_mode = True
