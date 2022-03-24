import datetime as _dt
from enum import Enum
from typing import Optional

import pydantic as _pydantic


class WalletTransaction(_pydantic.BaseModel):
    amount: float
    transaction_ref: str
    transaction_date: _dt.datetime
    currency_code: str
    id: str
    status: bool
    wallet_id: str

    class Config:
        orm_mode = True


class WalletCreate(_pydantic.BaseModel):
    organization_id: str
    currency_code: str
    user_id: Optional[str]


class Wallet(WalletCreate):
    id: str
    balance: float
    last_updated: _dt.datetime

    class Config:
        orm_mode = True


class WalletUpdate(_pydantic.BaseModel):
    amount: float
    currency_code: str
    redirect_url: str


class PaymentProvider(Enum):
    FLUTTERWAVE = 'flutterwave'
    STRIPE = 'stripe'
