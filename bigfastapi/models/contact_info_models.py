from sqlalchemy.types import String, DateTime, Boolean
from sqlalchemy.sql import func
from bigfastapi.db.database import Base
from uuid import uuid4
from sqlalchemy.schema import Column


class ContactInfo(Base):
    __tablename__ = "contact_info"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    # rel_id = Column(String(255), index=True)
    # model_type = Column(String(255))
    contact_data = Column(String(255), nullable=False)
    contact_tag = Column(String(255))
    contact_type = Column(String(255), nullable=False)
    contact_title = Column(String(255))
    phone_country_code = Column(String(255))
    is_primary  = Column(Boolean,  default=False)
    is_deleted = Column(Boolean,  default=False)
    description = Column(String(255), default="")
    date_created  = Column(DateTime, server_default=func.now())
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    date_created_db = Column(DateTime, nullable=False, server_default=func.now())
    last_updated_db = Column(DateTime, nullable=False,
                          server_default=func.now(), onupdate=func.now())