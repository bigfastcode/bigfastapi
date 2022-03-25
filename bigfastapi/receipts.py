from base64 import encode
import fastapi, os
from fastapi import Depends, FastAPI, Request, status
from fastapi import APIRouter
from fastapi import UploadFile, File
from sqlalchemy import null
from .schemas import receipt_schemas
from .schemas import pdf_schema
from .schemas import file_schemas
from bigfastapi import pdfs
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import random
from fastapi.encoders import jsonable_encoder
from bigfastapi.db.database import get_db
import sqlalchemy.orm as orm
from .models import receipt_models as receiptmodel
from uuid import uuid4
from fastapi import BackgroundTasks
from bigfastapi.utils import settings
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import Optional

app = APIRouter()


#send receipt endpoint
@app.post("/receipt", status_code=201, response_model=receipt_schemas.ResponseModel)
def send_receipt(payload: receipt_schemas.atrributes, background_tasks: BackgroundTasks, db: orm.Session = Depends(get_db)):

    """
        An endpoint to send receipts. 
        Note: The message field in the payload should be HTML formatted.
    """
    pdf_name = (payload.subject)+str(uuid4().hex)+".pdf"
    

    schema = {
            "htmlString": payload.message,
            "pdfName": pdf_name
    }
    
    file = convert_to_pdf(pdf_schema.Format(**schema), db=db)

    save_receipt(payload.sender, file.id, db)
    
    send_receipt_email(payload, background_tasks=background_tasks, template="email/mail_receipt.html", db=db, file="./filestorage/pdfs/"+pdf_name)

    return JSONResponse({'message' : "receipt sent"}, status_code=status.HTTP_201_CREATED)

#convert to pdf
def convert_to_pdf(pdfSchema, db: orm.Session = Depends(get_db)):
    return pdfs.convert_to_pdf(pdfSchema, db=db) 

def save_receipt(sender, file_id, db):

    receipt = receiptmodel.Receipt(id=uuid4().hex, sender_email=sender, file_id=file_id)
    db.add(receipt)
    db.commit()
    db.refresh(receipt)


#send mail
def send_receipt_email(
    email_details: receipt_schemas.atrributes,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "mail_receipt.html",
    db: orm.Session = fastapi.Depends(get_db),
    file: UploadFile = File(...)
):

    message = MessageSchema(
        subject=email_details.subject,
        recipients=email_details.recipient,
        template_body={
            "message": email_details.message,
        },
        subtype="html",
        attachments=[file]
        
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message, template_name=template)


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
    TEMPLATE_FOLDER=settings.TEMPLATE_FOLDER,
)