from uuid import uuid4

from sqlalchemy.schema import Column
from sqlalchemy.types import String, Float

import bigfastapi.db.database as _database


class CreditWalletConversion(_database.Base):
    __tablename__ = "credit_wallet_conversions"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    credit_wallet_type = Column(String(255), default='bfacredit')
    rate = Column(Float, default=0)
    currency_code = Column(String(4))
