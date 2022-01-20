from fastapi import APIRouter
from .schema import Faq as faqschema
from .schema import Ticket as ticketschema
import sqlalchemy.orm as _orm
import fastapi as _fastapi
from bigfastapi.database import get_db
from . import services as _services, schema as _schemas
from .database import create_database
import pydantic as _pydantic
from typing import List
from . import models as _models
from fastapi.responses import JSONResponse
from fastapi import status
from uuid import uuid4
from bigfastapi.utils import generate_short_id



app = APIRouter(tags=["FAQ and Support ❓"])


class CreateFaqRes(_pydantic.BaseModel):
    message: str
    faq: _schemas.Faq
@app.post('/support/faqs', response_model=CreateFaqRes)
async def create_faq(
    faq: faqschema, 
    db: _orm.Session = _fastapi.Depends(get_db), 
    user: _schemas.User = _fastapi.Depends(_services.is_authenticated)):
    if user.is_superuser == True:
        faq = _models.Faq(
            id = uuid4().hex, 
            question = faq.question, 
            answer = faq.answer,
            created_by = f'{user.first_name} {user.last_name}'
            )
        db.add(faq)
        db.commit()
        db.refresh(faq)
        return {"message": "Faq created succesfully", "faq": _schemas.Faq.from_orm(faq)}
    return JSONResponse({"message": "only an admin can create a faq"}, status_code=status.HTTP_401_UNAUTHORIZED)


@app.get('/support/faqs', response_model=List[_schemas.FaqInDB])
async def get_faqs(db: _orm.Session = _fastapi.Depends(get_db)):
    faqs = db.query(_models.Faq).all()
    return list(map(_schemas.FaqInDB.from_orm, faqs))


class CreateTicketRes(_pydantic.BaseModel):
    message: str
    ticket: _schemas.TicketInDB
@app.post('/support/tickets', response_model=CreateTicketRes)
async def create_ticket(
    ticket: ticketschema, 
    user: _schemas.User = _fastapi.Depends(_services.is_authenticated), 
    db: _orm.Session = _fastapi.Depends(get_db)):
    ticket = _models.Ticket(
        id = uuid4().hex, user_id= user.id, 
        title = ticket.title, 
        issue= ticket.issue, 
        opened_by = f'{user.first_name} {user.last_name}',
        short_id= generate_short_id())
    db.add(ticket)
    db.commit()
    return {"message": "Ticket created succesfully", "ticket": _schemas.TicketInDB.from_orm(ticket)}

@app.get('/support/ticket/{short_id}', response_model=_schemas.TicketInDB)
async def get_ticket(short_id: str, db: _orm.Session = _fastapi.Depends(get_db)):
    ticket = db.query(_models.Ticket).filter(_models.Ticket.short_id == short_id).first()
    return _schemas.TicketInDB.from_orm(ticket)


@app.get('/support/tickets', response_model=List[_schemas.TicketInDB])
async def get_tickets(db: _orm.Session = _fastapi.Depends(get_db)):
    tickets = db.query(_models.Ticket).all()
    return list(map(_schemas.TicketInDB.from_orm, tickets))


class TicketReplyRes(_pydantic.BaseModel):
    message: str
    reply: _schemas.TicketReply
@app.post('/support/tickets/{short_id}/reply', response_model=TicketReplyRes)
async def reply_ticket(
    ticket_reply: _schemas.TicketReply,
    short_id: str,
    db: _orm.Session = _fastapi.Depends(get_db),
    user: _schemas.User = _fastapi.Depends(_services.is_authenticated)):
    if user.is_superuser == True:
        ticket = db.query(_models.Ticket).filter(_models.Ticket.short_id == short_id).first()
        ticket_reply = _models.TicketReply(id = uuid4().hex,ticket_id=ticket.id, reply = ticket_reply.reply, reply_by = f'{user.first_name} {user.last_name}')
        db.add(ticket_reply)
        db.commit()
        db.refresh(ticket_reply)
        return JSONResponse({"message": f"Reply to {ticket.short_id}", "data": ticket_reply.reply}, status_code=status.HTTP_200_OK)
    return JSONResponse({"message": "Only an admin can reply a ticket", "data": None}, status_code=status.HTTP_401_UNAUTHORIZED)


class TicketCloseRes(_pydantic.BaseModel):
    message: str
@app.put('/support/tickets/{short_id}/close', response_model=TicketCloseRes)
async def close_ticket(
    short_id: str,
    db: _orm.Session = _fastapi.Depends(get_db),
    user: _schemas.User = _fastapi.Depends(_services.is_authenticated)
    ):
    ticket = db.query(_models.Ticket).filter( _models.Ticket.short_id==short_id).first()
    if user.is_superuser == True:
        ticket.closed = True
        ticket.closed_by = f'{user.first_name} {user.last_name}'
        db.commit()
        db.refresh(ticket)
        return JSONResponse({"message": f"Ticket with id {ticket.short_id} closed"}, status_code=status.HTTP_200_OK)
    return JSONResponse({"message": "Only an admin can close a ticket"}, status_code=status.HTTP_401_UNAUTHORIZED)

@app.get('/support/tickets/{short_id}/replies', response_model=List[_schemas.TicketReplyInDB])
async def get_ticket_replies(
    short_id: str,
    db: _orm.Session = _fastapi.Depends(get_db),
    ):
    ticket = db.query(_models.Ticket).filter(_models.Ticket.short_id==short_id).first()
    replies = db.query(_models.TicketReply).filter(_models.TicketReply.ticket_id==ticket.id).all()
    return list(map(_schemas.TicketReplyInDB.from_orm, replies))

@app.get('/support/tickets/open', response_model=List[_schemas.TicketInDB])
async def get_open_tickets(db: _orm.Session = _fastapi.Depends(get_db)):
    tickets = db.query(_models.Ticket).filter(_models.Ticket.closed==False).all()
    print("open tickets")
    return list(map(_schemas.TicketInDB.from_orm, tickets))

@app.get('/support/tickets/closed', response_model=List[_schemas.ClosedTicket])
async def get_closed_tickets(db: _orm.Session = _fastapi.Depends(get_db)):
    tickets = db.query(_models.Ticket).filter(_models.Ticket.closed==True).all()
    return list(map(_schemas.ClosedTicket.from_orm, tickets))





