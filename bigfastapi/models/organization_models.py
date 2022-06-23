import datetime as _dt
import os
from sqlalchemy import ForeignKey
import sqlalchemy.orm as _orm
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime, Boolean
from uuid import uuid4



from bigfastapi.db.database import Base
from bigfastapi.files import deleteFile, isFileExist
from bigfastapi.schemas import organization_schemas
from bigfastapi.schemas.organization_schemas import BusinessSwitch
from bigfastapi.utils.utils import defaultManu


class Organization(Base):
    __tablename__ = "businesses"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    creator = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"))
    mission = Column(String(255), index=True)
    vision = Column(String(255), index=True)
    values = Column(String(255), index=True)
    currency = Column(String(5), index=True)
    name = Column(String(255), index=True, default="")
    business_type = Column(String(225), default="retail")
    country = Column(String(255), index=True)
    state = Column(String(255), index=True)
    address = Column(String(255), index=True)
    tagline = Column(String(255), index=True)
    image = Column(String(255), default="")
    is_deleted = Column(Boolean(), default=False)
    current_subscription = Column(String(225), default="")
    credit_balance = Column(Integer, default=5000)
    currency_preference = Column(String(255), default="")
    email = Column(String(255), default="", index=True)
    phone_number = Column(String(255), default="", index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)

# Organization Invite
class OrganizationInvite(Base):
    __tablename__ = "organization_invites"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), ForeignKey("businesses.id"))
    user_id = Column(String(255), ForeignKey("users.id"))
    user_email = Column(String(255), index=True)
    role_id = Column(String(255), ForeignKey("roles.id"))
    invite_code = Column(String(255), index=True)
    is_accepted = Column(Boolean, default=False)
    is_revoked = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False) 
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    
    class Config:
        orm_mode = True

# Organization User

class OrganizationUser(Base):
    __tablename__ = "organization_users"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), index=True)
    user_id = Column(String(255), ForeignKey("users.id"))
    role_id = Column(String(255), ForeignKey("roles.id"))
    is_deleted = Column(Boolean, default=False) 
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)


# Organization Role
class Role(Base):
    __tablename__ = "roles"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), index=True)
    role_name = Column(String(255), index=True)

class DefaultTemplates(Base):
    __tablename__ = "default_templates"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), ForeignKey("businesses.id"))
    greeting = Column(String(225), index=True)
    subject = Column(String(255), index=True)
    escalation_level = Column(Integer, index=True)
    template_type = Column(String(255), index=True)
    email_message = Column(String(500), index=True)
    sms_message = Column(String(500), index=True)
    is_deleted = Column(Boolean, default=False)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)


class DefaultAutoReminder(Base):
    __tablename__ = "default_auto_reminder"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), index=True)
    days_before_debt = Column(Integer, index=True)
    first_template = Column(String(255), index=True)
    second_template = Column(String(255), index=True)


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
