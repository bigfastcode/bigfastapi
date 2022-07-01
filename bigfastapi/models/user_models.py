
import datetime as datetime
import passlib.hash as _hash
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Boolean, Text
from uuid import uuid4
from sqlalchemy.sql import func
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE
from bigfastapi.db.database import Base



class User(Base):
    __tablename__ = "users"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    email = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    phone_number = Column(String(50))
    phone_country_code = Column(String(7))
    # country_code = Column(String(10))
    # state_code =  Column(String(10))
    # county_code = Column(String(10))
    # address = Column(Text())
    password_hash = Column(Text(), nullable=False)
    image_url = Column(Text())
    device_id = Column(Text())
    google_id = Column(String(255))
    google_image_url = Column(Text())
    is_deleted = Column(Boolean, index = True, default=False)
    is_active = Column(Boolean)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    date_created_db = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated_db = Column(DateTime, default=datetime.datetime.utcnow)

    def verify_password(self, password: str):
        return _hash.sha256_crypt.verify(password, self.password_hash)
