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
import time
import os

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
    """An endpoint used to send an email

    Returns:
        object (dict): a message
    """

    send_email(email_details=email_details,
               background_tasks=background_tasks, template=template, db=db)

    return {"message": "Email will be sent in the background"}


@app.post("/email/send/notification", response_model=ResponseModel)
def send_notification_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "notification_email.html",
    db: orm.Session = fastapi.Depends(get_db)
):
    """An endpoint for sending a notification email

    Returns:
        object (dict): a message
    """

    send_email(email_details=email_details,
               background_tasks=background_tasks, template=template, db=db)
    return {"message": "Notification Email will be sent in the background"}


@app.post("/email/send/invoice", response_model=ResponseModel)
def send_invoice_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "invoice_email.html",
    db: orm.Session = fastapi.Depends(get_db)

):
    """An endpoint for sending an invoice email

    Returns:
        object (dict): a message
    """
    send_email(email_details=email_details,
               background_tasks=background_tasks, template=template, db=db)
    return {"message": "Invoice Email will be sent in the background"}


@app.post("/email/send/receipt", response_model=ResponseModel)
def send_receipt_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "receipt_email.html",
    db: orm.Session = fastapi.Depends(get_db)
):
    """An endpoint for sending a receipt email

    Returns:
        object (dict): a message
    """
    send_email(email_details=email_details,
               background_tasks=background_tasks, template=template, db=db)
    return {"message": "Receipt Email will be sent in the background"}


@app.post("/email/send/welcome", response_model=ResponseModel)
def send_welcome_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "welcome.html",
    db: orm.Session = fastapi.Depends(get_db)
):
    """An endpoint for sending a welcome email

    Returns:
        object (dict): a message
    """
    send_email(email_details=email_details,
               background_tasks=background_tasks, template=template, db=db)
    return {"message": "Welcome Email will be sent in the background"}


@app.post("/email/send/verification", response_model=ResponseModel)
def send_verification_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "verification_email.html",
    db: orm.Session = fastapi.Depends(get_db)
):
    """An endpoint for sending verification email

    Returns:
        object (dict): a message
    """

    send_email(email_details=email_details,
               background_tasks=background_tasks, template=template, db=db)
    return {"message": "Verification Email will be sent in the background"}


@app.post("/email/send/reset-password", response_model=ResponseModel)
def send_reset_password_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "reset_password_email.html",
    db: orm.Session = fastapi.Depends(get_db)
):
    """An endpoint for sending a reset password email

    Returns:
        object (dict): a message
    """

    send_email(email_details=email_details,
               background_tasks=background_tasks, template=template, db=db)
    return {"message": "Reset Password Email will be sent in the background"}


@app.post("/email/send/marketing-email", response_model=ResponseModel)
def send_marketing_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "marketing_email.html",
    db: orm.Session = fastapi.Depends(get_db)
):
    """An endpoint for sending a marketing email to a customer or a list of customers

    Returns:
        object (dict): a message
    """

    send_email(email_details=email_details,
               background_tasks=background_tasks, template=template, db=db)
    return {"message": "Marketing Email will be sent in the background"}


@app.post("/email/send/marketing-email/schedule")
def schedule_marketing_email(
    schedule_at: datetime,
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "marketing_email.html",
    db: orm.Session = fastapi.Depends(get_db)
):
    """An endpoint for scheduling a marketing email to be sent at a particular time

    Returns:
        object (dict): a message
    """

    if schedule_at <= datetime.now():
        raise fastapi.HTTPException(
            status_code=404, detail="The scheduled date/time can't be less than or equal to the current date/time")

    scheduled_time = schedule_at - datetime.now()
    scheduled_time_in_secs = int(round(scheduled_time.total_seconds()))
    time.sleep(scheduled_time_in_secs)
    send_email(email_details=email_details,
               background_tasks=background_tasks, template=template, db=db)
    return {"message": "Scheduled Marketing Email will be sent in the background"}


#=================================== EMAIL SERVICES =================================#
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_TLS=False,
    MAIL_SSL=True,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=os.path.join(settings.TEMPLATE_FOLDER, "email")
)


def send_invite_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "invite_email.html",
    db: orm.Session = fastapi.Depends(get_db)
):

    send_email(email_details=email_details,
               background_tasks=background_tasks, template=template, db=db)
    return {"message": "Invite email will be sent in the background"}


def send_email(email_details: email_schema.Email, background_tasks: BackgroundTasks, template: str, db: orm.Session):
    date_created = datetime.now()
    message = MessageSchema(
        subject=email_details.subject,
        recipients=email_details.recipient,
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
            "receipt_id": email_details.receipt_id,
            "promo_product_name": email_details.promo_product_name,
            "promo_product_description": email_details.promo_product_description,
            "promo_product_price": email_details.promo_product_price,
            "product_name": email_details.product_name,
            "product_description": email_details.product_description,
            "product_price": email_details.product_price,
            "extra_product_name": email_details.extra_product_name,
            "extra_product_description": email_details.extra_product_description,
            "extra_product_price": email_details.extra_product_price,
            "sender_address": email_details.sender_address,
            "sender_city": email_details.sender_city,
            "sender_state": email_details.sender_state,
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
        amount=email_details.amount,
        due_date=email_details.due_date,
        link=email_details.link,
        extra_link=email_details.extra_link,
        invoice_id=email_details.invoice_id,
        receipt_id=email_details.receipt_id,
        description=email_details.description,
        promo_product_name=email_details.promo_product_name,
        promo_product_description=email_details.promo_product_description,
        promo_product_price=email_details.promo_product_price,
        product_name=email_details.product_name,
        product_description=email_details.product_description,
        product_price=email_details.product_price,
        extra_product_name=email_details.extra_product_name,
        extra_product_description=email_details.extra_product_description,
        extra_product_price=email_details.extra_product_price,
        sender_address=email_details.sender_address,
        sender_city=email_details.sender_city,
        sender_state=email_details.sender_state,
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
            subject=title,
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
            subject=title,
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


async def send_email_debts(email: str, user, template, title: str, amount=int, due_date="", description="", date="", invoice_id=str, email_message="", business_name=""):

    message = MessageSchema(
        subject=title,
        recipients=[email],
        template_body={
            "title": title,
            "first_name": user.first_name,
            "amount": amount,
            "due_date": due_date,
            "description": description,
            "date": date,
            "invoice_id": invoice_id,
            "email_message": email_message,
            "business_name": business_name
        },
        subtype="html",
    )
    fm = FastMail(conf)

    return await fm.send_message(message, template)
