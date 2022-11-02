import datetime as dt
from typing import Optional

from pydantic import BaseModel


class _UserBase(BaseModel):
    email: Optional[str]


class UserUpdate(_UserBase):
    first_name: str
    last_name: str


class UserPasswordUpdate(BaseModel):
    password: str


class TestIn(_UserBase):
    username: str
    password: str
    full_name: str


class TestOut(_UserBase):
    username: str
    full_name: str


class UserCreate(_UserBase):
    password: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    phone_country_code: Optional[str]
    image_url: Optional[str]
    device_id: Optional[str]
    # country: Optional[str]
    # state: Optional[str]
    google_id: Optional[str]
    google_image_url: Optional[str]

    class Config:
        orm_mode = True


class UserCreateSync(BaseModel):
    id: Optional[str]
    password: str
    email: str
    organization_id: str
    role_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    phone_country_code: Optional[str]
    image_url: Optional[str]
    device_id: Optional[str]
    google_id: Optional[str]
    google_image_url: Optional[str]

    class Config:
        orm_mode = True


class UserCreateOut(_UserBase):
    id: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    is_deleted: Optional[bool]
    is_active: Optional[bool]
    is_superuser: Optional[bool]
    is_verified: Optional[bool]
    phone_number: Optional[str]
    phone_country_code: Optional[str]
    image_url: Optional[str]
    device_id: Optional[str]
    # country: Optional[str]
    # state: Optional[str]
    google_id: Optional[str]
    google_image_url: Optional[str]

    class Config:
        orm_mode = True


class UserLogin(_UserBase):
    phone_number: Optional[str]
    phone_country_code: Optional[str]
    device_id: Optional[str]
    password: str


class Token(_UserBase):
    access_token: str
    token_type: str


class TokenData(_UserBase):
    id: Optional[str] = None


class User(_UserBase):
    id: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    is_active: bool
    is_verified: bool
    is_superuser: bool
    phone_country_code: Optional[str]
    image_url: Optional[str]
    is_deleted: bool
    device_id: Optional[str]
    google_id: Optional[str]
    google_image_url: Optional[str]
    date_created: dt.datetime
    last_updated: dt.datetime

    class Config:
        orm_mode = True


class APIKey(_UserBase):
    app_name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    phone_country_code: Optional[str]
    user_id: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]


class APIKEYCheck(BaseModel):
    app_id: str
    api_key: str


class APIKeyReset(_UserBase):
    code: str
