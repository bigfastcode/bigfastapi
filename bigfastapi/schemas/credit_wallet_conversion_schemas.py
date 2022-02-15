import pydantic as _pydantic


class CreditWalletConversion(_pydantic.BaseModel):
    credit_wallet_type: str
    rate: float
    currency_code: str

    class Config:
        orm_mode = True
