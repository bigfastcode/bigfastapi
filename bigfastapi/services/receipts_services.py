from base64 import encode
from datetime import datetime
import fastapi, os
from fastapi import Depends
import sqlalchemy.orm as orm
from sqlalchemy import and_, desc

from ..models.receipt_models import Receipt
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
                .filter(and_(
                    Receipt.organization_id == organization_id,
                    Receipt.last_updated > datetime_constraint
                    ))
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
            .filter(Receipt.organization_id == organization_id)
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
    receipt = db.query(Receipt).filter(and_(
             Receipt.id == receipt_id, Receipt.organization_id == org_id)
            ).first()
    if not receipt:
        return None
    return receipt_schemas.Receipt.from_orm(receipt)


def convert_to_pdf(pdfSchema, db: orm.Session = Depends(get_db)):
    return pdfs.convert_to_pdf(pdfSchema, db=db)