from uuid import uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer

import bigfastapi.db.database as database


class Settings(database.Base):
    __tablename__ = "settings"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    org_id = Column(String(255), ForeignKey("businesses.id"))
    location = Column(String(255), index=True, nullable=True)
    phone_number = Column(String(255), index=True, nullable=True)
    email = Column(String(255), index=True, nullable=True)
    organization_size = Column(String(255), index=True)
    organization_type = Column(String(255), index=True)
    country = Column(String(255), index=True)
    state = Column(String(255), index=True)
    city = Column(String(255), index=True)
    zip_code = Column(Integer, index=True)


# App Settings
class AppSetting(database.Base):
    __tablename__ = "app_settings"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    name = Column(String(255), unique=True)
    value = Column(String(255), default='')
