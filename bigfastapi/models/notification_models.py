from datetime import datetime
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, PickleType, Boolean
from uuid import uuid4
import bigfastapi.db.database as database
from sqlalchemy.ext.mutable import MutableList

class Notification(database.Base):
    __tablename__ = "notifications"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    creator = Column(String(100), index=True)
    content = Column(String(255), index=True)
    has_read = Column(Boolean, default=False)
    reference = Column(String(100), index=True)
    recipient = Column(String(255), index=True)
    # recipients = Column(MutableList.as_mutable(PickleType), default=[])
    date_created = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)