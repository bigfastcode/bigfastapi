from sqlalchemy import func, ForeignKey, orm
import bigfastapi.db.database as database
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime
from uuid import uuid4
from bigfastapi.db import database
from bigfastapi.schemas import bank_schemas, users_schemas
from fastapi import  status
from fastapi.responses import JSONResponse


class   BankModels(database.Base):
    __tablename__ = "bank_models"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organisation_id = Column(String(255), ForeignKey("businesses.id"))
    creator_id = Column(String(255))
    account_number= Column(Integer, unique=True, index=True)
    bank_name = Column(String(255))
    account_name = Column(String(255), index=True, default=None)  
    country = Column(String(255), index=True) 
    sort_code = Column(String(255), index=True, default=None) 
    swift_code= Column(String(255), index=True,  default=None)
    address= Column(String(255), index=True, default=None)
    bank_type= Column(String(255), index=True, default=None)
    aba_routing_number = Column(String(255), index=True, default=None)
    iban= Column(String(255), index=True, default=None)
    date_created = Column(DateTime(timezone=True), server_default=func.now())



#===========================database query service===================================================

async def fetch_bank(user: users_schemas.User, id: str, db: orm.Session):
    bank = db.query(BankModels).filter(BankModels.id == id).first()
    if not bank:
        return JSONResponse({"This bank detail does not exist here"}, 
                    status_code=status.HTTP_403_FORBIDDEN) 
    return bank

async def add_bank(user: users_schemas.User, addbank: str, db: orm.Session):
    db.add(addbank)
    db.commit()
    db.refresh(addbank)
    
    return bank_schemas.BankResponse.from_orm(addbank) 
    
