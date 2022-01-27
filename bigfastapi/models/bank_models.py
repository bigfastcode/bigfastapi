from markupsafe import string
from sqlalchemy import func, ForeignKey
import bigfastapi.db.database as database
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime
from uuid import uuid4
from bigfastapi.db import database


class   BankDetails(database.Base):
    __tablename__ = "bank_details"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organisation_id = Column(String, index=True)
    creator_id = Column(String)
    account_number = Column(Integer, unique=True, index=True)
    bank_name = Column(String, index=True)
    account_name = Column(String, index=True, default=None)  
    country = Column(String, index=True) 
    sort_code = Column(String, index=True, default=None) 
    swift_code= Column(String, index=True,  default=None)
    address= Column(String, index=True, default=None)
    postcode= Column(String, index=True, default=None)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    
