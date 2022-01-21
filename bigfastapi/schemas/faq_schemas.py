import datetime as dt
import pydantic
from pydantic import Field
from uuid import UUID
from typing import List, Optional


class Ticket(pydantic.BaseModel):
    title: str
    issue: str


    class Config:
        orm_mode = True

class TicketInDB(Ticket):
    opened_by: str
    short_id: str
    closed: bool
    date_created: dt.datetime

class ClosedTicket(TicketInDB):
    closed_by: str

class TicketReply(pydantic.BaseModel):
    reply: str

    class Config:
        orm_mode = True

        
class TicketReplyInDB(TicketReply):
    reply_by: str
    date_created: dt.datetime

class Faq(pydantic.BaseModel):
    question: str
    answer: str

    class Config:
        orm_mode = True

class FaqInDB(Faq):
    created_by: str
    date_created: dt.datetime
