import datetime as _dt
from enum import Enum
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
    redirect_url: str


class PaymentProvider(Enum):
    FLUTTERWAVE = 'flutterwave'
    MPESA = 'mpesa'
    MTN_MOBILE_MONEY = 'mtn_mobile_money'
