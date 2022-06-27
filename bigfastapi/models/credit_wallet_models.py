import datetime as _dt
from uuid import uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Float

import bigfastapi.db.database as database


class CreditWallet(database.Base):
    __tablename__ = "credit_wallets"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), ForeignKey("organizations.id"))
    amount = Column(Float, default=0)
    type = Column(String(255), default='bfacredit')
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)


class CreditWalletHistory(database.Base):
    __tablename__ = "credit_wallet_history"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    credit_wallet_id = Column(String(255), ForeignKey("credit_wallets.id"))
    amount = Column(Float, default=0)
    date = Column(DateTime, default=_dt.datetime.utcnow)
    reference = Column(String(255), default='')


class CreditWalletConversion(database.Base):
    __tablename__ = "credit_wallet_conversions"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    credit_wallet_type = Column(String(255), default='bfacredit')
    rate = Column(Float, default=0)
    currency_code = Column(String(4))
