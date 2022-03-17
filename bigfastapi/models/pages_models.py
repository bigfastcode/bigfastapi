import bigfastapi.db.database as db
import datetime
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime
from uuid import uuid4


class Page(db.Base):
    __tablename__ = "pages"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    title = Column(String(255))
    content = Column(String(500))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
