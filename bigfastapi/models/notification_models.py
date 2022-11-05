from datetime import datetime
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Boolean, Enum
from uuid import uuid4
import bigfastapi.db.database as database
from bigfastapi.schemas import users_schemas as schema
import sqlalchemy.orm as orm
import enum
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

# class Notification(database.Base):
#     __tablename__ = "notifications"
#     id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
#     creator = Column(String(100), index=True)
#     content = Column(String(255), index=True)
#     has_read = Column(Boolean, default=False)
#     reference = Column(String(100), index=True)
#     recipient = Column(String(255), index=True)
#     date_created = Column(DateTime, default=datetime.utcnow)
#     last_updated = Column(DateTime, default=datetime.utcnow)


class SendVia(enum.Enum):
    email = "email"
    in_app = "in_app"
    both = "both"


class Notification(database.Base):
    __tablename__ = "notifications"
    id = Column(String(50), primary_key=True, index=True, default=uuid4().hex)
    creator_id = Column(String(50), ForeignKey(
        "users.id"))  # foreign key to users table
    message = Column(String(500), index=True)
    organization_id = Column(String(50), ForeignKey("organizations.id"))
    access_level = Column(String(100), index=True, default="admin")
    date_created = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", backref="notification_creator", lazy="selectin")


class NotificationModule(database.Base):
    __tablename__ = "notification_modules"
    id = Column(String(50), primary_key=True, index=True, default=uuid4().hex)
    module_name = Column(String(50), index=True)
    status = Column(Boolean, default=True)
    date_created = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)


class NotificationRecipient(database.Base):
    __tablename__ = "notification_recipients"
    id = Column(String(50), primary_key=True, index=True, default=uuid4().hex)
    notification_id = Column(String(50), ForeignKey(
        "notifications.id"))  # foreign key to notification
    recipient_id = Column(String(50), ForeignKey(
        "users.id"))  # foreign key to users table
    is_read = Column(Boolean, default=False)
    is_cleared = Column(Boolean, default=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)


class NotificationSetting(database.Base):
    __tablename__ = "notification_settings"
    id = Column(String(50), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(50), ForeignKey(
        "organizations.id"))  # foreignkey to organization
    access_level = Column(String(100), index=True)
    send_via = Column(String(100), index=True)
    status = Column(Boolean, default=True)
    date_created = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)


class NotificationGroup(database.Base):
    __tablename__ = "notification_groups"
    id = Column(String(50), primary_key=True, index=True, default=uuid4().hex)
    name = Column(String(255), index=True)
    organization_id = Column(String(50), ForeignKey(
        "organizations.id"))  # foreignkey to organization
    date_created = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    notification_group_members = relationship(
        "NotificationGroupMember", backref="notification_groups", lazy="selectin"
    )


# association table
class NotificationGroupMember(database.Base):
    __tablename__ = "notification_group_members"
    id = Column(String(50), primary_key=True, index=True, default=uuid4().hex)
    group_id = Column(String(50), ForeignKey("notification_groups.id"))
    member_id = Column(String(50), ForeignKey("users.id"))  # foreign key to users
    date_created = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)

    user_member = relationship(
        "User", backref="notification_group_members", lazy="selectin")


class NotificationGroupModule(database.Base):
    __tablename__ = "notification_group_modules"
    id = Column(String(50), primary_key=True, index=True, default=uuid4().hex)
    group_id = Column(String(50), ForeignKey("notification_groups.id"))
    module_id = Column(String(100), ForeignKey(
        "notification_modules.id"))  # sales, payments, stocks etc
    date_created = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)


def get_authenticated_user_email(user: schema.User):
    return user.email


def notification_selector(id: str, db: orm.Session):
    notification = db.query(Notification).filter(Notification.id == id).first()
    return notification
