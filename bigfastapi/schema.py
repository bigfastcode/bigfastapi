import datetime as _dt

import pydantic as _pydantic
from fastapi_utils.guid_type import GUID
from uuid import UUID

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
    organization: str

class UserPasswordUpdate(_pydantic.BaseModel):
    password: str

class UserVerification(_pydantic.BaseModel):
    email: str
    redirect_url: str

class UserCreate(_UserBase):
    password: str
    first_name: str
    last_name: str
    verification_redirect_url: str

    class Config:
        orm_mode = True

class UserOrgLogin(_UserBase):
    password: str
    organization: str
    
class UserLogin(_UserBase):
    password: str


class User(_UserBase):
    id: str
    first_name: str
    last_name: str
    phone_number: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    organization: str

    class Config:
        orm_mode = True


class _OrganizationBase(_pydantic.BaseModel):
    mission: str
    vision: str
    name: str
    values: list


class OrganizationCreate(_OrganizationBase):
    pass

class OrganizationUpdate(_OrganizationBase):
    pass


class Organization(_OrganizationBase):
    id: str
    values:list
    creator: str
    date_created: _dt.datetime
    last_updated: _dt.datetime

    class Config:
        orm_mode = True

class _BlogBase(_pydantic.BaseModel):
    title: str
    content: str
class Blog(_BlogBase):
    id: str
    creator: str
    date_created: _dt.datetime
    last_updated: _dt.datetime

    class Config:
        orm_mode = True

class BlogCreate(_BlogBase):
    pass

class BlogUpdate(_BlogBase):
    pass