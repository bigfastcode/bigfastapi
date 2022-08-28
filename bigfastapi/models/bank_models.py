from uuid import uuid4
from sqlalchemy import func, ForeignKey
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime, Boolean
from bigfastapi.db.database import Base



class BankModels(Base):
    __tablename__ = "banks"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), ForeignKey("organizations.id"))
    creator_id = Column(String(255))
    account_number = Column(Integer, index=True)
    bank_name = Column(String(255))
    recipient_name = Column(String(255), index=True, default=None)
    recipient_address = Column(String(255), index=True, default=None)
    country = Column(String(255), index=True)
    currency = Column(String(255))
    frequency = Column(String(255), default=None)
    sort_code = Column(String(255), index=True, default=None)
    swift_code = Column(String(255), index=True, default=None)
    bank_address = Column(String(255), index=True, default=None)
    bank_type = Column(String(255), index=True, default=None)
    account_type = Column(String(255), index=True, default=None)
    aba_routing_number = Column(String(255), index=True, default=None)
    iban = Column(String(255), index=True, default=None)
    is_preferred = Column(Boolean(), default=False)
    is_deleted = Column(Boolean(), default=False)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    date_created_db = Column(DateTime(timezone=True), server_default=func.now())
    last_updated_db = Column(DateTime(timezone=True), server_default=func.now())

