import datetime as date
from typing import Optional
import pydantic
from enum import Enum

class Countries(str, Enum):
    """Provides choices for supported countries.
    """
    Nigeria = "Nigeria"
    USA = "USA"
    Australia = "Australia"
    Ireland = "Ireland"

    def __str__(self):
        """returns string representation of enum choice"""
        return self.value


class BankBase(pydantic.BaseModel):
    account_number: int
    bank_name: str
    account_name: str = None

class AddBank(BankBase):
    organisation_id: str
    creator_id: str
    address: str = None
    swift_code: str = None
    sort_code: str= None
    postcode: str= None
    country: Countries  
    date_created : date.datetime

    
class BankResponse(AddBank):
    id: str
    class Config:
        orm_mode = True
