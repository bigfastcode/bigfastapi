import datetime as _dt

import pydantic as _pydantic


class _OrganizationBase(_pydantic.BaseModel):
    mission: str
    vision: str
    name: str
    values: str
    currency: str

    class Config:
        orm_mode = True


class OrganizationCreate(_OrganizationBase):
    pass


class OrganizationUpdate(_OrganizationBase):
    pass


class Organization(_OrganizationBase):
    id: str
    creator: str
    date_created: _dt.datetime
    last_updated: _dt.datetime

    class Config:
        orm_mode = True
