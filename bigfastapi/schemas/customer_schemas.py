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
    first_name: str = " "
    last_name: str = " "
    unique_id:Optional[str]
    organization_id: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    business_name: Optional[str]
    location: Optional[str]
    gender: Optional[str]
    age: Optional[int]
    postal_code: Optional[str]
    language: Optional[str]
    country: Optional[str]
    city: Optional[str]
    region: Optional[str]
    country_code: Optional[str]
    other_info: List[OtherInfo] = []
    is_deleted: bool = False

    class Config:
        orm_mode = True

class Customer(CustomerBase):
    customer_id: str
    date_created: datetime
    last_updated: datetime

class CustomerUpdate(BaseModel):
    unique_id: Optional[str] 
    first_name: Optional[str] = " "
    last_name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str] 
    organization_id: Optional[str]
    business_name: Optional[str]
    location: Optional[str]
    gender: Optional[str]
    age: Optional[int] 
    postal_code: Optional[str] 
    language: Optional[str]
    country: Optional[str]
    city: Optional[str]
    region: Optional[str]
    country_code: Optional[str]
    other_info: List[OtherInfo]
    

class CustomerResponse(BaseModel):
    message: Optional[str]
    customer: Optional[Customer]
