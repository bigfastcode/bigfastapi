from fastapi import APIRouter
from datetime import datetime
from bigfastapi.db.database import get_db
from fastapi import Depends
from .models import notification_models as model
from .schemas import notification_schemas as schema, users_schemas as user_schema
from typing import List
from bigfastapi.auth_api import is_authenticated
import sqlalchemy.orm as orm
from uuid import uuid4



app = APIRouter(tags=["Notification"])

@app.get("/notification/{notification_id}", response_model=schema.Notification)
def get_a_notification(notification_id: str, db: orm.Session = Depends(get_db)):

    """Get details of a notification

    Args:
        notification_id (str): the id of the notification.
    Returns:
        schema.Nofication: Detail of the notification
    """

    return model.notification_selector(id=notification_id, db=db)

@app.get("/notifications", response_model=List[schema.Notification])
def get_all_notifications(db: orm.Session = Depends(get_db)):  

    """Get all the notifications

    Returns:
        List of schema.Notification: A list of all the notifications
    """

    notifications = db.query(model.Notification).all()
    return list(map(schema.Notification.from_orm, notifications))

@app.post("/notification", response_model=schema.Notification)
def create_notification(notification: schema.NotificationCreate, user: user_schema.User = Depends(is_authenticated),db: orm.Session = Depends(get_db)):

    """Create a new notification

    Returns:
        schema.Notification: Details of the newly created notification
    """

    if notification.creator == "":
        creator = model.get_authenticated_user_email(user=user)
    else:
        creator = notification.creator

    new_notification = model.Notification(id=uuid4().hex, creator=creator, content=notification.content, reference=notification.reference, recipient=notification.recipient)
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return schema.Notification.from_orm(new_notification)

@app.put("/notification/{notification_id}/read", response_model=schema.Notification)
def mark_notification_read(notification_id: str,db: orm.Session = Depends(get_db)):  

    """Marks a notifcation as read

    Args:
        notification_id (str): the id of the notification
    
    Returns:
        schema.Notification: Refreshed data of the updated notification
    """

    notification = model.notification_selector(id=notification_id, db=db)

    if notification.has_read:
        pass
    else:
        notification.has_read = True
        notification.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(notification)

    return schema.Notification.from_orm(notification)

@app.put("/notifications/read", response_model=List[schema.Notification])
def mark_notifications_read(db: orm.Session = Depends(get_db)):

    """Mark all the notifications as read
    
    Returns:
        List of schema.Notification: A list of all the notifications updated to read
    """

    notifications = db.query(model.Notification).all()
    for notification in notifications:
        if notification.has_read:
            pass
        else:
            notification.has_read = True
            notification.last_updated = datetime.utcnow()
            
        db.commit()
        db.refresh(notification)
    
    return list(map(schema.Notification.from_orm, notifications))

@app.put("/notifications/{notification_id}", response_model=schema.Notification)
def update_notification(notification_id: str, notification: schema.NotificationUpdate, db: orm.Session = Depends(get_db)):
    
    """Update a notification
    
    Args:
        notification_id (str): the id of the notification

    Returns:
        schema.Notification: The details of the notification that has been updated
    """
    notification_from_db = model.notification_selector(id=notification_id, db=db)

    if notification.content != "":
        notification_from_db.content = notification.content

    if notification.reference != "":
        notification_from_db.reference = notification.reference

    if notification.recipient != "":
        notification_from_db.recipient = notification.recipient

    notification_from_db.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(notification_from_db)

    return schema.Notification.from_orm(notification_from_db)

@app.delete("/notification/{notification_id}")
def delete_notification(notification_id: str,db: orm.Session = Depends(get_db)):

    """Delete a notification from the db
    
    Args:
        notification_id (str): the id of the notification

    Returns:
        object (dict): successfully deleted
    """

    notification = model.notification_selector(id=notification_id, db=db)

    db.delete(notification)
    db.commit()

    return {"message":"successfully deleted"}
