import datetime as dt

from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Text, PickleType
from sqlalchemy.ext.mutable import MutableList
from uuid import uuid4
import bigfastapi.db.database as database


class Email(database.Base):
    __tablename__ = "email"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    subject = Column(String(255), index=True)
    recipient = Column(MutableList.as_mutable(PickleType), default=[])
    title = Column(String(255), index=True)
    first_name = Column(String(255), index=True)
    body = Column(String(255), index=True, nullable=True, default=None)
    amount = Column(String(255), index=True, nullable=True, default=None)
    due_date = Column(String(255), index=True, nullable=True, default=None)
    link = Column(String(255), index=True, nullable=True, default=None)
    extra_link = Column(String(255), index=True, nullable=True, default=None)
    receipt_id = Column(String(255), index=True, nullable=True, default=None)
    invoice_id = Column(String(255), index=True, nullable=True, default=None)
    description = Column(String(255), index=True, nullable=True, default=None)
    sender = Column(String(255), index=True, nullable=True, default=None)
    promo_product_name = Column(String(255), index=True, nullable=True, default=None)
    promo_product_description = Column(String(255), index=True, nullable=True, default=None)
    promo_product_price = Column(String(255), index=True, nullable=True, default=None)
    product_name = Column(String(255), index=True, nullable=True, default=None)
    product_description = Column(String(255), index=True, nullable=True, default=None)
    product_price = Column(String(255), index=True, nullable=True, default=None)
    extra_product_name = Column(String(255), index=True, nullable=True, default=None)
    extra_product_description = Column(String(255), index=True, nullable=True, default=None)
    extra_product_price = Column(String(255), index=True, nullable=True, default=None)
    sender_address = Column(String(255), index=True)
    sender_city = Column(String(255), index=True)
    sender_state = Column(String(255), index=True)
    date_created = Column(DateTime, default=dt.datetime.utcnow)
