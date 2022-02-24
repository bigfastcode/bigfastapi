from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, EmailStr

class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str = None
    address: str =None
    gender: str=None
    age: int =None
    postal_code: str =None
    language: str =None
    country: str = None
    city: str =None
    region: str =None
    country_code: Optional[str] = None
    other_information: Optional[Any] = {}

    class Config:
        orm_mode = True

class CustomerCreate(CustomerBase):
    organization_id: str

class Customer(CustomerBase):
    organization_id: str
    customer_id: str
    date_created: datetime
    last_updated: datetime

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    organization_id: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    postal_code: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country_code: Optional[str] = None
    other_information: Optional[Any] = {}

class CustomerCreateResponse(BaseModel):
    message: str
    customer: Customer

class ResponseModel(BaseModel):
    message: str
