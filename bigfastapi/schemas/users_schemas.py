import datetime as dt

# from resource import struct_rusage
from fastapi import File, UploadFile

import pydantic as _pydantic
from pydantic import Field
from uuid import UUID
from typing import List, Optional


class AuthToken(_pydantic.BaseModel):
    id: str
    user_id: str
    token: str

class _UserBase(_pydantic.BaseModel):
    email: str

class UserUpdate(_UserBase):
    first_name: str
    last_name: str
    phone_number: str

class UserActivate(_UserBase):
    is_active: bool

class UserResetPassword(_UserBase):
    email: Optional[str]
    code: str
    password: str

class UserPasswordUpdate(_pydantic.BaseModel):
    code: str
    password: str

class UserTokenVerification(_pydantic.BaseModel):
    email: str
    redirect_url: str
    
class UserCodeVerification(_pydantic.BaseModel):
    email: str
    code_length: Optional[int] = Field(None, title="This is the length of the verification code, which is 6 by default", example=5)

class UserCreate(_UserBase):
    password: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True

class UserCreateOut(_UserBase):
    first_name: str
    last_name: str

    class Config:
        orm_mode = True

class UserInfo(_UserBase):
    first_name: str
    last_name: str


class UserOrgLogin(_UserBase):
    password: str
    organization: str

    
class UserLogin(_UserBase):
    password: str

class UserRecoverPassword(_UserBase):
    pass


class User(_UserBase):
    id: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    is_active: bool
    is_verified: bool
    is_superuser: bool
    country_code: Optional[str]
    image_url: Optional[str] 
    is_deleted: bool
    device_id: Optional[str] 
    country: Optional[str]
    state: Optional[str]
    google_id: Optional[str]
    google_image_url: Optional[str] 
    date_created: dt.datetime
    last_updated: dt.datetime 

    class Config:
        orm_mode = True


class UpdateUserReq(_UserBase):
    first_name: Optional[str]
    last_name: Optional[str]
    country_code: Optional[str]
    phone_number: Optional[str]
    country: Optional[str]
    state: Optional[str]
   
    class Config:
        orm_mode = True
        
        
class updatePasswordRequest(_pydantic.BaseModel):
    password:str
    password_confirmation:str
    

class ImageUploadReq(_pydantic.BaseModel):
    image: UploadFile = File(...)
    




