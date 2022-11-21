from bigfastapi.db.database import get_db
from fastapi import Depends, status, HTTPException
import sqlalchemy.orm as orm
from bigfastapi.services.auth_service import is_authenticated
from bigfastapi.models.notification_models import (
    Notification,
    NotificationRecipient,
    NotificationGroupMember,
    NotificationGroupModule,
    NotificationSetting as Setting,
    NotificationModule,
    NotificationGroup
)
from bigfastapi.models.organization_models import (
    OrganizationUser,
    Organization,
    Role
)
from bigfastapi.models.user_models import User
from bigfastapi.schemas.notification_schemas import (
    NotificationCreate,
    NotificationSetting,
    NotificationSettingUpdate
)
from bigfastapi.schemas import users_schemas as user_schema
from uuid import uuid4
import re


def create_notification(
    notification: NotificationCreate,
    user: user_schema.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)
):
    if type(notification) != dict:
        notification = notification.dict()
    # check if organization notification setting status is True
    existing_setting = db.query(Setting).filter(
        Setting.organization_id == notification["organization_id"]
    ).first()

    # if existing_setting.status == True: #creates notification when status is set to True
    new_notification = Notification(
        id=uuid4().hex,
        creator_id=notification["creator_id"],
        message=notification["message"],
        organization_id=notification["organization_id"],
        access_level=notification["access_level"]
    )
    db.add(new_notification)

    recipient_ids = get_notification_recipients(
        organization_id=notification["organization_id"],
        module=notification["module"],
        access_level=notification["access_level"],
        db=db,
        mentions=notification["mentions"] if notification["mentions"] else None
    )

    print(recipient_ids)
    for recipient in recipient_ids:
        new_notification_recipient = NotificationRecipient(
            id=uuid4().hex, notification_id=new_notification.id, recipient_id=recipient,
            is_read=False, is_cleared=False
        )
        db.add(new_notification_recipient)

    db.commit()
    db.refresh(new_notification)

    return new_notification


def get_notification_recipients(organization_id, module, access_level, db, mentions):
    if mentions and module == "comments":
        user_ids = []
        for name in mentions:
            first_name = f"{name}%"

            creator = db.query(Organization).join(User).filter(
                Organization.id == organization_id
            ).filter(User.first_name.ilike(first_name)).first()

            users = db.query(OrganizationUser).join(User).filter(
                OrganizationUser.organization_id == organization_id
            ).filter(User.first_name.ilike(first_name)).all()

            if creator:
                user_ids.append(creator.user_id)

            if users:
                for user in users: user_ids.append(user.user_id)
        return user_ids

    creator = db.query(Organization).filter(Organization.id == organization_id).first()

    users = db.query(OrganizationUser).filter(
        OrganizationUser.organization_id == organization_id).all()

    user_ids = [user.user_id for user in users]
    user_ids.append(creator.user_id)

    return user_ids
    # # Find module in notification_module table that matches module and get its id
    # notification_module = db.query(NotificationModule).filter(
    #     NotificationModule.module_name == module).first()
    # if notification_module != None:
    #     notification_module_id = notification_module.id

    #     # Get id of all groups associated with that module
    #     notification_groups = db.query(NotificationGroupModule).filter(
    #         NotificationGroupModule.module_id == notification_module_id).all()

    #     if len(notification_groups) == 0:
    #         group_members = None

    #     else:
    #         notification_group_ids = []
    #         for notification_group in notification_groups:
    #             notification_group_ids.append(notification_group.group_id)

    #         # Get id of all group members in those groups
    #         group_members = []

    #         for group_id in notification_group_ids:
    #             members = db.query(NotificationGroupMember).filter(
    #                 NotificationGroupMember.group_id == group_id).all()

    #             group_member_ids = []
    #             for group_member in members:
    #                 group_member_ids.append(group_member.member_id)

    #             for member_id in group_member_ids:
    #                 if member_id not in group_members:
    #                     group_members.append(member_id)
    # else:
    #     group_members = None

    # if access_level and group_members is None:
    #     users_id = []
    #     users = db.query(OrganizationUser).join(Role).filter(
    #         OrganizationUser.organization_id == organization_id
    #     ).filter(Role.role_name == access_level).all()
    #     for user in users:
    #         users_id.append(user.user_id)
    #     return users_id

    # if access_level is None and group_members is None:
    #     users_id = []
    #     users = db.query(OrganizationUser).filter(
    #         OrganizationUser.organization_id == organization_id
    #     ).all()
    #     for user in users:
    #         users_id.append(user.user_id)
    #     return users_id

    # if group_members and access_level is None:
    #     return group_members

    # if group_members and access_level:

    #     # get role_id with role = access_level
    #     role = db.query(Role).filter(
    #         Role.organization_id == organization_id
    #     ).filter(Role.role_name == access_level).first()

    #     role_id = role.id

    #     # get group members with access_level = access_level
    #     group_members_with_access_level = []

    #     for group_member in group_members:
    #         member = db.query(OrganizationUser).filter(
    #             OrganizationUser.organization_id == organization_id
    #         ).filter(OrganizationUser.user_id == group_member).filter(
    #             OrganizationUser.role_id == role_id).first()

    #         if member != None:
    #             member_id = member.user_id
    #             group_members_with_access_level.append(member_id)


