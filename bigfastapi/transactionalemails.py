from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Response
from pydantic import BaseModel
from .mail import conf
from fastapi_mail import FastMail, MessageSchema
from bigfastapi.schemas.transactionalemail_schema import InvoiceMail, ReceiptMail
from bigfastapi.db.database import get_db
import sqlalchemy.orm as orm
import fastapi
from uuid import uuid4
from .models import transactionalemail_models as trans_models


app = APIRouter(tags=["Transactional Emails 📧"])

class ResponseModel(BaseModel):
    message: str

def send_email_background(
    background_tasks: BackgroundTasks, message: MessageSchema, template: str
):
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message, template_name=template)

@app.post('/mail/invoice', response_model=ResponseModel)
def send_invoice_mail(invoice_details: InvoiceMail, background_tasks: BackgroundTasks, db: orm.Session = fastapi.Depends(get_db)):
    date_created = datetime.now()
    message = MessageSchema(
    subject=invoice_details.subject,
    recipients=[invoice_details.recipient],
    template_body={
        "title": invoice_details.title,
        "first_name": invoice_details.first_name,
        "amount": invoice_details.amount,
        "due_date": invoice_details.due_date,
        "payment_link": invoice_details.payment_link,
        "invoice_id": invoice_details.invoice_id,
        "description": invoice_details.description,
        "date_created": date_created, 
    },
    subtype="html",
    )

    invoice = trans_models.InvoiceMail(
            id = uuid4().hex,
            subject = invoice_details.subject,
            recipient = invoice_details.recipient,
            title = invoice_details.title,
            first_name = invoice_details.first_name,
            amount = invoice_details.amount,
            due_date = invoice_details.due_date,
            payment_link = invoice_details.payment_link,
            invoice_id = invoice_details.invoice_id,
            description = invoice_details.description,
            date_created = date_created 
            )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    send_email_background(background_tasks=background_tasks, message=message, template="invoice_email.html")
    return {"message": "Invoice Email will be sent in the background"}

@app.post('/mail/receipt', response_model=ResponseModel)
def send_receipt_mail(receipt_details: ReceiptMail, background_tasks: BackgroundTasks, db: orm.Session = fastapi.Depends(get_db)):
    date_created = datetime.now()
    message = MessageSchema(
    subject=receipt_details.subject,
    recipients=[receipt_details.recipient],
    template_body={
        "title": receipt_details.title,
        "first_name": receipt_details.first_name,
        "amount": receipt_details.amount,
        "receipt_id": receipt_details.receipt_id,
        "description": receipt_details.description,
        "date_created": date_created, 
    },
    subtype="html",
    )

    receipt = trans_models.ReceiptMail(
            id = uuid4().hex,
            subject = receipt_details.subject,
            recipient = receipt_details.recipient,
            title = receipt_details.title,
            first_name = receipt_details.first_name,
            amount = receipt_details.amount,
            receipt_id = receipt_details.receipt_id,
            description = receipt_details.description,
            date_created = date_created 
            )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    send_email_background(background_tasks=background_tasks, message=message, template="receipt_email.html")
    return {"message": "Receipt Email will be sent in the background"}



