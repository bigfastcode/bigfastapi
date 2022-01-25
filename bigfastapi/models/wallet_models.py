import datetime as _dt
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Float
from sqlalchemy import ForeignKey
from uuid import uuid4
import bigfastapi.db.database as _database


class Wallet(_database.Base):
    __tablename__ = "wallets"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), ForeignKey("organizations.id"))
    balance = Column(Float, default=0)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)
