from .models import email_models as trans_models
from .schemas import email_schema
from typing import Optional
from bigfastapi.schemas.email_schema import InvoiceMail, ReceiptMail
from uuid import uuid4
from .mail import conf
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Response
from bigfastapi.db.database import get_db
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema
from pydantic import BaseModel
import fastapi
import sqlalchemy.orm as orm

app = APIRouter(tags=["Transactional Emails 📧"])


class ResponseModel(BaseModel):
    message: str


def send_email_background(
    background_tasks: BackgroundTasks, message: MessageSchema, template: str
):
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message, template_name=template)


@app.post("/email/send", response_model=ResponseModel)
def send_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "base.html",
    db: orm.Session = fastapi.Depends(get_db),
):
    date_created = datetime.now()
    message = MessageSchema(
        subject=email_details.subject,
        recipients=[email_details.recipient],
        template_body={
            "title": email_details.title,
            "first_name": email_details.first_name,
            "body": email_details.body,
            "date_created": date_created,
        },
        subtype="html",
    )

    email = trans_models.Email(
        id=uuid4().hex,
        subject=email_details.subject,
        recipient=email_details.recipient,
        title=email_details.title,
        first_name=email_details.first_name,
        body=email_details.body,
        date_created=date_created,
    )
    db.add(email)
    db.commit()
    db.refresh(email)

    send_email_background(
        background_tasks=background_tasks, message=message, template=template
    )
    return {"message": "Email will be sent in the background"}


@app.post("/email/send/notification", response_model=ResponseModel)
def send_notification_email(
    email_details: email_schema.NotificationEmail,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "notification_email.html",
    db: orm.Session = fastapi.Depends(get_db),
):
    date_created = datetime.now()
    message = MessageSchema(
        subject=email_details.subject,
        recipients=[email_details.recipient],
        template_body={
            "title": email_details.title,
            "first_name": email_details.first_name,
            "body": email_details.body,
            "date_created": date_created,
            "from": email_details.sender
        },
        subtype="html",
    )

    email = trans_models.NotificationEmail(
        id=uuid4().hex,
        subject=email_details.subject,
        recipient=email_details.recipient,
        title=email_details.title,
        first_name=email_details.first_name,
        body=email_details.body,
        sender = email_details.sender,
        date_created=date_created,
    )
    db.add(email)
    db.commit()
    db.refresh(email)

    send_email_background(
        background_tasks=background_tasks, message=message, template=template
    )
    return {"message": "Notification Email will be sent in the background"}



@app.post("/email/send/invoice", response_model=ResponseModel)
def send_invoice_mail(
    invoice_details: InvoiceMail,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "invoice_email.html",
    db: orm.Session = fastapi.Depends(get_db),
):
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
        id=uuid4().hex,
        subject=invoice_details.subject,
        recipient=invoice_details.recipient,
        title=invoice_details.title,
        first_name=invoice_details.first_name,
        amount=invoice_details.amount,
        due_date=invoice_details.due_date,
        payment_link=invoice_details.payment_link,
        invoice_id=invoice_details.invoice_id,
        description=invoice_details.description,
        date_created=date_created,
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    send_email_background(
        background_tasks=background_tasks, message=message, template=template
    )
    return {"message": "Invoice Email will be sent in the background"}


@app.post("/email/send/receipt", response_model=ResponseModel)
def send_receipt_mail(
    receipt_details: ReceiptMail,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "receipt_email.html",
    db: orm.Session = fastapi.Depends(get_db),
):
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
        id=uuid4().hex,
        subject=receipt_details.subject,
        recipient=receipt_details.recipient,
        title=receipt_details.title,
        first_name=receipt_details.first_name,
        amount=receipt_details.amount,
        receipt_id=receipt_details.receipt_id,
        description=receipt_details.description,
        date_created=date_created,
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    send_email_background(
        background_tasks=background_tasks, message=message, template=template
    )
    return {"message": "Receipt Email will be sent in the background"}
