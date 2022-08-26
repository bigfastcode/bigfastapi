import datetime as date
from enum import Enum
from typing import Optional, List

import pydantic


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


class Frequencies(str, Enum):
    Yearly = "yearly"
    Monthly = "monthly"
    Daily = "daily"


class BankBase(pydantic.BaseModel):
    account_number: int
    bank_name: str
    recipient_name: str = None
    account_type: str = None
    currency: Optional[str]  # currency is supposed to be require. Optional for the sake of old data
    frequency: Frequencies = None


class AddBank(BankBase):
    organization_id: str
    bank_address: str
    swift_code: Optional[str]
    sort_code: Optional[str]
    country: str
    aba_routing_number: Optional[str]
    iban: Optional[str]
    is_preferred: bool = False
    date_created: Optional[date.datetime]


class BankResponse(AddBank):
    id: str
    creator_id: str
    last_updated: Optional[date.datetime]

    class Config:
        orm_mode = True


class PaginatedBankResponse(pydantic.BaseModel):
    page: int
    size: int
    total: int
    items: List[BankResponse]
    previous_page: Optional[str]
    next_page: Optional[str]

    class Config:
        orm_mode = True