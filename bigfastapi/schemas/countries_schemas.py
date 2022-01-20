

class State(_pydantic.BaseModel):
    name:str
    state_code:str

class Country(_pydantic.BaseModel):
    name:str
    iso3:str
    iso2:str
    dial_code:str
    states: List[State]
