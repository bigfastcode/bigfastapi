import datetime as _dt
import pydantic as _pydantic
from pydantic import Field
from uuid import UUID
from typing import List, Optional



class _UserBase(_pydantic.BaseModel):
    email: str

class UserUpdate(_UserBase):
    first_name: str
    last_name: str
    phone_number: str


class UserPasswordUpdate(_pydantic.BaseModel):
    password: str


class UserCreate(_UserBase):
    password: str
    first_name: str
    last_name: str
    phone_number: str
    country_code: str
    
    class Config:
        orm_mode = True
    

class UserLogin(_UserBase):
    password: str



class Token(_UserBase):
    access_token: str
    token_type: str


class TokenData(_UserBase):
    id: Optional[str] = None



class User(_UserBase):
    id: str
    first_name: str
    last_name: str
    phone_number: str
    is_active: bool
    is_verified: bool
    is_superuser: bool


    class Config:
        orm_mode = True

