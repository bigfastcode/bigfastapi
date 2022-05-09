from datetime import datetime
from enum import unique
from typing import Optional, List
from pydantic import BaseModel, root_validator
from fastapi import HTTPException, status
from bigfastapi.utils import utils

class SaleBase(BaseModel):
    sale_id :str = utils.generate_short_id(size=12)
    unique_id: str = utils.generate_random_int()
    product_id :str
    customer_id :str
    organization_id : str
    amount :int
    sale_currency :str
    mode_of_payment : str
    payment_status:Optional[str]
    sales_status:Optional[str]
    description: Optional[str]
    is_deleted: bool = False
    date_created:  datetime = datetime.utcnow()
    last_updated: Optional[datetime] = datetime.utcnow()

    class Config:
        orm_mode = True

class SaleUpdate(BaseModel):
    product_id :Optional[str]
    customer_id :Optional[str]
    amount :Optional[str]
    sale_currency :Optional[str]
    mode_of_payment : Optional[str]
    payment_status:Optional[str]
    sales_status:Optional[str]
    description: Optional[str]
    is_deleted: Optional[bool] = False
    last_updated: datetime = datetime.utcnow()
    
    class Config:
        orm_mode = True


class SaleResponse(BaseModel):
    message: Optional[str]
    sale: Optional[SaleBase]