
from typing import List
from pydantic import BaseModel

class State(BaseModel):
    name:str
    state_code:str

class Country(BaseModel):
    name:str
    iso3:str
    iso2:str
    dial_code:str
    states: List[State]
