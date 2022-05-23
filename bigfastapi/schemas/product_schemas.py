
import datetime as dt
from pydantic import BaseModel 
from typing import List, Optional, Any
from bigfastapi.utils.schema_form import as_form


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    unique_id: Optional[str] = None

class Product(ProductBase):
    id: str
    created: dt.datetime
    business_id: str
    product_image: Optional[List[Any]] = []


    class Config:
        orm_mode = True

@as_form
class ProductCreate(BaseModel):
    name: str
    description: str
    unique_id: Optional[str] = None
    business_id: str

class ProductImage(ProductCreate):
    product_image: str

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    description: Optional[str]= None
    business_id: str

class ShowProduct(Product):
    created_by: str
    product_image: Optional[List[Any]] = []

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

class DeleteProduct(BaseModel):
    business_id: str


class DeleteSelectedProduct(BaseModel):
    product_id_list: list
    business_id: str

    class Config:
        orm_mode = True
