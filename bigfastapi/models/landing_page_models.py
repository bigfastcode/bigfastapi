
from uuid import uuid4
import datetime as datetime
from sqlalchemy import ForeignKey
import bigfastapi.db.database as db
import sqlalchemy.orm as orm
from sqlalchemy.schema import Column, Table
from sqlalchemy.types import String, DateTime, JSON





class LPage(db.Base):
  __tablename__ = 'landing_page'
  id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
  user_id = Column(String(255), ForeignKey("users.id"))
  landing_page_name = Column(String(255), index=True, unique=True)
  content = Column('data', JSON)
  date_created = Column(DateTime, default=datetime.datetime.utcnow)
  last_updated = Column(DateTime, default=datetime.datetime.utcnow)


