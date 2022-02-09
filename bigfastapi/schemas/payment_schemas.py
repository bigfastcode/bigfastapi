from typing import Optional

import pydantic as _pydantic


class Payment(_pydantic.BaseModel):
    type: str
    organization_id: str
    type_id: Optional[str]
    amount: str
    invoice_id: str
    debt_id: str
    customer_id: str
    bank_account: bool
    plan: str
    amount: str
    redirect_url: str
    currency: str


class PaymentLink(_pydantic.BaseModel):
    link: str
