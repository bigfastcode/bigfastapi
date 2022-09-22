import datetime as _dt
from uuid import uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Float, Boolean

from bigfastapi.db.database import Base


class Activitylog(Base):
    __tablename__ = "activity_logs"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255))
    user_id = Column(String(255))
    model_id = Column(String(255))
    created_for_id= Column(String(225))
    created_for_model=Column(String(225))
    object_url = Column(String(255),default='')
    model_name = Column(String(255))
    action = Column(String(255), default='')
    created_at = Column(DateTime, default=_dt.datetime.now())
    is_deleted = Column(Boolean, default=False)


