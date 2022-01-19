from fastapi import APIRouter
from .schema import Faq as faqschema
from .schema import Ticket as ticketschema
import sqlalchemy.orm as _orm
import fastapi as _fastapi
from bigfastapi.database import get_db
from . import services as _services, schema as _schemas, faq_services as _faq_services
from .database import create_database
import pydantic as _pydantic
from typing import List



app = APIRouter(tags=["FAQ and Support ❓"])


class CreateFaqRes(_pydantic.BaseModel):
    message: str
    faq: _schemas.Faq
@app.post('/support/faqs', response_model=CreateFaqRes)
async def create_faq(
    faq: faqschema, 
    db: _orm.Session = _fastapi.Depends(get_db), 
    user: _schemas.User = _fastapi.Depends(_services.is_authenticated)):
    return await _faq_services.create_faq(faq=faq, db=db, user=user)


@app.get('/support/faqs', response_model=List[_schemas.FaqInDB])
async def get_faqs(db: _orm.Session = _fastapi.Depends(get_db)):
    return await _faq_services.get_faqs_from_db(db=db)


class CreateTicketRes(_pydantic.BaseModel):
    message: str
    ticket: _schemas.TicketInDB
@app.post('/support/tickets', response_model=CreateTicketRes)
async def create_ticket(
    ticket: ticketschema, 
    user: _schemas.User = _fastapi.Depends(_services.is_authenticated), 
    db: _orm.Session = _fastapi.Depends(get_db)):
    return await _faq_services.create_ticket(ticket=ticket, user=user, db=db)


@app.get('/support/ticket/{short_id}', response_model=_schemas.TicketInDB)
async def get_ticket(short_id: str, db: _orm.Session = _fastapi.Depends(get_db)):
    return await _faq_services.get_ticket(short_id=short_id, db=db)


@app.get('/support/tickets', response_model=List[_schemas.TicketInDB])
async def get_tickets(db: _orm.Session = _fastapi.Depends(get_db)):
    return await _faq_services.get_tickets(db=db)


class TicketReplyRes(_pydantic.BaseModel):
    message: str
    reply: _schemas.TicketReply
@app.post('/support/tickets/{short_id}/reply', response_model=TicketReplyRes)
async def reply_ticket(
    ticket_reply: _schemas.TicketReply,
    short_id: str,
    db: _orm.Session = _fastapi.Depends(get_db),
    user: _schemas.User = _fastapi.Depends(_services.is_authenticated)):
    return await _faq_services.reply_ticket(ticket_reply=ticket_reply, short_id=short_id, db=db, user=user)

class TicketCloseRes(_pydantic.BaseModel):
    message: str
@app.put('/support/tickets/{short_id}/close', response_model=TicketCloseRes)
async def close_ticket(
    short_id: str,
    db: _orm.Session = _fastapi.Depends(get_db),
    user: _schemas.User = _fastapi.Depends(_services.is_authenticated)
    ):
    return await _faq_services.close_ticket(short_id=short_id, db=db, user=user)

@app.get('/support/tickets/{short_id}/replies', response_model=List[_schemas.TicketReplyInDB])
async def get_ticket_replies(
    short_id: str,
    db: _orm.Session = _fastapi.Depends(get_db),
    ):
    return await _faq_services.get_ticket_replies(db=db, short_id=short_id)

@app.get('/support/tickets/open', response_model=List[_schemas.TicketInDB])
async def get_open_tickets(db: _orm.Session = _fastapi.Depends(get_db)):
    return await _faq_services.get_open_tickets(db=db)

@app.get('/support/tickets/closed', response_model=List[_schemas.ClosedTicket])
async def get_closed_tickets(db: _orm.Session = _fastapi.Depends(get_db)):
    return await _faq_services.get_closed_tickets(db=db)





