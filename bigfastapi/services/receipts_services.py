from base64 import encode
from datetime import datetime
import os
from fastapi import Depends, HTTPException
from fastapi.responses import FileResponse

import sqlalchemy.orm as orm
from sqlalchemy import and_, desc

from bigfastapi.utils import settings


from ..models.receipt_models import Receipt
from ..models.file_models import File
from ..schemas import receipt_schemas
from bigfastapi import pdfs
from ..db.database import get_db


async def get_receipts(
    organization_id: str,
    offset: int, 
    size: int = 50,
    datetime_constraint: datetime = None,
    sort_dir:str = "desc",
    sorting_key: str = "date_created",
    db: orm.Session = Depends(get_db)
    ):

    total_items =  (
            db.query(Receipt)
                .filter(
                    Receipt.organization_id == organization_id)
                .count()
            )
    receipts = db.query(Receipt).filter(and_(Receipt.organization_id == organization_id, Receipt.is_deleted == False))

    if datetime_constraint:
            receipts = ( 
                receipts
                .filter(
                    Receipt.last_updated > datetime_constraint
                    )
                .order_by(Receipt.date_created.desc())
                .offset(offset=offset)
                .limit(limit=size)
                .all()
                )
            total_items = db.query(Receipt).filter(and_(
                    Receipt.organization_id == organization_id,
                    Receipt.last_updated > datetime_constraint
                    )).count()
    elif sort_dir == "desc":
        receipts= receipts.order_by(
            desc(getattr(Receipt, sorting_key, "date_created"))
            ).offset(offset=offset).limit(limit=size).all()

    else:
        receipts = ( 
            receipts
            .order_by(Receipt.date_created.desc())
            .offset(offset=offset)
            .limit(limit=size)
            .all()
            )
    return (receipts, total_items)


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

async def get_receipt_by_id(receipt_id:str, org_id: str, db: orm.Session = Depends(get_db)):
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id, Receipt.organization_id == org_id).first()
    if not receipt:
        return None
    return receipt_schemas.Receipt.from_orm(receipt)


def convert_to_pdf(pdfSchema, db: orm.Session = Depends(get_db)):
    return pdfs.convert_to_pdf(pdfSchema, db=db)

def get_file(bucket_name: str, file_id: str, db: orm.Session = Depends(get_db)):

    """Download a single file from the storage

    Args:
        bucket_name (str): the bucket to list all the files.
        file_name (str): the file that you want to retrieve

    Returns:
        A stream of the file
    """

    existing_file = db.query(File).filter(and_(File.bucketname == bucket_name, File.id == file_id)).first()
    if existing_file:
        local_file_path = os.path.join(os.path.realpath(settings.FILES_BASE_FOLDER), existing_file.bucketname, existing_file.filename)

        common_path = os.path.commonpath((os.path.realpath(settings.FILES_BASE_FOLDER), local_file_path))
        if os.path.realpath(settings.FILES_BASE_FOLDER) != common_path:
            raise HTTPException(status_code=403, detail="File reading from unallowed path")

        return FileResponse(local_file_path, media_type='application/octet-stream',filename=existing_file.filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")
