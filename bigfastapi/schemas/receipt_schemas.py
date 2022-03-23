import datetime
from typing import Optional, List
from pydantic import BaseModel,EmailStr


class atrributes(BaseModel):
    sender: EmailStr
    recipient: List[EmailStr] = []
    message: str
    subject: str

class ResponseModel(BaseModel):
    message: str
