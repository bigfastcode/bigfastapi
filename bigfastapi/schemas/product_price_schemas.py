import datetime as dt
from pydantic import BaseModel 
from typing import List, Optional, Any


class ProductPriceBase(BaseModel):
    product_id: str
    stock_id: str
    price: float
    currency: str
    customer_group: str

class CreateProductPrice(ProductPriceBase):
    start: Optional[dt.datetime] = None
    end: Optional[dt.datetime] = None
    apply_on: Optional[str] = None
    business_id: str
    
class ProductPrice(ProductPriceBase):
    id: str
    start: Optional[dt.datetime] = None
    end: Optional[dt.datetime] = None
    apply_on: Optional[str] = None
    created_by: str
    created_at: dt.datetime
    updated_at: dt.datetime

    class Config:
        orm_mode = True

class DeleteProductPrice(BaseModel):
    business_id: str