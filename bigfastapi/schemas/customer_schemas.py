from datetime import datetime
from email.mime import message
from typing import Optional
from pydantic import BaseModel, EmailStr

class Customer(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    address: str
    gender: str
    age: int
    postal_code: str
    language: str
    country: str
    city: str
    region: str

    class Config:
        orm_mode = True

class CustomerValidator(Customer):
    organization_name: str

class CustomerInDB(Customer):
    organization: str
    customer_id: str
    date_created: datetime
    last_updated: datetime

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    organization_name: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    postal_code: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None

class CustomerCreateResponse(BaseModel):
    message: str
    customer: CustomerInDB

class ResponseModel(BaseModel):
    message: str
