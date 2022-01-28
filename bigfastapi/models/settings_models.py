import datetime as _dt
from sqlite3 import Timestamp
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Enum, DateTime, Boolean, ARRAY, Text
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql import func
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE
import bigfastapi.db.database as database
# from organisation_models import Organisation


class Settings(database.Base):

    __tablename__ = "settings"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization = Column(String(255), ForeignKey("organizations.id"))
    location = Column(String(255), index=True)
    phone_number = Column(String(255), index=True)
    email = Column(String(255), index=True)
    organization_size = Column(String(255), index=True)
    organization_type = Column(String(255), index=True)
    country = Column(String(255), index=True)
    state = Column(String(255), index=True)
    city = Column(String(255), index=True)
    zip_code = Column(Integer, index=True)















#     def __init__(self, settings):
#         self.settings = settings



#     # mission = Column(String(255), index=True)
#     # vision = Column(String(255), index=True)
#     # values = Column(String(255), index=True)
#     # name = Column(String(255),unique= True, index=True, default="")

#     # date_created = Column(DateTime, default=_dt.datetime.utcnow)
#     # last_updated = Column(DateTime, default=_dt.datetime.utcnow)


# import datetime as _dt
# from sqlite3 import Timestamp
# import sqlalchemy as _sql
# import sqlalchemy.orm as _orm
# import passlib.hash as _hash
# from sqlalchemy.schema import Column
# from sqlalchemy.types import String, Integer, Enum, DateTime, Boolean, ARRAY, Text
# from sqlalchemy import ForeignKey
# from uuid import UUID, uuid4
# from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
# from sqlalchemy.sql import func
# from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE
# import bigfastapi.db.database as _database

# class User(_database.Base):
#     __tablename__ = "users"
#     id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
#     email = Column(String(255), unique=True, index=True)
#     first_name = Column(String(255), index=True)
#     last_name = Column(String(255), index=True)
#     phone_number = Column(String(255), index=True, default="")
#     password = Column(String(255))
#     is_active = Column(Boolean)
#     is_verified = Column(Boolean)
#     is_superuser = Column(Boolean, default=False)
#     organization = Column(String(255), default="")

#     def verify_password(self, password: str):
#         return _hash.sha256_crypt.verify(password, self.password)



# # class User(Base):
# #    __tablename__ = "users"
# #    id = Column(Integer, primary_key=True, index=True)
# #    lname = Column(String)
# #    fname = Column(String)
# #    email = Column(String, unique=True, index=True)
# #    todos = relationship("TODO", back_populates="owner", cascade="all, delete-orphan")
 
# # class TODO(Base):
# #    __tablename__ = "todos"
# #    id = Column(Integer, primary_key=True, index=True)
# #    text = Column(String, index=True)
# #    completed = Column(Boolean, default=False)
# #    owner_id = Column(Integer, ForeignKey("users.id"))
# #    owner = relationship("User", back_populates="todos")



