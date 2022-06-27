from uuid import uuid4
import datetime as datetime
from sqlalchemy import ForeignKey
import bigfastapi.db.database as db
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Table
from sqlalchemy.types import String, DateTime, JSON, Boolean
from sqlalchemy.sql import func




class LPage(db.Base):
  __tablename__ = 'landing_page'
  id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
  user_id = Column(String(255), ForeignKey("users.id"))
  landing_page_name = Column(String(255), index=True, unique=True)
  other_info = relationship("OtherInfo", back_populates="landing_page_data")
  date_created = Column(DateTime, server_default=func.now())
  last_updated = Column(DateTime, nullable=False,
                        server_default=func.now(), onupdate=func.now())


class OtherInfo(db.Base):
  __tablename__ = "landing_info"
  id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
  landing_page_id = Column(String(255), ForeignKey("landing_page"))
  key = Column(String(255), index=True, default="")
  value = Column(String(255), index=True, default="")
  landing_page_data = relationship("LPage", back_populates="other_info")
  date_created = Column(DateTime, server_default=func.now())
  last_updated = Column(DateTime, nullable=False,
                        server_default=func.now(), onupdate=func.now())