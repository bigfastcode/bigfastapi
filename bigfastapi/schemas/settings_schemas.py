

import datetime as _dt

import pydantic as _pydantic
from pydantic import Field
from uuid import UUID
from typing import List, Optional

class SettingsBase(_pydantic.BaseModel):
    organization_settings: str
    user_settings: str
   


class SettingsSave(SettingsBase):
    location : str
    phone_number = str
    email = str
    organization_size = str
    organization_type = str
    country = str
    state = str
    city = str
    zip_code = int


class Settings(SettingsBase):
    id: str
    location = str
    phone_number = str
    email = str
    organization_size = str
    organization_type = str
    country = str
    state = str
    city = str
    zip_code = int


    class Config:
        orm_mode = True

