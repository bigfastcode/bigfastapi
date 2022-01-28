

import datetime as _dt

import pydantic as _pydantic
from pydantic import Field
from uuid import UUID
from typing import List, Optional

class _OrganizationBase(_pydantic.BaseModel):
    mission: str
    vision: str
    name: str
    values: str
  

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


