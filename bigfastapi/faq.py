import fastapi
from uuid import uuid4
from typing import List
import sqlalchemy.orm as orm
from fastapi import status
from fastapi import APIRouter
from .models import faq_models
from .schemas import faq_schemas
from .auth_api import is_authenticated
from .schemas import users_schemas
from bigfastapi.db.database import get_db
from fastapi.responses import JSONResponse
from bigfastapi.utils.utils import generate_short_id



app = APIRouter(tags=["FAQ and Support ❓"])


# ////////////////////////////////////////////////////////////////
#                          FAQ Endpoint

@app.post('/support/faqs', response_model=faq_schemas.CreateFaqRes)
def create_faq(
    faq: faq_schemas.Faq, 
    db: orm.Session = fastapi.Depends(get_db), 
    user: users_schemas.User = fastapi.Depends(is_authenticated)):

     

    if user.is_superuser == True:
        faq = faq_models.Faq(
            id = uuid4().hex, 
            question = faq.question, 
            answer = faq.answer,
            created_by = f'{user.first_name} {user.last_name}'
            )
        db.add(faq)
        db.commit()
        db.refresh(faq)
        return {"message": "Faq created succesfully", "faq": faq_schemas.Faq.from_orm(faq)}

    return JSONResponse({"message": "only an admin can create a faq"}, status_code=status.HTTP_401_UNAUTHORIZED)


@app.get('/support/faqs', response_model=List[faq_schemas.FaqInDB])
def get_faqs(db: orm.Session = fastapi.Depends(get_db)):

    """model for support and faqs
    
    Args:
        id (str): 

    Returns:
        Faq created succesfully
    """
    
    faqs = db.query(faq_models.Faq).all()
    return list(map(faq_schemas.FaqInDB.from_orm, faqs))


@app.post('/support/tickets', response_model=faq_schemas.CreateTicketRes)
def create_ticket(
    ticket: faq_schemas.Ticket, 
    user: users_schemas.User = fastapi.Depends(is_authenticated), 
    db: orm.Session = fastapi.Depends(get_db)):

    ticket = faq_models.Ticket(
        id = uuid4().hex, user_id= user.id, 
        title = ticket.title, 
        issue= ticket.issue, 
        opened_by = f'{user.first_name} {user.last_name}',
        short_id= generate_short_id())
    db.add(ticket)
    db.commit()
    return {"message": "Ticket created succesfully", "ticket": faq_schemas.TicketInDB.from_orm(ticket)}

@app.get('/support/ticket/{short_id}', response_model=faq_schemas.TicketInDB)
def get_ticket(short_id: str, db: orm.Session = fastapi.Depends(get_db)):
    ticket = db.query(faq_models.Ticket).filter(faq_models.Ticket.short_id == short_id).first()
    return faq_schemas.TicketInDB.from_orm(ticket)


@app.get('/support/tickets', response_model=List[faq_schemas.TicketInDB])
def get_tickets(db: orm.Session = fastapi.Depends(get_db)):
    tickets = db.query(faq_models.Ticket).all()
    return list(map(faq_schemas.TicketInDB.from_orm, tickets))


@app.post('/support/tickets/{short_id}/reply', response_model=faq_schemas.TicketReplyRes)
def reply_ticket(
    ticket_reply: faq_schemas.TicketReply,
    short_id: str,
    db: orm.Session = fastapi.Depends(get_db),
    user: users_schemas.User = fastapi.Depends(is_authenticated)):
    if user.is_superuser == True:
        ticket = db.query(faq_models.Ticket).filter(faq_models.Ticket.short_id == short_id).first()
        ticket_reply = faq_models.TicketReply(id = uuid4().hex,ticket_id=ticket.id, reply = ticket_reply.reply, reply_by = f'{user.first_name} {user.last_name}')
        db.add(ticket_reply)
        db.commit()
        db.refresh(ticket_reply)
        return JSONResponse({"message": f"Reply to {ticket.short_id}", "data": ticket_reply.reply}, status_code=status.HTTP_200_OK)
    return JSONResponse({"message": "Only an admin can reply a ticket", "data": None}, status_code=status.HTTP_401_UNAUTHORIZED)


@app.put('/support/tickets/{short_id}/close', response_model=faq_schemas.TicketCloseRes)
def close_ticket(
    short_id: str,
    db: orm.Session = fastapi.Depends(get_db),
    user: users_schemas.User = fastapi.Depends(is_authenticated)
    ):
    ticket = db.query(faq_models.Ticket).filter( faq_models.Ticket.short_id==short_id).first()
    if user.is_superuser == True:
        ticket.closed = True
        ticket.closed_by = f'{user.first_name} {user.last_name}'
        db.commit()
        db.refresh(ticket)
        return JSONResponse({"message": f"Ticket with id {ticket.short_id} closed"}, status_code=status.HTTP_200_OK)
    return JSONResponse({"message": "Only an admin can close a ticket"}, status_code=status.HTTP_401_UNAUTHORIZED)

@app.get('/support/tickets/{short_id}/replies', response_model=List[faq_schemas.TicketReplyInDB])
def get_ticket_replies(
    short_id: str,
    db: orm.Session = fastapi.Depends(get_db),
    ):
    ticket = db.query(faq_models.Ticket).filter(faq_models.Ticket.short_id==short_id).first()
    replies = db.query(faq_models.TicketReply).filter(faq_models.TicketReply.ticket_id==ticket.id).all()
    return list(map(faq_schemas.TicketReplyInDB.from_orm, replies))

@app.get('/support/tickets/open', response_model=List[faq_schemas.TicketInDB])
def get_open_tickets(db: orm.Session = fastapi.Depends(get_db)):
    tickets = db.query(faq_models.Ticket).filter(faq_models.Ticket.closed==False).all()
    print("open tickets")
    return list(map(faq_schemas.TicketInDB.from_orm, tickets))

@app.get('/support/tickets/closed', response_model=List[faq_schemas.ClosedTicket])
def get_closed_tickets(db: orm.Session = fastapi.Depends(get_db)):
    tickets = db.query(faq_models.Ticket).filter(faq_models.Ticket.closed==True).all()
    return list(map(faq_schemas.ClosedTicket.from_orm, tickets))





