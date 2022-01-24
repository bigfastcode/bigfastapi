import datetime as dt

from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Text
from uuid import uuid4
import bigfastapi.db.database as database


class Email(database.Base):
    __tablename__ = "email"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    subject = Column(String(255), index=True)
    recipient = Column(String(255), index=True)
    title = Column(String(255), index=True)
    first_name = Column(String(255), index=True)
    body = Column(Text(), index=True)
    date_created = Column(DateTime, default=dt.datetime.utcnow)


class InvoiceMail(database.Base):
    __tablename__ = "invoicemail"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    subject = Column(String(255), index=True)
    recipient = Column(String(255), index=True)
    title = Column(String(255), index=True)
    first_name = Column(String(255), index=True)
    amount = Column(String(255), index=True)
    due_date = Column(String(255), index=True)
    payment_link = Column(String(255), index=True)
    invoice_id = Column(String(255), index=True)
    description = Column(String(255), index=True)
    date_created = Column(DateTime, default=dt.datetime.utcnow)


class ReceiptMail(database.Base):
    __tablename__ = "receiptemail"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    subject = Column(String(255), index=True)
    recipient = Column(String(255), index=True)
    title = Column(String(255), index=True)
    first_name = Column(String(255), index=True)
    amount = Column(String(255), index=True)
    receipt_id = Column(String(255), index=True)
    description = Column(String(255), index=True)
    date_created = Column(DateTime, default=dt.datetime.utcnow)
