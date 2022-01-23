import fastapi
from fastapi import Request, APIRouter
from datetime import datetime
import sqlalchemy.orm as orm
from bigfastapi import auth
from bigfastapi.db.database import get_db
from fastapi import Depends

from bigfastapi.schemas import users_schemas
from .models import notification_models
from .schemas import notification_schemas
from uuid import uuid4
from typing import List
from bigfastapi.auth import is_authenticated


app = APIRouter(tags=["Notification"])

@app.get("/notification/{notification_id}", response_model=notification_schemas.Notification)
def get_a_notification(
    notification_id: str, 
    db: orm.Session = Depends(get_db)
):
    return notification_selector(id=notification_id, db=db)

@app.get("/notifications", response_model=List[notification_schemas.Notification])
def get_all_notifications(
    db: orm.Session = Depends(get_db)
):
    return get_all_notifications_from_db(db=db)

@app.post("/notification", response_model=notification_schemas.Notification)
def create_notification(
    notification: notification_schemas.NotificationCreate, 
    user: users_schemas.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)
):
    return create_a_notification(user=user, notification=notification, db=db)

@app.put("/notification/{notification_id}/read", response_model=notification_schemas.Notification)
def mark_notification_read(
    notification_id: str,
    db: orm.Session = Depends(get_db)
):
    return mark_a_notification_read(id=notification_id, db=db)

@app.put("/notifications/read", response_model=List[notification_schemas.Notification])
def mark_notifications_read(
    db: orm.Session = Depends(get_db)
):
    return mark_all_notifications_read(db=db)

@app.put("/notifications/{notification_id}", response_model=notification_schemas.Notification)
def update_notification(
    notification_id: str,
    notification: notification_schemas.NotificationUpdate,
    db: orm.Session = Depends(get_db)
):
    return update_a_notification(id=notification_id, notification=notification, db=db)

@app.delete("/notification/{notification_id}")
def delete_notification(
    notification_id: str,
    db: orm.Session = Depends(get_db)
):
    return delete_a_notification(id=notification_id, db=db)




#=================================== NOTIFICATION SERVICES =================================#

def get_authenticated_user_email(user: users_schemas.User):
    return user.email

def notification_selector(id: str, db: orm.Session):
    notification = db.query(notification_models.Notification).filter(notification_models.Notification.id == id).first()

    if notification is None:
        raise fastapi.HTTPException(status_code=404, detail="Notification does not exist")

    return notification

def get_all_notifications_from_db(db: orm.Session):
    notifications = db.query(notification_models.Notification).all()
    return list(map(notification_schemas.Notification.from_orm, notifications))

def mark_a_notification_read(id:str, db: orm.Session):
    notification = notification_selector(id=id, db=db)

    if notification.has_read:
        pass
    else:
        notification.has_read = True
        notification.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(notification)

    return notification_schemas.Notification.from_orm(notification)

def mark_all_notifications_read(db: orm.Session):
    notifications = db.query(notification_models.Notification).all()
    for notification in notifications:
        if notification.has_read:
            pass
        else:
            notification.has_read = True
            notification.last_updated = datetime.utcnow()
            
        db.commit()
        db.refresh(notification)
    
    return list(map(notification_schemas.Notification.from_orm, notifications))

def create_a_notification(user: users_schemas.User, notification: notification_schemas.NotificationCreate, db: orm.Session):

    if notification.creator == "":
        creator = get_authenticated_user_email(user=user)
    else:
        creator = notification.creator

    new_notification = notification_models.Notification(id=uuid4().hex, creator=creator, content=notification.content, reference=notification.reference, recipient=notification.recipient)
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return notification_schemas.Notification.from_orm(new_notification)

def delete_a_notification(id:str , db: orm.Session):
    notification = notification_selector(id=id, db=db)

    db.delete(notification)
    db.commit()

    return {"message":"successfully deleted"}

def update_a_notification(id: str, notification: notification_schemas.NotificationUpdate, db: orm.Session):
    notification_from_db = notification_selector(id=id, db=db)

    if notification.content != "":
        notification_from_db.content = notification.content

    if notification.reference != "":
        notification_from_db.reference = notification.reference

    if notification.recipient != "":
        notification_from_db.recipient = notification.recipient

    notification_from_db.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(notification_from_db)

    return notification_schemas.Notification.from_orm(notification_from_db)