import datetime
from typing import Optional
from pydantic import BaseModel


# TODO: make content accept html
class PageInput(BaseModel):
    title: str
    content: str


class Page(PageInput):
    id: Optional[str]
    date_created: Optional[datetime.datetime]
    last_updated: Optional[datetime.datetime]

    class Config:
        orm_mode = True
