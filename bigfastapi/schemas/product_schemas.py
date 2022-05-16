
import datetime as dt
from pydoc import describe
from fastapi import File, UploadFile
from pydantic import BaseModel 
from pydantic import Field
from uuid import UUID
from typing import List, Optional
from bigfastapi.utils.schema_form import as_form


class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    # images: str
    unique_id: Optional[str] = None
    quantity: int

class Product(ProductBase):
    id: str
    discount: str
    created: dt.datetime
    business_id: str
    status: bool

    class Config:
        orm_mode = True

@as_form
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    # images: str
    unique_id: Optional[str] = None
    quantity: int
    discount: float

class ProductImage(ProductCreate):
    product_image: str

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    description: Optional[str]= None
    price: Optional[float] = None
    # images: str
    unique_id: Optional[str] = None
    quantity: Optional[int] = None
    discount: Optional[str] = None

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