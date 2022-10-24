from datetime import datetime
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Boolean
from uuid import uuid4
import bigfastapi.db.database as database
from bigfastapi.schemas import users_schemas as schema
import sqlalchemy.orm as orm


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
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(100), index=True)
    message = Column(String(255), index=True)
    organization_id = Column(String(100), index=True)
    access_level = Column(String(100), index = True)    
    date_created = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    date_created_db = Column(DateTime, default=datetime.utcnow)
    last_updated_db = Column(DateTime, default=datetime.utcnow)


class NotificationRecipients(database.Base):
    __tablename__ = "notification_recipients"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    notification_id = Column(String(100), index=True)
    recipient_id = Column(String(100), index=True)
    is_read = Column(Boolean, default=False)
    is_cleared = Column(Boolean, default=False)     
    date_created = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    date_created_db = Column(DateTime, default=datetime.utcnow)
    last_updated_db = Column(DateTime, default=datetime.utcnow)

   
class NotificationSettings(database.Base):
    __tablename__ = "notification_settings"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(100), index=True)    
    sales = Column(Boolean, default=True)
    products = Column(Boolean, default=True) 
    stocks = Column(Boolean, default=True)
    debts = Column(Boolean, default=True) 
    payments = Column(Boolean, default=True) 
    purchases = Column(Boolean, default=True) 
    invoices = Column(Boolean, default=True) 
    access_level = Column(String(255), index=True)
    send_via = Column(Enum(SendVia), index=True)
    date_created = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    date_created_db = Column(DateTime, default=datetime.utcnow)
    last_updated_db = Column(DateTime, default=datetime.utcnow)


def get_authenticated_user_email(user: schema.User):
    return user.email

def notification_selector(id: str, db: orm.Session):
    notification = db.query(Notification).filter(Notification.id == id).first()
    return notification
