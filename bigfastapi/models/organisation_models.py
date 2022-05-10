import datetime as _dt
from uuid import uuid4

import sqlalchemy.orm as _orm
from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime, Boolean

from bigfastapi.db.database import Base
from bigfastapi.models import store_user_model
from bigfastapi.utils.utils import defaultManu


class Organization(Base):
    __tablename__ = "businesses"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    creator = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"))
    mission = Column(String(255), index=True)
    vision = Column(String(255), index=True)
    values = Column(String(255), index=True)
    currency = Column(String(5), index=True)
    name = Column(String(255), unique=True, index=True, default="")
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
    standard_debt_percentage = Column(String(255), default=None)
    auto_reminders = Column(String(255), default=None)
    bank_details = Column(String(255), default=None)
    email = Column(String(255), default="", index=True)
    phone_number = Column(String(255), default="", index=True)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)


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


async def is_organization_member(user_id: str, organization_id: str, db: _orm.Session):
    organization = (
        db.query(Organization)
            .filter_by(creator=user_id)
            .filter(Organization.id == organization_id)
            .first()
    )

    store_user = db.query(store_user_model.StoreUser).filter_by(store_id=organization_id).filter_by(
        user_id=user_id).first()
    if store_user != None and organization != None:
        return False
    return True
