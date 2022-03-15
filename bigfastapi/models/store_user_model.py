import datetime as dt
from re import T

from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Boolean
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4
import bigfastapi.db.database as database

class StoreUser(database.Base):
    __tablename__ = "store_users"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    store_id = Column(String(255), index=True)
    user_id = Column(String(255), ForeignKey("users.id"))
    role_id = Column(String(255), ForeignKey("roles.id"))
    is_deleted = Column(Boolean, default=False) 
    date_created = Column(DateTime, default=dt.datetime.utcnow)