def create_notification_setting(
    notification_setting: NotificationSetting,
    user: user_schema.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)
):
    new_settings = Setting(
        id=uuid4().hex,
        organization_id=notification_setting.organization_id,
        access_level=notification_setting.access_level,
        send_via=notification_setting.send_via
    )

    db.add(new_settings)
    db.commit()
    db.refresh(new_settings)

    return new_settings


async def update_notification_setting(
        notification_setting: NotificationSettingUpdate,
        fetched_setting,
        user: user_schema.User = Depends(is_authenticated),
        db: orm.Session = Depends(get_db)):

    if notification_setting.access_level:
        fetched_setting.access_level = notification_setting.access_level
    if notification_setting.send_via:
        fetched_setting.send_via = notification_setting.send_via
    if notification_setting.status != "":
        fetched_setting.status = notification_setting.status
    fetched_setting.last_updated = notification_setting.last_updated if notification_setting.last_updated else datetime.now()

    db.commit()
    db.refresh(fetched_setting)
    return fetched_setting


async def fetch_existing_setting(id: str, organization_id: str, db: orm.Session):
    notification_setting = db.query(Setting).filter(Setting.id == id).filter(
        Setting.organization_id == organization_id).first()
    if not notification_setting:
        raise HTTPException(detail="Notification does not exist",
                            status_code=status.HTTP_404_NOT_FOUND)
    return notification_setting


async def get_organization_access_level(organization_id: str, db: orm.Session):
    org_notification_setting = db.query(Setting).filter(
        Setting.organization_id == organization_id
    ).first()

    access_level = org_notification_setting.access_level

    return access_level


async def get_notifications(user_id: str, organization_id: str, db: orm.Session, size: int = None, offset: int = None):

    notifications_query = (db.query(Notification, NotificationRecipient.is_read, NotificationRecipient.is_cleared)
                           .join(NotificationRecipient)
                           .filter(NotificationRecipient.recipient_id == user_id, Notification.organization_id == organization_id)
                           .order_by(Notification.date_created.desc()))

    total_items = notifications_query.count()

    notifications = (notifications_query.offset(offset=offset).limit(limit=size).all())

    return notifications, total_items


async def check_group_member_exists(group_id: str, member_id: str, db: orm.Session):
    member = db.query(NotificationGroupMember).filter(NotificationGroupMember.group_id == group_id
                                                      ).filter(NotificationGroupMember.member_id == member_id).first()

    if member != None:
        return True
    else:
        return False


async def get_recipient_notification(recipient_id: str, notification_id: str, db: orm.Session):
    notification = db.query(NotificationRecipient).filter(NotificationRecipient.notification_id
                                                          == notification_id, NotificationRecipient.recipient_id == recipient_id).first()

    return notification


async def get_notification_with_recipient(recipient_id: str, notification_id: str, db: orm.Session):
    notification = (db.query(Notification, NotificationRecipient.is_read, NotificationRecipient.is_cleared)
                      .join(NotificationRecipient)
                      .filter(NotificationRecipient.notification_id == notification_id, NotificationRecipient.recipient_id == recipient_id)
                      .first())

    return notification


async def get_mentions(comment):
    mentions = re.findall(r'(?<=@)\w+', comment)
    return mentions


async def create_comment_notification_format(
    organization_id: str, 
    module: str,    
    mentions: list,
    action: str = "mentioned", 
    db: orm.Session = Depends(get_db),
    user: user_schema.User = Depends(is_authenticated)    
):
    message = f"{user.first_name} mentioned you in a comment"
    try:
        access_level = await get_organization_access_level(organization_id=organization_id, db=db)
    except:
        access_level = None    
    notification_format =  {
        "creator_id": user.id,
        "module": module,
        "message": message,
        "organization_id": organization_id,
        "access_level": access_level,
        "mentions": mentions
    }
    
    return notification_format
