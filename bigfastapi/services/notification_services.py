from bigfastapi.db.database import get_db
from fastapi import Depends, status, HTTPException
import sqlalchemy.orm as orm
from bigfastapi.services.auth_service import is_authenticated
from bigfastapi.models.notification_models import(
    Notification,
    NotificationRecipient,
    NotificationGroupMember,
    NotificationGroupModule,
    NotificationSetting as Setting
)
from bigfastapi.models.organization_models import (
    OrganizationUser,
    Role
)
from bigfastapi.schemas.notification_schemas import(
    NotificationCreate,
    NotificationSetting,
    NotificationSettingUpdate
)
from bigfastapi.schemas import users_schemas as user_schema



def create_notification(
    notification: NotificationCreate,
    user: user_schema.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)
):
    new_notification = Notification(
        id=notification.id if notification.id else uuid4().hex, 
        creator_id=notification.creator_id, 
        message=notification.message, 
        access_level=notification.access_level, 
    )
    db.add(new_notification)
    # db.commit()

    recipient_ids = get_notification_recipients(
        module=notification.module, 
        organization_id=notification.organization_id, 
        access_level=notification.access_level
    )
    for recipient in notification.recipient_ids:
        new_notification_recipient = NotificationRecipient(
            id=uuid4().hex, notification_id=new_notification.id, recipient_id=recipient
        )
        db.add(new_notification_recipient)
    
    db.commit()
    db.refresh(new_notification)    

    return new_notification


def get_notification_recipients(module, organization_id, access_level):
    group_members = db.query(NotificationGroupMember.member_id).join(NotificationGroupModule).filter(
        NotificationGroupModule.module == module).all() 
    
    #if empty list, default group members will be all users 
    if group_members is None:
        users = db.query(OrganizationUser.user_id).join(Role).filter(
            OrganizationUser.organization_id == organization_id
            ).filter(Role.role_name == access_level).all()

        return users
    return group_members  


def create_notification_setting(
    notification_setting: NotificationSetting, 
    user: user_schema.User = Depends(is_authenticated), 
    db: orm.Session = Depends(get_db)
):
    new_settings = Setting(
        id=notification_seting.id if notification_setting.id else uuid4().hex,
        organization_id=notification_setting.organization_id,
        sales=notification_setting.sales,
        products=notification_setting.products,
        stocks=notification_setting.stocks,
        debts=notification_setting.debts,
        payments=notification_setting.payments,
        purchases=notification_setting.purchases,
        invoices=notification_setting.invoices,
        comments=notification_setting.comments,
        access_level=notification_setting.access_level,
        send_via=notification_setting.send_via
    )

    return new_settings


async def update_notification_setting(
    notification_setting: NotificationSettingUpdate,
    fetched_setting,
    user: user_schema.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)):

    if notification_setting.sales:           
        fetched_setting.sales = notification_setting.sales
    if notification_setting.products:
        fetched_setting.products = notification_setting.products
    if notification_setting.stocks:
        fetched_setting.stocks = notification_setting.stocks
    if notification_setting.debts:
        fetched_setting.debts = notification_setting.debts
    if notification_setting.payments:
        fetched_setting.payments = notification_setting.payments
    if notification_setting.purchases:
        fetched_setting.purchases = notification_setting.purchases
    if notification_setting.invoices:
        fetched_setting.invoices = notification_setting.invoices
    if notification_setting.comments:
        fetched_setting.comments = notification_setting.comments
    if notification_setting.access_level:
        fetched_setting.access_level = notification_setting.access_level
    if notification_setting.send_via:
        fetched_setting.send_via = notification_setting.send_via   
    fetched_setting.last_updated = notification_setting.last_updated if notification_setting.last_updated else datetime.now()

    db.commit()
    db.refresh(fetched_setting)
    return fetched_setting


async def fetch_existing_setting(id:str, organization_id:str, db:orm.Session):
    notification_setting = db.query(Setting).filter(Setting.id == id).filter(
        Setting.organization_id== organization_id).first()
    if not notification_setting:
        raise HTTPException(detail="Notification does not exist",
            status_code=status.HTTP_404_NOT_FOUND)
    return notification_setting


            
