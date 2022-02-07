import pydantic as _pydantic


class Credit(_pydantic.BaseModel):
    amount: float
    organization_id: str


class CreditResponse(Credit):
    last_updated: str
    id: str
