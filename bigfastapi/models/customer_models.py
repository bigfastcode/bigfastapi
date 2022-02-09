from sqlalchemy.types import String, DateTime, Text, Integer
from sqlalchemy import ForeignKey
from bigfastapi.db.database import Base
from uuid import uuid4
from sqlalchemy.schema import Column
import datetime as dt
from sqlalchemy.orm import relationship

from bigfastapi.utils.utils import generate_short_id


class Customer(Base):
    __tablename__ = "customer"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    customer_id = Column(String(255), index=True, default=generate_short_id(size=12))
    organization_id = Column(String(255), ForeignKey("businesses.id"))
    email = Column(String(255), unique=True, index=True)
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    phone_number = Column(String(255), index=True, default="")
    address = Column(Text(), index=True)
    gender = Column(String(255), index=True, default="")
    age = Column(Integer, index=True, default=0)
    postal_code = Column(String(255), index=True, default="")
    language = Column(String(255), index=True, default="")
    country = Column(String(255), index=True, default="")
    city = Column(String(255), index=True, default="")
    region = Column(String(255), index=True, default="")
    country_code= Column(String(255), index=True, default="")
    date_created = Column(DateTime, default=dt.datetime.utcnow)
    last_updated = Column(DateTime, default=dt.datetime.utcnow)
    debt = relationship("Debt", back_populates="customer", uselist=False)