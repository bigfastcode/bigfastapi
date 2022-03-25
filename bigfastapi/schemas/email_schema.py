from pydantic import EmailStr, BaseModel
from typing import Optional, List


class Email(BaseModel):
    subject: str
    recipient: List[EmailStr]
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
    promo_product_name: Optional[str] = None
    promo_product_description: Optional[str] = None
    promo_product_price: Optional[str] = None
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    product_price: Optional[str] = None
    extra_product_name: Optional[str] = None
    extra_product_description: Optional[str] = None
    extra_product_price: Optional[str] = None
    sender_address: str
    sender_city: str
    sender_state: str

