
import datetime
from uuid import uuid4
import bigfastapi.db.database as db
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Integer


class File(db.Base):
    __tablename__ = "files"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    filename = Column(String(255), index=True)
    bucketname = Column(String(255), index=True)
    filesize = Column(Integer, index=True)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

