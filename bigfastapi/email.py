from bigfastapi.utils import settings as settings
from .models import user_models
from uuid import uuid4
from .auth import create_passwordreset_token, create_verification_token
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from .auth import create_forgot_pasword_code, create_verification_code
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Response
from pydantic import BaseModel
from fastapi_mail import FastMail, MessageSchema
from bigfastapi.schemas.email_schema import InvoiceMail, ReceiptMail
from bigfastapi.db.database import get_db
import sqlalchemy.orm as orm
import fastapi
from uuid import uuid4
from .models import email_models as trans_models
from .schemas import email_schema
from typing import Optional


app = APIRouter(tags=["Transactional Emails 📧"])

class ResponseModel(BaseModel):
    message: str

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


async def get_user_by_email(email: str, db: orm.Session):
    return db.query(user_models.User).filter(user_models.User.email == email).first()



async def send_code_password_reset_email(email: str, db: orm.Session, codelength:int=None):
    user = await get_user_by_email(email, db)
    if user:
        code = await create_forgot_pasword_code(user, codelength)
        message = MessageSchema(
            subject="Password Reset",
            recipients=[email],
            template_body={
                "title": "Change your password",
                "first_name": user.first_name,
                "code": code["code"],
            },
            subtype="html",
        )
        await send_email_async(message, settings.PASSWORD_RESET_TEMPLATE)
        return {"code": code["code"]}
    else:
        raise fastapi.HTTPException(status_code=401, detail="Email not registered")

async def resend_code_verification_mail(email: str, db: orm.Session, codelength:int=None):
    user = await get_user_by_email(email, db)
    if user:
        code = await create_verification_code(user, codelength)
        message = MessageSchema(
            subject="Email Verification",
            recipients=[email],
            template_body={
                "title": "Verify Your Account",
                "first_name": user.first_name,
                "code": code["code"],
            },
            subtype="html",
        )
        await send_email_async(message, settings.EMAIL_VERIFICATION_TEMPLATE)
        return {"code": code["code"]}
    else:
        raise fastapi.HTTPException(status_code=401, detail="Email not registered")


async def send_token_password_reset_email(email: str,redirect_url: str, db: orm.Session):
    user = await get_user_by_email(email, db)
    if user:
        token = await create_passwordreset_token(user)
        path = "{}/?token={}".format(redirect_url, token["token"])
        message = MessageSchema(
            subject="Password Reset",
            recipients=[email],
            template_body={
                "title": "Change you",
                "first_name": user.first_name,
                "path": path,
            },
            subtype="html",
        )
        await send_email_async(message, settings.PASSWORD_RESET_TEMPLATE)
        return {"token": token}
    else:
        raise fastapi.HTTPException(status_code=401, detail="Email not registered")



async def resend_token_verification_mail(email: str,redirect_url: str, db: orm.Session):
    user = await get_user_by_email(email, db)
    if user:
        token = await create_verification_token(user)
        path = "{}/?token={}".format(redirect_url, token["token"])
        message = MessageSchema(
            subject="Email Verification",
            recipients=[email],
            template_body={
                "title": "Verify Your Account",
                "first_name": user.first_name,
                "path": path,
            },
            subtype="html",
        )
        await send_email_async(message, settings.EMAIL_VERIFICATION_TEMPLATE)
        return {"token": token}
    else:
        raise fastapi.HTTPException(status_code=401, detail="Email not registered")


async def send_email_async(message: MessageSchema, template: str):
    fm = FastMail(conf)
    await fm.send_message(message, template_name=template)


# def send_email_background(
#     background_tasks: BackgroundTasks, message: MessageSchema, template: str
# ):
#     fm = FastMail(conf)
#     background_tasks.add_task(fm.send_message, message, template_name="email.html")




def send_email_background(
    background_tasks: BackgroundTasks, message: MessageSchema, template: str
):
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message, template_name=template)



@app.post('/email/send', response_model=ResponseModel)
def send_email(email_details: email_schema.Email, background_tasks: BackgroundTasks, template: Optional[str] = "base.html", db: orm.Session = fastapi.Depends(get_db)):
    date_created = datetime.now()
    message = MessageSchema(
        subject= email_details.subject,
        recipients= [email_details.recipient],
        template_body={
            "title": email_details.title,
            "first_name": email_details.first_name,
            "body": email_details.body,
            "date_created": date_created, 
        },
        subtype="html",
    )

    email = trans_models.Email(
        id = uuid4().hex,
        subject = email_details.subject,
        recipient = email_details.recipient,
        title = email_details.title, 
        first_name = email_details.first_name,
        body = email_details.body,
        date_created = date_created
        )
    db.add(email)
    db.commit()
    db.refresh(email)

    send_email_background(background_tasks=background_tasks, message=message, template=template)
    return {"message": "Email will be sent in the background"}

@app.post('/email/send/invoice', response_model=ResponseModel)
def send_invoice_mail(invoice_details: InvoiceMail, background_tasks: BackgroundTasks, template: Optional[str] = "invoice_email.html", db: orm.Session = fastapi.Depends(get_db)):
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

    send_email_background(background_tasks=background_tasks, message=message, template=template)
    return {"message": "Invoice Email will be sent in the background"}

@app.post('/email/send/receipt', response_model=ResponseModel)
def send_receipt_mail(receipt_details: ReceiptMail, background_tasks: BackgroundTasks, template: Optional[str] ="receipt_email.html",  db: orm.Session = fastapi.Depends(get_db)):
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

    send_email_background(background_tasks=background_tasks, message=message, template=template)
    return {"message": "Receipt Email will be sent in the background"}