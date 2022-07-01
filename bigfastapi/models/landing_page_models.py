from uuid import uuid4

from sqlalchemy import ForeignKey
import bigfastapi.db.database as db
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime
from sqlalchemy.sql import func




class LandingPage(db.Base):
  __tablename__ = 'landing_page'
  id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
  user_id = Column(String(255), ForeignKey("users.id"))
  landing_page_name = Column(String(255), index=True, unique=True)
  bucket_name = Column(String(255),)
  other_info = relationship("LandingPageOtherInfo", back_populates="landing_page_data")
  date_created = Column(DateTime, server_default=func.now())
  last_updated = Column(DateTime, nullable=False,
                        server_default=func.now(), onupdate=func.now())


class LandingPageOtherInfo(db.Base):
  __tablename__ = "landing_info"
  id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
  landing_page_id = Column(String(255), ForeignKey("landing_page.id"))
  key = Column(String(255), index=True, default="")
  value = Column(String(255), default="")
  landing_page_data = relationship("LandingPage", back_populates="other_info")
  date_created = Column(DateTime, server_default=func.now())
  last_updated = Column(DateTime, nullable=False,
                        server_default=func.now(), onupdate=func.now())