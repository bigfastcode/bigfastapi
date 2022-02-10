import datetime as dt

import pydantic as _pydantic
from pydantic import Field
from uuid import UUID



class GoogleAuth(_pydantic.BaseModel):
    user_id: str
    token: str

