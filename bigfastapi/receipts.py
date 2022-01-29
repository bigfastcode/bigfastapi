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
from .models import file_models as file_model
from .models import receipt_models as receiptmodel
from uuid import uuid4
from fastapi import BackgroundTasks
from bigfastapi.utils import settings
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import Optional

app = APIRouter()


#send receipt endpoint
@app.post("/sendreceipt")
def sendReceipt(body: receipt_schemas.atrributes, background_tasks: BackgroundTasks, db: orm.Session = Depends(get_db)):
    #define pdf schema
    pdfname = (body.subject)+str(random.randint(3,8))+".pdf"
    
    pdfSchema = {
            "htmlString": body.message,
            "pdfName": pdfname
    }
    
    #convert receipt message to pdf
    fileresponse = convertToPdf(pdf_schema.Format(**pdfSchema), db=db)
    #save to db
    saveReceiptDetails(body.sender, fileresponse.id, db)
    
    #send mail
    send_email(body, background_tasks=background_tasks, template="email/mail_receipt.html", db=db, file="./filestorage/pdfs/"+pdfname)
    #save to db

    return responseMessage()

#response message
def responseMessage():
    return {'message' : "receipt sent"}

#convert to pdf
def convertToPdf(pdfSchema, db: orm.Session = Depends(get_db)):
    return pdfs.convertToPdf(pdfSchema, db=db) 

#save deatisl to db
def saveReceiptDetails(sender, file_id, db):
    # Create a db entry for this recepit. 
    receipt = receiptmodel.Receipt(id=uuid4().hex, sender_email=sender, file_id=file_id)
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return

#send mail
def send_email(
    email_details,
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

    return

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