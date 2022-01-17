import datetime as _dt
import sqlalchemy.orm as _orm

from bigfastapi.utils import generate_short_id
from . import models as _models, schema as _schemas
from fastapi.responses import JSONResponse
from fastapi import status
from uuid import uuid4
from passlib import hash as _hash



async def create_faq(faq: _schemas.Faq, db: _orm.Session):
    faq = _models.Faq(id = uuid4().hex, question = faq.question, answer = faq.answer)
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return {"message": "Faq created succesfully", "faq": _schemas.Faq.from_orm(faq)}

async def get_faqs_from_db(db: _orm.Session):
    faqs = db.query(_models.Faq).all()
    return list(map(_schemas.FaqInDB.from_orm, faqs))

async def create_ticket(ticket: _schemas.Ticket, user: _schemas.User, db: _orm.Session):
    ticket = _models.Ticket(
        id = uuid4().hex, user_id= user.id, 
        title = ticket.title, 
        issue= ticket.issue, 
        opened_by = f'{user.first_name} {user.last_name}',
        short_id= generate_short_id())
    db.add(ticket)
    db.commit()
    return {"message": "Ticket created succesfully", "ticket": _schemas.Ticket.from_orm(ticket)}

async def get_ticket(db: _orm.Session, short_id: str):
    ticket = db.query(_models.Ticket).filter(_models.Ticket.short_id == short_id).first()
    return _schemas.TicketInDB.from_orm(ticket)

async def get_tickets(db: _orm.Session):
    tickets = db.query(_models.Ticket).all()
    return list(map(_schemas.TicketInDB.from_orm, tickets))

async def reply_ticket(ticket_reply: _schemas.TicketReply, db: _orm.Session, short_id: str, user: _schemas.User):
    if user.is_superuser == True:
        ticket = db.query(_models.Ticket).filter(_models.Ticket.short_id == short_id).first()
        ticket_reply = _models.TicketReply(id = uuid4().hex,ticket_id=ticket.id, reply = ticket_reply.reply, reply_by = f'{user.first_name} {user.last_name}')
        db.add(ticket_reply)
        db.commit()
        db.refresh(ticket_reply)
        return JSONResponse({"message": f"Reply to {ticket.short_id}", "data": ticket_reply.reply}, status_code=status.HTTP_200_OK)
    return JSONResponse({"message": "Only an admin can reply a ticket", "data": None}, status_code=status.HTTP_401_UNAUTHORIZED)


async def close_ticket(db: _orm.Session, short_id: str, user: _schemas.User):
    ticket = db.query(_models.Ticket).filter( _models.Ticket.short_id==short_id).first()
    if user.is_superuser == True:
        ticket.closed = True
        ticket.closed_by = f'{user.first_name} {user.last_name}'
        db.commit()
        db.refresh(ticket)
        return JSONResponse({"message": f"Ticket with id {ticket.id} closed"}, status_code=status.HTTP_200_OK)
    return JSONResponse({"message": "Only an admin can close a ticket"}, status_code=status.HTTP_401_UNAUTHORIZED)

async def get_ticket_replies(db: _orm.Session, short_id: str):
    ticket = db.query(_models.Ticket).filter(_models.Ticket.short_id==short_id).first()
    replies = db.query(_models.TicketReply).filter(_models.TicketReply.ticket_id==ticket.id).all()
    return list(map(_schemas.TicketReplyInDB.from_orm, replies))

async def get_open_tickets(db: _orm.Session):
    tickets = db.query(_models.Ticket).filter(_models.Ticket.closed==False).all()
    print("open tickets")
    return list(map(_schemas.TicketInDB.from_orm, tickets))

async def get_closed_tickets(db: _orm.Session):
    tickets = db.query(_models.Ticket).filter(_models.Ticket.closed==True).all()
    return list(map(_schemas.ClosedTicket.from_orm, tickets))

async def create_fake_user(user: _schemas.FakeUserSchema, db: _orm.Session):
    user = _models.User(
        id = uuid4().hex,

        email = user.email,
        first_name = user.first_name,
        last_name = 'test',
        phone_number = 'test',
        password = _hash.bcrypt.hash(user.password),
        is_active = True,
        is_verified = True,
        organization = 'test')
    db.add(user)
    db.commit()
    db.refresh(user)
    return _schemas.FakeUserSchema.from_orm(user)


async def create_fake_super_user(user: _schemas.FakeUserSchema, db: _orm.Session):
    user = _models.User(
        id = uuid4().hex,

        email = user.email,
        first_name = user.first_name,
        last_name = 'test',
        phone_number = 'test',
        password = _hash.bcrypt.hash(user.password),
        is_active = True,
        is_verified = True,
        is_superuser = True,
        organization = 'test')
    db.add(user)
    db.commit()
    db.refresh(user)
    return _schemas.FakeUserSchema.from_orm(user)



    
