
import datetime as dt
from pydoc import describe
from fastapi import File, UploadFile

from pydantic import BaseModel 
from pydantic import Field
from uuid import UUID
from typing import List, Optional

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    # images: str
    unique_id: str
    quantity: int

class Product(ProductBase):
    id: str
    discount: str
    created: dt.datetime
    business_id: str
    status: bool

    class Config:
        orm_mode = True

class ProductCreate(ProductBase):
    discount: float
    business_id: str
    files: Optional [List[UploadFile]] = None


class ProductUpdate(ProductBase):
    discount: str


class ShowProduct(Product):
    created_by: str

    class Config:
        orm_mode = True

class ProductOut(BaseModel):
    page: int
    size: int
    total: int
    previous_page: Optional[str]
    next_page: Optional[str]
    items: List[ShowProduct]

    class Config:
        orm_mode = True