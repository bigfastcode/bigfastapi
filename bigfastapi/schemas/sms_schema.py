from pydantic import EmailStr, BaseModel
from typing import Optional, List


class SMS(BaseModel):
    sender: str
    recipient: List[EmailStr]
    body: Optional[str] = None