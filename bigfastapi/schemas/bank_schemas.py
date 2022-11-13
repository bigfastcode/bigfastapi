from datetime import datetime
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
    organization_id: str
    country:  str
    account_number: str
    bank_name: str
    bank_code: Optional[str]
    recipient_name: Optional[str]
    account_type: Optional[str]
    currency_code: Optional[str]  # currency is supposed to be require. Optional for the sake of old data
    frequency: Optional[Frequencies]
    bank_address: Optional[str]
    swift_code: Optional[str]
    sort_code: Optional[str]
    aba_routing_number: Optional[str]
    iban: Optional[str]
    is_preferred: bool = False


class AddBank(BankBase):
    id: Optional[str]
    date_created: datetime = datetime.now()

class UpdateBank(BankBase):
    last_updated:datetime = datetime.now()

class BankResponse(BankBase):
    id: str
    creator_id: str
    last_updated: datetime
    date_created: datetime
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