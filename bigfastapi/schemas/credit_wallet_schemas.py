import datetime

import pydantic as _pydantic


class CreditWalletCreate(_pydantic.BaseModel):
    type: str
    amount: float


class CreditWallet(CreditWalletCreate):
    organization_id: str


class CreditWalletResponse(CreditWalletCreate):
    type: str
    amount: float
    last_updated: datetime.datetime
    id: str

    class Config:
        orm_mode = True