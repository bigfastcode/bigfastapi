from datetime import datetime
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Boolean
from uuid import uuid4
import bigfastapi.db.database as database
from bigfastapi.schemas import users_schemas as schema
import sqlalchemy.orm as orm


class Notification(database.Base):
    __tablename__ = "notifications"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    creator = Column(String(100), index=True)
    content = Column(String(255), index=True)
    has_read = Column(Boolean, default=False)
    reference = Column(String(100), index=True)
    recipient = Column(String(255), index=True)
    date_created = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)


def get_authenticated_user_email(user: schema.User):
    return user.email

def notification_selector(id: str, db: orm.Session):
    notification = db.query(Notification).filter(Notification.id == id).first()
    return notification
