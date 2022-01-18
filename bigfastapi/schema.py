import datetime as _dt

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
    organization: str

class UserPasswordUpdate(_pydantic.BaseModel):
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
    verification_method: str = Field(..., title="The user verification method you prefer, this is either: token or code", example="code")
    verification_redirect_url: Optional[str] = Field(None, title="This is the redirect url if you are chosing token verification method", example="https://bigfastapi.com/verify")
    verification_code_length: Optional[int] = Field(None, title="This is the length of the verification code, which is 6 by default", example=5)

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


class _CommentBase(_pydantic.BaseModel):
    text : str 
    name : str
    email : str

class Comment(_CommentBase):
    id : int
    rel_id : str
    downvotes : int
    upvotes : int
    time_created : _dt.datetime
    time_updated : _dt.datetime
    replies : List["Comment"]
    class Config:
        orm_mode = True

class CommentCreate(_CommentBase):
    pass

class CommentUpdate(_CommentBase):
    pass
        

class State(_pydantic.BaseModel):
    name:str
    state_code:str

class Country(_pydantic.BaseModel):
    name:str
    iso3:str
    iso2:str
    dial_code:str
    states: List[State]
