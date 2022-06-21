import datetime as dt
from pydantic import BaseModel 
from typing import List, Optional, Any


class ProductPriceBase(BaseModel):
    product_id: str
    stock_id: str
    price: float
    currency: str
    customer_group: Optional[str] = None

class CreateProductPrice(ProductPriceBase):
    start: Optional[dt.date] = None
    end: Optional[dt.date] = None
    apply_on: Optional[str] = None
    organization_id: str
    
class ProductPrice(ProductPriceBase):
    id: str
    start: Optional[dt.datetime] = None
    end: Optional[dt.datetime] = None
    apply_on: Optional[str] = None
    created_by: str
    date_created: dt.datetime
    last_updated: dt.datetime

    class Config:
        orm_mode = True

class ProductPriceUpdate(BaseModel):
    price: Optional[float] = None
    currency: Optional[str] = None
    customer_group: Optional[str] = None
    start: Optional[dt.datetime] = None
    end: Optional[dt.datetime] = None
    apply_on: Optional[str] = None
    organization_id: str


class DeleteProductPrice(BaseModel):
    organization_id: str