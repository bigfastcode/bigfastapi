import datetime as _dt
from sqlite3 import Timestamp
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Enum, DateTime, Boolean, ARRAY, DateTime
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql import func
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE

import bigfastapi.database as _database

class User(_database.Base):
    __tablename__ = "users"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    email = Column(String(255), unique=True, index=True)
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    phone_number = Column(String(255), index=True, default="")
    password = Column(String(255))
    is_active = Column(Boolean)
    is_verified = Column(Boolean)
    is_superuser = Column(Boolean, default=False)
    organization = Column(String(255), default="")

    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.password)


class Organization(_database.Base):
    __tablename__ = "organizations"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    creator = Column(String(255), ForeignKey("users.id"))
    mission = Column(String(255), index=True)
    vision = Column(String(255), index=True)
    values = Column(ARRAY(String(255)), index=True)
    name = Column(String(255),unique= True, index=True, default="")
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)


class Token(_database.Base):
    __tablename__ = "tokens"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    token = Column(String(255), index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)

class VerificationToken(_database.Base):
    __tablename__ = "verification_tokens"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    token = Column(String(255), index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)

class PasswordResetToken(_database.Base):
    __tablename__ = "password_reset_tokens"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    token = Column(String(255), index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)


class VerificationCode(_database.Base):
    __tablename__ = "verification_codes"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    code = Column(String(255), index=True, unique=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)


class PasswordResetCode(_database.Base):
    __tablename__ = "password_reset_codes"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id"))
    code = Column(String(255), index=True, unique=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)


class Comment(_database.Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_type = Column(String) 
    rel_id = Column(String)
    
    email = Column(String(255))
    name = Column(String(255))
    text = Column(String())
    downvotes = Column(Integer, default=0, nullable=False)
    upvotes = Column(Integer, default=0, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    p_id = Column(Integer, ForeignKey("comments.id", ondelete="cascade"))
    parent = _orm.relationship("Comment", backref=_orm.backref('replies',  cascade="all, delete-orphan"), remote_side=[id], post_update=True, single_parent=True, uselist=True)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.model_type = kwargs["model_name"] 
        self.rel_id = kwargs["rel_id"]
        self.email = kwargs["email"] 
        self.name = kwargs["name"] 
        self.text = kwargs["text"] 
        self.p_id = kwargs.get("p_id", None)

    @hybrid_method
    def upvote(self):
        self.upvotes += 1
    
    @hybrid_method
    def downvote(self):
        self.downvotes += 1