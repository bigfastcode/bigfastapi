from datetime import datetime
from enum import unique
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class OtherInfo(BaseModel):
    value: str
    key: str
    class Config:
        orm_mode = True

class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    unique_id:str
    organization_id: str
    email: str = None
    phone_number: str = None
    business_name: str =None
    location: str =None
    gender: str=None
    age: int =None
    postal_code: str =None
    language: str =None
    country: str = None
    city: str =None
    region: str =None
    country_code: str = None
    other_info: List[OtherInfo] = None

    class Config:
        orm_mode = True

class Customer(CustomerBase):
    customer_id: str
    date_created: datetime
    last_updated: datetime

class CustomerUpdate(BaseModel):
    unique_id: Optional[str] =None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    organization_id: Optional[str] = None
    business_name: str =None
    location: str =None
    gender: Optional[str] = None
    age: Optional[int] = None
    postal_code: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country_code: Optional[str] = None
    other_info: List[OtherInfo] = None
    

class CustomerResponse(BaseModel):
    message: str 
    customer: Customer =None
