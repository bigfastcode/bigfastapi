import datetime as dt
import pydantic
from typing import Optional


class ContactBase(pydantic.BaseModel):
    address: str
    phone: str
    map_coordinates: str


class Contact(ContactBase):
    id: str
    date_created: dt.datetime
    last_updated: dt.datetime

    class Config:
        orm_mode = True


class ContactUSB(pydantic.BaseModel):
    name: str
    email: str
    subject: Optional[str] = None
    message: str


class ContactRequest(ContactUSB):
    id: str
    date_created: dt.datetime

    class Config:
        orm_mode = True
