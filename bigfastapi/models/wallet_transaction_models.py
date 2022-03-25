import datetime as _dt
from uuid import uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Float, Boolean

from bigfastapi.db.database import Base


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    wallet_id = Column(String(255), ForeignKey("wallets.id"))
    status = Column(Boolean, default=0)
    amount = Column(Float, default=0)
    currency_code = Column(String(4))
    transaction_date = Column(DateTime, default=_dt.datetime.utcnow)
    transaction_ref = Column(String(255), default='')
