from typing import Optional, List

from pydantic import BaseModel


class SettingsBase(BaseModel):
    email: str
    location: str
    phone_number: Optional[str] = None
    organization_size: Optional[str] = None
    organization_type: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[int] = None


class SettingsUpdate(SettingsBase):
    pass


class Settings(SettingsBase):
    pass

    class Config:
        orm_mode = True


# App Settings

class CreateAppSetting(BaseModel):
    value: str
    name: str


class AppSetting(CreateAppSetting):
    id: str

    class Config:
        orm_mode = True


class CreateAppSettingBody(BaseModel):
    settings: List[AppSetting]
