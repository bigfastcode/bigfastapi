from sqlalchemy.types import String, DateTime, Text, Integer, JSON, Boolean
from sqlalchemy import ForeignKey, text
from sqlalchemy.sql import func
from bigfastapi.db.database import Base
from uuid import uuid4
from sqlalchemy.schema import Column


from bigfastapi.utils.utils import generate_short_id


class Customer(Base):
    __tablename__ = "customers"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    customer_id = Column(String(255), index=True, default=generate_short_id(size=12))
    organization_id = Column(String(255), ForeignKey("businesses.id"))
    email = Column(String(255), index=True,  default="")
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    phone_number = Column(String(255), index=True, default="")
    address = Column(Text(), index=True,  default="")
    gender = Column(String(255), index=True, default="")
    age = Column(Integer, index=True, default=0)
    postal_code = Column(String(255), index=True, default="")
    language = Column(String(255), index=True, default="")
    country = Column(String(255), index=True, default="")
    city = Column(String(255), index=True, default="")
    region = Column(String(255), index=True, default="")
    country_code= Column(String(255), index=True, default="")
    other_information = Column(JSON, index=True, default=text("'null'"))
    is_deleted = Column(Boolean,  index=True, default=False)
    date_created = Column(DateTime, server_default=func.now())
    last_updated = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    

