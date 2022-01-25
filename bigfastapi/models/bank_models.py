from markupsafe import string
from sqlalchemy import func
import bigfastapi.db.database as database
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime
from uuid import uuid4



class   Bank(database.Base):
    __tablename__ = "Banks"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    account_number = Column(Integer)
    bank_name = Column(String)
    account_name = Column(String)   
    bank_sort_code = Column(String) 
    country = Column(String)
    creator_id = Column(String)
    created_by = Column(String)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    