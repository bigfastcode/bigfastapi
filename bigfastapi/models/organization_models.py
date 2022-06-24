from ast import Str
import datetime as _dt
from email.policy import default
import json
import os
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


from bigfastapi.db.database import Base
from bigfastapi.files import deleteFile, isFileExist
from bigfastapi.schemas import organization_schemas
from bigfastapi.schemas.organization_schemas import BusinessSwitch
from bigfastapi.utils.utils import defaultManu


class Organization(Base):
    __tablename__ = "organization"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"))
    mission = Column(Text())
    vision = Column(Text())
    currency = Column(String(5))
    name = Column(String(255), index=True, default="")
    business_type = Column(String(225), default="retail")
    country_code = Column(String(255), index=True)
    county = Column(String(225))
    state = Column(String(255))
    address = Column(String(255))
    tagline = Column(Text())
    image_url = Column(Text(), default="")
    is_deleted = Column(Boolean(), default=False)
    credit_balance = Column(Integer, default=5000)
    email = Column(String(255), default="")
    phone_number = Column(String(255), default="")
    phone_country_code = Column(String(225))
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)
    date_created_db = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated_db = Column(DateTime, default=_dt.datetime.utcnow)





# --------------------------------------------------------------------------------------------------#
#                                    REPOSITORY AND HELPERS
# --------------------------------------------------------------------------------------------------#

def getActiveMenu(businessType):
    menuList = defaultManu()
    return menuList[businessType]


async def fetchOrganization(orgId: str, db: _orm.Session):
    return db.query(Organization).filter(Organization.id == orgId).first()


async def deleteBizImageIfExist(org: Organization):
    # check if user object contains image endpoint
    if org.image is not None and len(org.image) > 17 and 'organzationImages/' in org.image:
        # construct the image path from endpoint
        splitPath = org.image.split('organzationImages/', 1)
        imagePath = f"\organzationImages\{splitPath[1]}"
        fullStoragePath = os.path.abspath("filestorage") + imagePath

        isImageInFile = await isFileExist(fullStoragePath)

        # check if image exist in file prior and delete it
        if isImageInFile:
            deleteRes = await deleteFile(fullStoragePath)
            return deleteRes
        else:
            return False
    else:
        return False
