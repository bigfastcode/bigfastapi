import datetime as _dt
from uuid import uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Float

import bigfastapi.db.database as _database


class CreditWallet(_database.Base):
    __tablename__ = "credit_wallets"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), ForeignKey("businesses.id"))
    amount = Column(Float, default=0)
    type = Column(String(255), default='bfacredit')
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)