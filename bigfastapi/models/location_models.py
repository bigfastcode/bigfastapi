from sqlalchemy.types import String, DateTime, Boolean
from sqlalchemy.sql import func
from bigfastapi.db.database import Base
from uuid import uuid4
from sqlalchemy.schema import Column


class Location(Base):
    __tablename__ = "locations"

    id = Column(String(50), primary_key=True, index=True, default=uuid4().hex)
    country = Column(String(255))
    state = Column(String(255))
    city = Column(String(255))
    county = Column(String(255))
    zip_code = Column(String(255))
    full_address = Column(String(255))
    street = Column(String(255))
    significant_landmark = Column(String(255))
    driving_instructions = Column(String(255))
    longitude = Column(String(255))
    latitude = Column(String(255))
    is_deleted = Column(Boolean,  default=False)
    date_created  = Column(DateTime, server_default=func.now())
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    date_created_db = Column(DateTime, nullable=False, server_default=func.now())
    last_updated_db = Column(DateTime, nullable=False,
                          server_default=func.now(), onupdate=func.now())