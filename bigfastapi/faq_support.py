from fastapi import APIRouter
from .schema import Faq as faqschema
from .schema import Ticket as ticketschema
import sqlalchemy.orm as _orm
import fastapi as _fastapi
from bigfastapi.database import get_db
from . import services as _services, schema as _schemas, faq_services as _faq_services
from .database import create_database



app = APIRouter(tags=["FAQ and Support"])


@app.post('/faqs/create')
async def create_faq(faq: faqschema, db: _orm.Session = _fastapi.Depends(get_db)):
    return await _faq_services.create_faq(faq=faq, db=db)

@app.get('/faqs')
async def get_faqs(db: _orm.Session = _fastapi.Depends(get_db)):
    return await _faq_services.get_faqs_from_db(db=db)

@app.post('/support/tickets/create')
async def create_ticket(
    ticket: ticketschema, 
    user: _schemas.User = _fastapi.Depends(_services.is_authenticated), 
    db: _orm.Session = _fastapi.Depends(get_db)):
    return await _faq_services.create_ticket(ticket=ticket, user=user, db=db)

@app.get('/support/tickets/view/{ticket_id}')
async def get_ticket(ticket_id: str, db: _orm.Session = _fastapi.Depends(get_db)):
    return await _faq_services.get_ticket(ticket_id=ticket_id, db=db)

@app.get('/support/tickets')
async def get_tickets(db: _orm.Session = _fastapi.Depends(get_db)):
    return await _faq_services.get_tickets(db=db)
