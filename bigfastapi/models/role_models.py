import datetime as dt
from re import T
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime
from uuid import UUID, uuid4
import bigfastapi.db.database as database

class Role(database.Base):
    __tablename__ = "roles"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), index=True)
    role_name = Column(String(255), index=True)