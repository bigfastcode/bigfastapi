
import pydantic
import datetime as dt


################## Tickets ###################

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

class CreateTicketRes(pydantic.BaseModel):
    message: str
    ticket: TicketInDB

class TicketCloseRes(pydantic.BaseModel):
    message: str

class TicketReplyRes(pydantic.BaseModel):
    message: str
    reply: TicketReply

###################### FAQ #########################
 
class Faq(pydantic.BaseModel):
    question: str
    answer: str

    class Config:
        orm_mode = True


class FaqInDB(Faq):
    created_by: str
    date_created: dt.datetime


class CreateFaqRes(pydantic.BaseModel):
    message: str
    faq: Faq