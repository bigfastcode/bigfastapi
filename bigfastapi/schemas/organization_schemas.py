

import datetime as _dt
from pydantic import BaseModel
from typing import Any, List, Optional

from .email_schema import Email
from .users_schemas import User


class _OrganizationBase(BaseModel):
    id: Optional[str]
    mission: Optional[str]
    vision: Optional[str]
    name: str
    country_code: str
    state: str
    address: str
    currency_code: str
    phone_number: str = None
    email: str = None
    tagline: Optional[str]
    image_url: Optional[str]
    business_type: str = "retail"
    add_template: Optional[bool] = False

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
    user_email: Optional[str]
    user_id: Optional[str]
    user_role: Optional[str]
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

class OrganizationCreate(_OrganizationBase):
    pass

class OrganizationUpdate(_OrganizationBase):
    pass

class Organization(_OrganizationBase):
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
    invite: Any = dict(id="string", user_email="string", user_id="string", user_role="string", organization=org)
    user: str
class AllInvites(BaseModel):
    data: List[InviteBase]

class AcceptInviteResponse(BaseModel):
    invited: OrganizationUserBase
    organization: _OrganizationBase

class RevokedInviteResponse(InviteBase):
    is_revoked: bool = True
    is_deleted: bool = True

class DeclinedInviteResponse(InviteBase):
    is_deleted: bool = True

# END ORGANIZATION INVITE SCHEMAS

# ------------------------------ #

# ORGANIZATION USER SCHEMAS
class OrganizationUsersResponse(BaseModel):
    user: User
    invited: List = list(dict(id="string", first_name="string", last_name="string", email="string", user_id="string", role="string", organization_id="string", date_created="string"))

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