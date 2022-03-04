import pydantic as _pydantic


class CreditWalletConversion(_pydantic.BaseModel):
    rate: float
    currency_code: str

    class Config:
        orm_mode = True
