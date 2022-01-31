from .models import email_models
from .schemas import email_schema
from typing import Optional
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Response
from bigfastapi.db.database import get_db
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel
import fastapi
import sqlalchemy.orm as orm
from bigfastapi.utils import settings


app = APIRouter(tags=["Transactional Emails 📧"])


class ResponseModel(BaseModel):
    message: str



@app.post("/email/send", response_model=ResponseModel)
def send_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "base_email.html",
    db: orm.Session = fastapi.Depends(get_db)
):
    send_email(email_details=email_details, background_tasks=background_tasks, template=template, db=db)

    return {"message": "Email will be sent in the background"}


@app.post("/email/send/notification", response_model=ResponseModel)
def send_notification_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "notification_email.html",
    db: orm.Session = fastapi.Depends(get_db)
):
    send_email(email_details=email_details, background_tasks=background_tasks, template=template, db=db)
    return {"message": "Notification Email will be sent in the background"}



@app.post("/email/send/invoice", response_model=ResponseModel)
def send_invoice_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "invoice_email.html",
    db: orm.Session = fastapi.Depends(get_db)

):
    send_email(email_details=email_details, background_tasks=background_tasks, template=template, db=db)
    return {"message": "Invoice Email will be sent in the background"}


@app.post("/email/send/receipt", response_model=ResponseModel)
def send_receipt_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "receipt_email.html",
    db: orm.Session = fastapi.Depends(get_db)
):
    send_email(email_details=email_details, background_tasks=background_tasks, template=template, db = db)
    return {"message": "Receipt Email will be sent in the background"}

@app.post("/email/send/welcome", response_model=ResponseModel)
def send_welcome_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "welcome.html",
    db: orm.Session = fastapi.Depends(get_db)
):
    send_email(email_details=email_details, background_tasks=background_tasks, template=template, db = db)
    return {"message": "Welcome Email will be sent in the background"}

@app.post("/email/send/verification", response_model=ResponseModel)
def send_verification_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "verification_email.html",
    db: orm.Session = fastapi.Depends(get_db)
):
    send_email(email_details=email_details, background_tasks=background_tasks, template=template, db = db)
    return {"message": "Verification Email will be sent in the background"}

@app.post("/email/send/reset-password", response_model=ResponseModel)
def send_reset_password_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "reset_password_email.html",
    db: orm.Session = fastapi.Depends(get_db)
):
    send_email(email_details=email_details, background_tasks=background_tasks, template=template, db = db)
    return {"message": "Reset Password Email will be sent in the background"}

#=================================== EMAIL SERVICES =================================#

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=settings.TEMPLATE_FOLDER,
)


def send_email(email_details: email_schema.Email, background_tasks: BackgroundTasks, template: str, db: orm.Session):
    date_created = datetime.now()
    message = MessageSchema(
        subject=email_details.subject,
        recipients=[email_details.recipient],
        template_body={
            "title": email_details.title,
            "first_name": email_details.first_name,
            "body": email_details.body,
            "date_created": date_created,
            "amount": email_details.amount,
            "due_date": email_details.due_date,
            "link": email_details.link,
            "extra_link": email_details.extra_link,
            "invoice_id": email_details.invoice_id,
            "description": email_details.description,
            "receipt_id": email_details.receipt_id
        },
        subtype="html",
    )
    email = email_models.Email(
        id=uuid4().hex,
        subject=email_details.subject,
        recipient=email_details.recipient,
        title=email_details.title,
        first_name=email_details.first_name,
        body=email_details.body,
        amount = email_details.amount,
        due_date = email_details.due_date,
        link = email_details.link,
        extra_link=email_details.extra_link,
        invoice_id = email_details.invoice_id,
        receipt_id = email_details.receipt_id,
        description = email_details.description,
        date_created=date_created,
    )
    db.add(email)
    db.commit()
    db.refresh(email)
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message, template_name=template)


async def send_email_user(email: str, user, template, title: str, path="", code=""):
    if path == "" and code != "":
        message = MessageSchema(
        subject="Password Reset",
        recipients=[email],
        template_body={
            "title": title,
            "first_name": user.first_name,
            "code": code
        },
        subtype="html",
        )
        fm = FastMail(conf)
        return await fm.send_message(message, template)
    else:
        message = MessageSchema(
        subject="Password Reset",
        recipients=[email],
        template_body={
            "title": title,
            "first_name": user.first_name,
            "path": path
        },
        subtype="html",
        )
        fm = FastMail(conf)
        return await fm.send_message(message, template)


    