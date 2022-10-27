from fastapi import APIRouter
from datetime import datetime
from bigfastapi.db.database import get_db
from fastapi import Depends, status, HTTPException
from .models import notification_models as model
from .schemas import notification_schemas as schema, users_schemas as user_schema
from typing import List
from bigfastapi.services.auth_service import is_authenticated
import sqlalchemy.orm as orm
from uuid import uuid4
from bigfastapi.models.organization_models import Organization
from fastapi.responses import JSONResponse
from .models.user_models import User
from .services.notification_services import (
    create_notification, 
    create_notification_setting, 
    fetch_existing_setting,
    update_notification_setting
)
from bigfastapi.core.helpers import Helpers

app = APIRouter(tags=["Notification"])

@app.get("/notification/{notification_id}", response_model=schema.Notification)
def get_a_notification(notification_id: str, db: orm.Session = Depends(get_db)):

    """intro-->This endpoint allows you to details of a particular notification. You need to make a get request to the /notification/{notification_id} 

    paramDesc--> On get request the url takes a query parameter "notification_id"
        param-->notification_id: This is the unique identifier of the notification

    returnDesc-->On sucessful request, it returns
        returnBody--> details of the notification.
    """

    return model.notification_selector(id=notification_id, db=db)

@app.get("/notifications", response_model=List[schema.Notification])
def get_all_notifications(db: orm.Session = Depends(get_db)):  

    """intro-->This endpoint allows you to retrieve all notifications from the database. To retrieve you need to make a get request to the /notifications endpoint


    returnDesc-->On sucessful request, it returns
        returnBody--> an array of notifications.
    """

    notifications = db.query(model.Notification).all()
    return list(map(schema.Notification.from_orm, notifications))

# added
@app.get("/notifications/{user_id}", response_model=List[schema.Notification])
async def get_user_notifications(
    user_id: str,
    organization_id: str,
    user: user_schema.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)):  

    """intro-->This endpoint allows you to retrieve all notifications from the database. To retrieve you need to make a get request to the /notifications endpoint


    returnDesc-->On sucessful request, it returns
        returnBody--> an array of notifications.
    """ 
    #validate user and organization    
    await Helpers.check_user_org_validity(
            user_id=user.id, organization_id=organization_id, db=db
        )     

    notifications = db.query(model.Notification).join(model.NotificationRecipient).filter(
                    model.NotificationRecipient.recipient_id == user_id 
                    ).filter(model.NotificationRecipient.is_cleared == False).all()

    #return notifications            
    return list(map(schema.Notification.from_orm, notifications))
    

# @app.post("/notification", response_model=schema.Notification)
# def create_notification(notification: schema.NotificationCreate, user: user_schema.User = Depends(is_authenticated),db: orm.Session = Depends(get_db)):

#     """intro-->This endpoint allows you to create a new notification. To create, you need to make a post request to the /notification endpoint with a required body of request as specified below

#         reqBody-->content: This is the content of the notification
#         reqBody-->recipient: This the receiver of the notification
#         reqBody-->reference: This is a unique identifier of the notification
#         reqBody-->creator: This is the creator of the notification

#     returnDesc-->On sucessful request, it returns
#         returnBody--> the details of the newly created notification.
#     """

#     if notification.creator == "":
#         creator = model.get_authenticated_user_email(user=user)
#     else:
#         creator = notification.creator

#     new_notification = model.Notification(id=uuid4().hex, creator=creator, content=notification.content, reference=notification.reference, recipient=notification.recipient)
#     db.add(new_notification)
#     db.commit()
#     db.refresh(new_notification)

#     return schema.Notification.from_orm(new_notification)

# added
@app.post("/notification", response_model=schema.Notification)
async def create_user_notification(
    notification: schema.NotificationCreate,
    user: user_schema.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)):

    """intro-->This endpoint allows you to create a new notification. To create, you need to make a post request to the /notification endpoint with a required body of request as specified below

        reqBody-->message: This is the content of the notification
        reqBody-->recipient: This the receiver of the notification
        reqBody-->creator: This is the creator of the notification

    returnDesc-->On sucessful request, it returns
        returnBody--> the details of the newly created notification.
    """     
    #organization and user check
    await Helpers.check_user_org_validity(
            user_id=user.id, organization_id=notification.organization_id, db=db
        )     

    new_notification = create_notification(notification=notification, user=user, db=db)          

    return new_notification

