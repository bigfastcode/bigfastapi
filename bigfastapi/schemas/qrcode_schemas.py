from typing import List
from pydantic import BaseModel

class State(BaseModel):
    name:str
    state_code:str
    class Config:
        orm_mode = True