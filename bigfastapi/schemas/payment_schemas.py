from typing import Optional

import pydantic as _pydantic


class Payment(_pydantic.BaseModel):
    type: str
    organization_id: str
    type_id: Optional[str]
    amount: str


class PaymentLink(_pydantic.BaseModel):
    link: str
