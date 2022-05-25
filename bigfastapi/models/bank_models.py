from uuid import uuid4

from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy import func, ForeignKey, orm
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime, Boolean

from bigfastapi.db import database
from bigfastapi.schemas import bank_schemas, users_schemas
from bigfastapi.schemas.bank_schemas import AddBank

from bigfastapi.db.database import Base



class BankModels(Base):
    __tablename__ = "banks"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organisation_id = Column(String(255), ForeignKey("businesses.id"))
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


# ===========================database query service===================================================

async def fetch_bank(user: users_schemas.User, id: str, db: orm.Session):
    bank = db.query(BankModels).filter(BankModels.id == id).first()
    if not bank:
        return JSONResponse({"Bank does not exist"},
                            status_code=status.HTTP_403_FORBIDDEN)
    return bank


async def add_bank(user: users_schemas.User, addbank: str, db: orm.Session):
    db.add(addbank)
    db.commit()
    db.refresh(addbank)

    return bank_schemas.BankResponse.from_orm(addbank)


async def update_bank(addBank: AddBank, db: orm.Session):
    db.commit()
    db.refresh(addBank)

    return bank_schemas.BankResponse.from_orm(addBank)
