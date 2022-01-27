import datetime as date
import pydantic


class AddBank(pydantic.BaseModel):
    account_number: int
    bank_name: str
    account_name: str
    bank_sort_code: str 
    country: str
    created_by : str
    creator_id: str
    date_created : date.datetime
    
class BankResponse(AddBank):
    id: str
    class Config:
        orm_mode = True
