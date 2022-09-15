import datetime as _dt
from typing import Any, List, Optional

from pydantic import BaseModel

from .contact_info_schema import ContactInfo
from .email_schema import Email
from .location_schema import Location
from .users_schemas import User


class OrganizationBase(BaseModel):
    id: Optional[str]
    mission: Optional[str]
    vision: Optional[str]
    tagline: Optional[str]
    image_url: Optional[str]

    # contact info
    contact_infos: Optional[List[ContactInfo]]
    # location
    location: Optional[List[Location]]

    class Config:
        orm_mode = True


class OrganizationUserBase(BaseModel):
    organization_id: Optional[str]
    user_id: Optional[str]
    role_id: Optional[str]
    is_deleted: Optional[bool] = False
    date_created: Optional[_dt.date]

    class Config:
        orm_mode = True


class InviteBase(BaseModel):
    id: Optional[str]
    email: Optional[str]
    user_id: Optional[str]
    role: Optional[str]
    invite_code: Optional[str]
    is_accepted: Optional[bool] = False
    is_revoked: Optional[bool] = False
    is_deleted: Optional[bool] = False

    class Config:
        orm_mode = True


class Role(BaseModel):
    organization_id: Optional[str]
    role_name: str

    class Config:
        orm_mode = True


# ORGANIZATION SCHEMAS


class OrganizationCreate(OrganizationBase):
    currency_code: str
    name: str
    business_type: str = "retail"
    create_wallet: Optional[bool] = False


class OrganizationUpdate(OrganizationBase):
    currency_code: Optional[str]
    name: Optional[str]
    business_type: Optional[str] = "retail"


class Organization(OrganizationBase):
    id: str
    creator: str
    date_created: _dt.datetime
    last_updated: _dt.datetime

    class Config:
        orm_mode = True


class BusinessSwitch(BaseModel):
    id: str
    business_type: str

    class Config:
        orm_mode = True


class PinOrUnpin(BusinessSwitch):
    menu_item: str
    action: str

    class Config:
        orm_mode = True


# END ORGANIZATION SCHEMAS

# -------------------------------------- #

# ORGANIZATION INVITE SCHEMAS


class UserInvite(InviteBase):
    organization: dict
    app_url: str
    email_details: Email


class Invite(InviteBase):
    organization_id: str
    invite_code: str

    class Config:
        orm_mode = True


class OrganizationUser(InviteBase):
    user_id: str


class InviteResponse(BaseModel):
    message: str


org: dict = dict(
    id="string",
    mission="string",
    vision="string",
    name="string",
    country="string",
    state="string",
    address="string",
    currency_preference="string",
    phone_number="string",
    email="string",
    current_subscription="string",
    tagline="string",
    image="string",
    values="string",
    business_type="retail",
    image_full_path="string",
)


class SingleInviteResponse(BaseModel):
    invite: Any = dict(
        id="string",
        email="string",
        user_id="string",
        role="string",
        organization=org,
    )
    user: User


class AllInvites(BaseModel):
    data: List[InviteBase]


class AcceptInviteResponse(BaseModel):
    invited: OrganizationUserBase
    organization: OrganizationBase


class RevokedInviteResponse(InviteBase):
    is_revoked: bool = True
    is_deleted: bool = True


class DeclinedInviteResponse(InviteBase):
    is_deleted: bool = True


# END ORGANIZATION INVITE SCHEMAS

# ------------------------------ #

# ORGANIZATION USER SCHEMAS


class Invited(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    user_id: str
    role_name: str


class ItemsClass(BaseModel):
    owner: User
    invited_users: List[
        Any
    ]  # naming list type to Invited class when response is confirmed


class OrganizationUsersResponse(BaseModel):
    page: int
    size: int
    total: int
    items: List[ItemsClass]
    previous_page: Optional[str]
    next_page: Optional[str]
    # invited: List = list(dict(id="string", first_name="string", last_name="string", email="string", user_id="string", role="string", organization_id="string", date_created="string"))


# END ORGANIZATION USER SCHEMAS


# ---------------------------------- #

# ORGANIZATION ROLE SCHEMAS
class AddRole(Role):
    role_name: str


class RoleUpdate(OrganizationUserBase):
    email: str
    role: str


class UpdateRoleResponse(BaseModel):
    message: str
    data: OrganizationUserBase


# END ORGANIZATION ROLE SCHEMAS
