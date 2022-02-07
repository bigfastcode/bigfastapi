import datetime as _dt

import pydantic as _pydantic


class Credit(_pydantic.BaseModel):
    amount: str
    organization_id: str
