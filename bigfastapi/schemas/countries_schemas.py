
import datetime as _dt

import pydantic as _pydantic
from pydantic import Field
from uuid import UUID
from typing import List, Optional

class State(_pydantic.BaseModel):
    name:str
    state_code:str

class Country(_pydantic.BaseModel):
    name:str
    iso3:str
    iso2:str
    dial_code:str
    states: List[State]
