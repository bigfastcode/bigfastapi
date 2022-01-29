import datetime
from typing import Optional
from pydantic import BaseModel,EmailStr


class atrributes(BaseModel):
    sender: EmailStr
    recipient: list[EmailStr] = []
    message: str
    subject: str
    