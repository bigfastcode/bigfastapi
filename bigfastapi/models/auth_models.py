import datetime as _dt
import passlib.hash as _hash
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Boolean
from sqlalchemy import ForeignKey
from uuid import uuid4
from ..utils.utils import gen_max_age
from bigfastapi.db import database

class PasswordResetCode(database.Base):
    __tablename__ = "password_reset_codes"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    code = Column(String(255), index=True, unique=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)


class Token(database.Base):
    __tablename__ = "tokens"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(String(255), index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)



class APIKeys(database.Base):
    __tablename__ = "api_keys"
    id = Column(String(225), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    app_id = Column(String(225), index=True)
    ipAddr = Column(String(225), index=True)
    app_name = Column(String(225), index=True)
    key = Column(String(225), index=True)
    is_enabled = Column(Boolean, default=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)

    def verify_apikey(self, key: str):
        return _hash.sha256_crypt.verify(key, self.key)


class DeviceToken(database.Base):
    __tablename__ = "device_tokens"
    id = Column(String(225), primary_key=True, index=True, default=uuid4().hex)
    user_email = Column(String(255), index=True)
    device_id = Column(String(225), index=True)
    token = Column(String(225), index=True)
    max_age = Column(DateTime, default=gen_max_age)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
