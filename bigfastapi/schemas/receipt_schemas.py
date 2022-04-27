import datetime
from typing import Optional, List
from pydantic import BaseModel,EmailStr


class Receipt(BaseModel):
    id: Optional[str]
    organization_id: Optional[str]
    sender_email: Optional[str]
    message: Optional[str]
    subject: Optional[str]
    recipient: Optional[str]
    file_id: Optional[str]

    class Config:
        orm_mode = True

class atrributes(Receipt):
    recipient: List[EmailStr] = []

class ResponseModel(BaseModel):
    message: str
