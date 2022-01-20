
class _OrganizationBase(_pydantic.BaseModel):
    mission: str
    vision: str
    name: str
    values: list


class OrganizationCreate(_OrganizationBase):
    pass

class OrganizationUpdate(_OrganizationBase):
    pass


class Organization(_OrganizationBase):
    id: str
    values:list
    creator: str
    date_created: _dt.datetime
    last_updated: _dt.datetime

    class Config:
        orm_mode = True
