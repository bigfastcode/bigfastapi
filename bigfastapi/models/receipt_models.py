import datetime as _dt
from uuid import uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column
from sqlalchemy.types import BOOLEAN, DateTime, String, Text

import bigfastapi.db.database as _database


class Receipt(_database.Base):
    __tablename__ = "receipts"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), index=True)
    sender_email = Column(String(255), index=True)
    message = Column(Text(), index=True)
    subject = Column(String(255), index=True)
    recipient = Column(String(255), index=True)
    file_id = Column(String(255), ForeignKey("files.id"), default=None)
    is_deleted = Column(BOOLEAN, index=True, default=False)
    date_created = Column(DateTime, default=_dt.datetime.now())
    last_updated = Column(DateTime, default=_dt.datetime.now())
    date_created_db = Column(DateTime, default=_dt.datetime.now())
    last_updated_db = Column(DateTime, default=_dt.datetime.now())
