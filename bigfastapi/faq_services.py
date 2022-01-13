import datetime as _dt
import sqlalchemy.orm as _orm
from . import models as _models, schema as _schemas



async def create_faq(faq: _schemas.Faq, db: _orm.Session):
    faq = _models.Faq(question = faq.question, answer = faq.answer)
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return _schemas.Faq.from_orm(faq)

async def get_faqs_from_db(db: _orm.Session):
    faqs = db.query(_models.Faq).all()
    return list(map(_schemas.Faq.from_orm, faqs))

async def create_ticket(ticket: _schemas.Ticket,user: _schemas.User, db: _orm.Session):
    ticket = _models.Ticket(user_id= user.id, title = ticket.title, issue= ticket.issue)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return _schemas.Ticket.from_orm(ticket)

async def get_ticket(db: _orm.Session, ticket_id: str):
    ticket = db.query(_models.Ticket).get(ticket_id= ticket_id)
    return _schemas.Ticket.from_orm(ticket)

async def get_tickets(db: _orm.Session):
    tickets = db.query(_models.Ticket).all()
    return list(map(_schemas.Ticket.from_orm, tickets))