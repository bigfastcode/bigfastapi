class Ticket(_pydantic.BaseModel):
    title: str
    issue: str


    class Config:
        orm_mode = True

class TicketInDB(Ticket):
    opened_by: str
    short_id: str
    closed: bool
    date_created: _dt.datetime

class ClosedTicket(TicketInDB):
    closed_by: str

class TicketReply(_pydantic.BaseModel):
    reply: str

    class Config:
        orm_mode = True

        
class TicketReplyInDB(TicketReply):
    reply_by: str
    date_created: _dt.datetime

class Faq(_pydantic.BaseModel):
    question: str
    answer: str

    class Config:
        orm_mode = True

class FaqInDB(Faq):
    created_by: str
    date_created: _dt.datetime
