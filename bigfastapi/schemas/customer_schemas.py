from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, root_validator
from fastapi import HTTPException, status
from bigfastapi.utils.utils import generate_short_id, generate_random_int

        
class OtherInfo(BaseModel):
    value: str
    key: str
    class Config:
        orm_mode = True

class CustomerBase(BaseModel):
    customer_id: str = generate_short_id(size=12)
    unique_id: str = generate_random_int()
    first_name: Optional[str] = " "
    last_name: Optional[str] = " "
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
    is_deleted: Optional[bool]  = False
    is_inactive: Optional[bool] = False
    date_created: datetime = datetime.now()
    last_updated: Optional[datetime] = datetime.now()
    default_currency: Optional[str]

    class Config:
        orm_mode = True

    @root_validator(pre=True)
    @classmethod
    def validate_phone_number(cls, values):
        """Validate the presence of a country code when a phone number is provided"""
        code, phone = values.get('country_code'), values.get('phone_number')
        if phone  and not code:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail={"invalid request":'Every phone number requires a valid country code', 
                    "message":"missing country code"})
        return values
    
    @root_validator(pre=True)
    @classmethod
    def validate_unique_id(cls, values):
        """ validates that unique id is not an empty string or a null value"""
        unique_id = values.get('unique_id')
        if not unique_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail={"invalid request":'the unique id cannot be null, none or an empty string', 
                    "message":"invalid unique id value"})
        return values
    


class Customer(CustomerBase):
    customer_id: str
 
 
class CustomerUpdate(BaseModel):
    unique_id: Optional[str] 
    first_name: Optional[str]
    last_name: Optional[str]
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
    other_info: List[OtherInfo]
    is_deleted: Optional[bool]
    is_inactive: Optional[bool]
    last_updated: datetime = datetime.now()
    default_currency: Optional[str]

    class Config:
        orm_mode = True

    @root_validator(pre=True)
    @classmethod
    def validate_phone_number(cls, values):
        """Validate the presence of a country code when a phone number is provided"""
        code, phone = values.get('country_code'), values.get('phone_number')
        if phone  and not code:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail={"invalid request":'Every phone number requires a valid country code', 
                    "message":"missing country code"})
        return values
    
    @root_validator(pre=True)
    @classmethod
    def validate_unique_id(cls, values):
        """ validates that unique id is not an empty string or a null value"""
        unique_id = values.get('unique_id')
        if not unique_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail={"invalid request":'the unique id cannot be null, none or an empty string', 
                    "message":"invalid unique id value"})
        return values

class CustomerResponse(BaseModel):
    message: Optional[str]
    customer: Optional[Customer]

class PaginatedCustomerResponse(BaseModel):
    page: int
    size: int
    total: int
    items: List
    previous_page: Optional[str]
    next_page: Optional[str]

