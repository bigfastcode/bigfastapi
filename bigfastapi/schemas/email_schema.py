from pydantic import EmailStr, BaseModel
from typing import Optional


class Email(BaseModel):
    subject: str
    recipient: EmailStr
    title: str
    first_name: str
    body: Optional[str] = None
    amount: Optional[str] = None
    due_date: Optional[str] = None
    link: Optional[str] = None
    extra_link: Optional[str] = None
    invoice_id: Optional[str] = None
    description: Optional[str] = None
    receipt_id: Optional[str] = None



