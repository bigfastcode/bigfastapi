import datetime as dt
from pydoc import describe
from fastapi import File, UploadFile
from pydantic import BaseModel 
from pydantic import Field
from uuid import UUID
from typing import List, Optional
from bigfastapi.utils.schema_form import as_form


class StockBase(BaseModel):
    name: Optional[str]= None
    quantity: int
    price: float

class CreateStock(StockBase):
    product_id: str
    organization_id: str

class ShowStock(StockBase):
    id: str
    product_id: str
    status: bool
    created_by: str
    date_created: dt.datetime

    class Config:
        orm_mode = True

class StockOut(BaseModel):
    page: int
    size: int
    total: int
    previous_page: Optional[str]
    next_page: Optional[str]
    items: List[ShowStock]

    class Config:
        orm_mode = True

class StockUpdate(StockBase):
    name: Optional[str]= None
    quantity: Optional[int] = None
    price: Optional[float] = None
    status: Optional[bool] = None
    organization_id: str

class DeleteStock(BaseModel):
    organization_id: str

class DeleteSelectedStock(BaseModel):
    stock_id_list: list
    organization_id: str

    class Config:
        orm_mode = True
    


