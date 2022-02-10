import datetime as _dt
from typing import Optional

import pydantic as _pydantic


class WalletCreate(_pydantic.BaseModel):
    organization_id: str
    currency_code: str
    user_id: Optional[str]


class Wallet(WalletCreate):
    id: str
    balance: int
    last_updated: _dt.datetime

    class Config:
        orm_mode = True


class WalletUpdate(_pydantic.BaseModel):
    amount: float
    currency_code: str
