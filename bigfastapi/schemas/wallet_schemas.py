import datetime as _dt
from enum import auto, Enum

import pydantic as _pydantic


class PaymentProvider(Enum):
    FLUTTERWAVE = 'flutterwave'
    MPESA = 'mpesa'
    MTN_MOBILE_MONEY = 'mtn_mobile_money'


class WalletCreate(_pydantic.BaseModel):
    organization_id: str


class Wallet(WalletCreate):
    id: str
    balance: int
    last_updated: _dt.datetime

    class Config:
        orm_mode = True


class WalletUpdate(_pydantic.BaseModel):
    amount: float


class WalletFund(WalletUpdate):
    provider: PaymentProvider
    ref: str
