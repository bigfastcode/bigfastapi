import datetime as _dt

import pydantic as _pydantic


class Wallet(_pydantic.BaseModel):
    id: str
    organization_id: str
    balance: int
    last_updated: _dt.datetime

    class Config:
        orm_mode = True