# added
@app.get("/notifications-settings/{organization_id}", response_model=List[schema.NotificationSettingResponse])
async def get_org_notification_settings(
    organization_id: str,
    user: user_schema.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)):  

    """intro-->This endpoint allows you to retrieve all notifications from the database. To retrieve you need to make a get request to the /notifications endpoint


    returnDesc-->On sucessful request, it returns
        returnBody--> an array of notifications.
    """ 
    #validate user and organization    
    await Helpers.check_user_org_validity(
            user_id=user.id, organization_id=organization_id, db=db
        )     

    notification_settings = db.query(model.NotificationSetting).filter(
                    model.NotificationSetting.organization_id == organization_id 
                    ).all()

    return notification_settings   

    
# added
@app.post("/notification-settings", response_model=schema.NotificationSettingResponse)
async def create_org_notification_settings(
    notification_setting: schema.NotificationSetting,
    user: user_schema.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)):

    """intro-->This endpoint allows you to create a new notification. To create, you need to make a post request to the /notification endpoint with a required body of request as specified below

        reqBody-->message: This is the content of the notification
        reqBody-->recipient: This the receiver of the notification
        reqBody-->creator: This is the creator of the notification

    returnDesc-->On sucessful request, it returns
        returnBody--> the details of the newly created notification.
    """         
    if user.is_superuser:

        #organization and user check
        await Helpers.check_user_org_validity(
                user_id=user.id, organization_id=notification_setting.organization_id, db=db
            )     

        new_notification_setting = create_notification_setting(
            notification_setting=notification_setting, 
            user=user, 
            db=db
        )         
        return new_notification_setting

    return JSONResponse(
            {"message": "Only an Admin can perform this action"}, 
            status_code=status.HTTP_401_UNAUTHORIZED
        )    


@app.put("/notification-settings/{setting_id}", response_model=schema.NotificationSettingResponse)
async def update_org_notification_settings(
    setting_id: str,
    notification_setting: schema.NotificationSetting,
    user: user_schema.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)):

    if user.is_superuser:

        #organization and user check
        await Helpers.check_user_org_validity(
                user_id=user.id, organization_id=notification_setting.organization_id, db=db
            )     

        existing_setting = await fetch_existing_setting(
            id=setting_id,
            organization_id=notification_setting.organization_id, 
            db=db
        )
        updated_notification_setting = await update_notification_setting(
            notification_setting=notification_setting, 
            fetched_setting=existing_setting
        )     

        return updated_notification_setting

    return JSONResponse(
            {"message": "Only an Admin can perform this action"}, 
            status_code=status.HTTP_401_UNAUTHORIZED
        )    


@app.post("/notification-group", response_model=schema.NotificationGroupResponse)
async def create_notification_group(
    group: schema.NotificationGroup,
    organization_id: str, #query_parameter
    user: user_schema.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)):

    #organization and user check
    await Helpers.check_user_org_validity(
            user_id=user.id, organization_id=organization_id, db=db
        )     

    new_notification_group = model.NotificationGroup(id=uuid4().hex, name=group.name)      

    db.add(new_notification_group)
    db.commit()
    db.refresh(new_notification_group)    

    return new_notification_group


@app.put("/notification-group/{group_id}", response_model=schema.NotificationGroupResponse)
async def update_notification_group(
    group_id: str,   
    organization_id: str, #query_parameter,
    group: schema.NotificationGroupUpdate,
    user: user_schema.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)
):

    #organization and user check
    await Helpers.check_user_org_validity(
            user_id=user.id, organization_id=organization_id, db=db
        )     

    fetched_group = db.query(model.NotificationGroup).filter(
    model.NotificationGroup.id == group_id).first()
    if fetched_group is None:
        raise HTTPException(detail="Notification group does not exist",
            status_code=status.HTTP_404_NOT_FOUND)
          
    if group.name:
        fetched_group.name = group.name
    fetched_group.last_updated = group.last_updated if group.last_updated else datetime.now()
    fetched_group.last_updated_db = datetime.now()

    db.commit()
    db.refresh(fetched_group)         

    return fetched_group


