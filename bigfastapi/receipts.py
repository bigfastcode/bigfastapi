from base64 import encode
import fastapi, os
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi import APIRouter
from fastapi import UploadFile, File
from sqlalchemy import and_, null

from bigfastapi.models import file_models
from bigfastapi.models.organisation_models import Organization
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
from .models.receipt_models import Receipt
from uuid import uuid4
from fastapi import BackgroundTasks
from bigfastapi.utils import paginator, settings
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import Optional

app = APIRouter()


#send receipt endpoint
@app.post("/receipts", status_code=201, response_model=receipt_schemas.ResponseModel)
def send_receipt(payload: receipt_schemas.atrributes, background_tasks: BackgroundTasks, db: orm.Session = Depends(get_db)):

    """
        An endpoint to send receipts. 
        Note: The message field in the payload should be HTML formatted.
    """
    try: 

        pdf_name = (payload.subject)+str(uuid4().hex)+".pdf"
        

        schema = {
                "htmlString": payload.message,
                "pdfName": pdf_name
        }
        
        receipt = Receipt(
            id=uuid4().hex, 
            sender_email=payload.sender, 
            recipient=payload.recipient[0],
            subject=payload.subject,
            message=payload.message,
            organization_id=payload.organization_id
            )
        file = convert_to_pdf(pdf_schema.Format(**schema), db=db)

        receipt.file_id = file.id
        db.add(receipt)
        db.commit()
        db.refresh(receipt)
        
        send_receipt_email(payload, background_tasks=background_tasks, template="email/mail_receipt.html", db=db, file="./filestorage/pdfs/"+pdf_name)

        return JSONResponse({"message" : "receipt sent"}, status_code=status.HTTP_201_CREATED)

    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))

@app.get("/receipts", status_code=200)
async def fetch_receipts(
    organization_id:str,
    search_value: str = None,
    sorting_key: str = None,
    page: int = 1, 
    size: int = 50, 
    db: orm.Session = Depends(get_db)):

    """
        An endpoint to fetch all receipts. 
        Note: The message field in the payload should be HTML formatted.
    """
    # FETCH RECEIPT FROM DB.
    try:
        page_size = 50 if size < 1 or size > 100 else size
        page_number = 1 if page <= 0 else page
        offset = await paginator.off_set(page=page_number, size=page_size)
        total_items =  (
            db.query(Receipt)
                .filter(
                    Receipt.organization_id == organization_id)
                .count()
            )
        pointers = await paginator.page_urls(page=page, size=page_size, 
            count=total_items, endpoint=f"/receipts")
        organization = db.query(Organization).filter(Organization.id == organization_id).first()
        if not organization:
            return JSONResponse({"message": "Organization does not exist"}, status_code=status.HTTP_404_NOT_FOUND)
        if search_value:
            receipts, total_items = await search_receipts(organization_id=organization_id, 
                search_value=search_value, offset=offset, size=page_size, db=db)
        else:
            receipts = ( 
                db.query(Receipt)
                .filter(Receipt.organization_id == organization_id)
                .order_by(Receipt.date_created.desc())
                .offset(offset=offset)
                .limit(limit=size)
                .all()
                )
        response = {"page": page_number, "size": page_size, "total": total_items,
            "previous_page":pointers['previous'], "next_page": pointers["next"], "items": receipts}
        return response
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            , detail=str(ex))






#SERVICES
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


def convert_to_pdf(pdfSchema, db: orm.Session = Depends(get_db)):
    return pdfs.convert_to_pdf(pdfSchema, db=db) 

async def search_receipts(
    organization_id:str,
    search_value: str,
    offset: int, size:int=50,
    db: orm.Session = Depends(get_db)
    ):  
    search_text = f"%{search_value}%"
    search_result_count =db.query(Receipt).filter(and_(
        Receipt.organization_id == organization_id,
        Receipt.recipient.like(search_text))).count()

    receipts_by_recipient = db.query(Receipt).filter(and_(
        Receipt.organization_id == organization_id,
        Receipt.recipient.like(search_text))
        ).offset(
        offset=offset).limit(limit=size).all()


    recipient_list = [*receipts_by_recipient]
    return (recipient_list, search_result_count)


# async def sort_receipts(
#     organization_id:str,
#     sort_key: str,
#     offset: int, size:int=50,
#     sort_dir: str = "asc",
#     db:Session = Depends(get_db)
#     ):  
#     if sort_dir == "desc":
#         customers = db.query(Customer).filter(
#             Customer.organization_id == organization_id).filter(
#             Customer.is_deleted == False).filter(
#             Customer.is_inactive == False).order_by(
#             desc(getattr(Customer, sort_key, "first_name"))
#             ).offset(offset=offset).limit(limit=size).all()
#     else:
#         customers = db.query(Customer).filter(
#             Customer.organization_id == organization_id).filter(
#             Customer.is_deleted == False).filter(
#             Customer.is_inactive != True).order_by(
#             getattr(Customer, sort_key, "first_name")
#             ).offset(offset=offset).limit(limit=size).all()

#     return list(map(customer_schemas.Customer.from_orm, customers))
