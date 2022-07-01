from sqlalchemy.types import String, DateTime, Boolean
from sqlalchemy.sql import func
from bigfastapi.db.database import Base
from uuid import uuid4
from sqlalchemy.schema import Column


class ExtraInfo(Base):
    __tablename__ = "extra_info"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    rel_id = Column(String(255))
    model_type = Column(String(255))
    key = Column(String(255), nullable=False)
    value = Column(String(255), default="")
    value_dt =   Column(DateTime, default=None)
    description = Column(String(255), default="")
    is_primary = Column(Boolean,  default=False)
    is_deleted  = Column(Boolean, default=False)
    date_created  = Column(DateTime, server_default=func.now())
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    date_created_db = Column(DateTime, nullable=False, server_default=func.now())
    last_updated_db = Column(DateTime, nullable=False,
                          server_default=func.now(), onupdate=func.now())






