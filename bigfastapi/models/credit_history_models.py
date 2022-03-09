import datetime as _dt
from uuid import uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Float

from bigfastapi.db.database import Base


class CreditHistory(Base):
    __tablename__ = "credit_history"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    credit_wallet_id = Column(String(255), ForeignKey("credit_wallets.id"))
    amount = Column(Float, default=0)
    date = Column(DateTime, default=_dt.datetime.utcnow)
    reference = Column(String(255), default='')