@app.delete("/notification-group/{group_id}")
def delete_notification_group(
    notification_id: str,
    user: user_schema.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)
):
    """intro-->This endpoint allows you to delete a particular notification group from the database. You need to make a delete request to the /notification-group/{notification_id} endpoint.

    paramDesc-->On delete request the url takes a query parameter "group_id" 
        param-->group_id: This is the unique identifier of the notification group

    returnDesc-->On sucessful request, it returns message,
        returnBody--> "success".
    """

    group = db.query(model.NotificationGroup).filter(
    model.NotificationGroup.id == group_id).first()

    if group is None:
        raise HTTPException(detail="Notification group not found",
            status_code=status.HTTP_404_NOT_FOUND)

    db.delete(group)
    db.commit()

    return {"message":"successfully deleted"}


@app.post("/notification-group/notification-member", response_model=schema.NotificationGroupMemberResponse)
def add_member_to_notification_group(
    group_member: schema.NotificationGroupMember,
    user: user_schema.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)
):
    new_group_member = model.NotificationGroupMember(
        id=uuid4().hex, group_id=group_member.group_id, member=group_member.member_id
    )   

    db.add(new_group_member)
    db.commit()
    db.refresh(new_group_member)    

    return new_group_member



@app.delete("/notification-group/notification-member/{group_member_id}")
def delete_notification_group(
    group_member_id: str,
    user: user_schema.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)
):
    """intro-->This endpoint allows you to delete a particular notification group from the database. You need to make a delete request to the /notification-group/{notification_id} endpoint.

    paramDesc-->On delete request the url takes a query parameter "group_id" 
        param-->group_id: This is the unique identifier of the notification group

    returnDesc-->On sucessful request, it returns message,
        returnBody--> "success".
    """

    group_member = db.query(model.NotificationGroupMember).filter(
    model.NotificationGroupMember.id == group_member_id).first()

    if group_member is None:
        raise HTTPException(detail="Notification group member not found",
            status_code=status.HTTP_404_NOT_FOUND)

    db.delete(group_member)
    db.commit()

    return {"message":"successfully deleted"}



@app.put("/notification/{notification_id}/read", response_model=schema.Notification)
def mark_notification_read(notification_id: str,db: orm.Session = Depends(get_db)):  

    """intro-->This endpoint allows you mark a queried notifications as read. To use, you need to make a put request to the /notification/{notification_id}/read enpoint. 

    paramDesc--> On put request the url takes a query parameter "notification_id" 
        param-->notification_id: This is the unique identifier of the notification

    returnDesc-->On sucessful request, it returns
        returnBody--> details of the updated notification.
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

    """intro-->This endpoint allows you mark all notifications as read. To use, you need to make a put request to the /notification/read enpoint. 

    returnDesc-->On sucessful request it returns 
        returnBody--> an array of the notifications.
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
    
    """intro-->This endpoint allows you to update a particular notification. You need to make a put request to the /notification/{notification_id} endpoint.

    paramDesc-->On put request the url takes a query parameter "notification_id" 
        param-->notification_id: This is the unique identifier of the notification
        reqBody-->content: This is the content of the notification
        reqBody-->recipient: This the receiver of the notification
        reqBody-->reference: This is a unique identifier of the notification

    returnDesc-->On sucessful request, it returns message,
        returnBody--> "success".
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
    """intro-->This endpoint allows you to delete a particular notification from the database. You need to make a delete request to the /notification/{notification_id} endpoint.

    paramDesc-->On delete request the url takes a query parameter "notification_id" 
        param-->notification_id: This is the unique identifier of the notification

    returnDesc-->On sucessful request, it returns message,
        returnBody--> "success".
    """

    notification = model.notification_selector(id=notification_id, db=db)

    db.delete(notification)
    db.commit()

    return {"message":"successfully deleted"}
