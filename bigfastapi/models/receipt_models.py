import datetime as _dt
from re import T
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Text
from sqlalchemy import ForeignKey, and_
from uuid import uuid4
import bigfastapi.db.database as _database
import sqlalchemy.orm as orm
from fastapi import Depends
from bigfastapi.db.database import get_db



class Receipt(_database.Base):
    __tablename__ = "newreceipts"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), index=True)
    sender_email = Column(String(255), index=True)
    message = Column(Text, index=True)
    subject = Column(String(255), index=True)
    recipient = Column(String(255), index=True)
    file_id = Column(String(255), ForeignKey("files.id"))
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)



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
