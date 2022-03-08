import datetime

import pydantic as _pydantic


class CreditWalletFund(_pydantic.BaseModel):
    currency: str
    amount: float
    # type: str
    redirect_url: str


class CreditWalletFundResponse(_pydantic.BaseModel):
    link: str


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
