from datetime import datetime
from typing import Optional, List, bool
from pydantic import BaseModel, root_validator
from fastapi import HTTPException, status

class SalesBase(BaseModel):
    sale_id :str
    creator_id:str
    product_id :str
    customer_id :str
    organization_id :str
    amount :str = 0
    sale_currency :str
    mode_of_payment :str
    payment_status:str
    sales_status:str
    description: Optional[str]
    is_deleted: bool = False
    date_created:  datetime
    last_updated: datetime