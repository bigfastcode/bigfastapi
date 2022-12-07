import datetime as _dt
import os
from uuid import uuid4

import sqlalchemy.orm as _orm
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean, DateTime, String, Text

from bigfastapi.db.database import Base
from bigfastapi.files import deleteFile, is_file_exist
from bigfastapi.models.contact_info_models import ContactInfo
from bigfastapi.models.location_models import Location


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    user_id = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"))
    # email = Column(String(255), default="")
    # phone_number = Column(String(50), default="")
    # phone_country_code = Column(String(10))
    mission = Column(Text())
    vision = Column(Text())
    currency_code = Column(String(5))
    name = Column(String(255), index=True, default="")
    business_type = Column(String(225), default="retail")
    # country_code = Column(String(255))
    # county = Column(String(225))
    # state = Column(String(255))
    # address = Column(String(255))
    tagline = Column(Text())
    image_url = Column(Text(), default="")
    is_deleted = Column(Boolean(), default=False)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)
    date_created_db = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated_db = Column(DateTime, default=_dt.datetime.utcnow)

    org_contact_infos = relationship(
        "OrganizationContactInfo", backref="organizations", lazy="selectin"
    )
    org_locations = relationship(
        "OrganizationLocation", backref="organizations", lazy="selectin"
    )


# Organization Invite


class OrganizationInvite(Base):
    __tablename__ = "organization_invites"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), ForeignKey("organizations.id"))
    user_id = Column(String(255), ForeignKey("users.id"))
    email = Column(String(255), index=True)
    role_id = Column(String(255), ForeignKey("roles.id"))
    invite_code = Column(String(255), index=True)
    is_accepted = Column(Boolean, default=False)
    is_revoked = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)

    class Config:
        orm_mode = True


# Organization User


class OrganizationUser(Base):
    __tablename__ = "organization_users"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), index=True)
    user_id = Column(String(255), ForeignKey("users.id"))
    role_id = Column(String(255), ForeignKey("roles.id"))
    is_deleted = Column(Boolean, default=False)
    date_created = Column(DateTime, default=_dt.datetime.utcnow)
    last_updated = Column(DateTime, default=_dt.datetime.utcnow)


# Organization Role
class Role(Base):
    __tablename__ = "roles"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), index=True)
    role_name = Column(String(255), index=True)


class OrganizationLocation(Location):
    __tablename__ = "organization_location"
    association_id = Column(
        String(50), primary_key=True, index=True, default=uuid4().hex
    )
    location_id = Column(
        String(50), ForeignKey("locations.id"), index=True, nullable=False
    )
    organization_id = Column(
        String(50), ForeignKey("organizations.id"), index=True, nullable=False
    )

    __mapper_args__ = {
        "polymorphic_identity": "organization_location",
    }


class OrganizationContactInfo(ContactInfo):
    __tablename__ = "organization_contact_info"
    association_id = Column(
        String(50), primary_key=True, index=True, default=uuid4().hex
    )
    contact_info_id = Column(
        String(50), ForeignKey("contact_info.id"), index=True, nullable=False
    )
    organization_id = Column(
        String(255), ForeignKey("organizations.id"), index=True, nullable=False
    )

    __mapper_args__ = {
        "polymorphic_identity": "organization_contact_info",
    }


# --------------------------------------------------------------------------------------------------#
#                                    REPOSITORY AND HELPERS
# --------------------------------------------------------------------------------------------------#


async def fetchOrganization(orgId: str, db: _orm.Session):
    return db.query(Organization).filter(Organization.id == orgId).first()


async def deleteBizImageIfExist(org: Organization):
    if not org:
        return False
    # check if user object contains image endpoint
    if org.image_url != None:
        image_url = org.image_url.strip("/")
        image_folder = os.environ.get("IMAGES_FOLDER", "images")
        image_path = f"/{image_folder}/{image_url}"

        isImageInFile = await is_file_exist(image_path)

        # check if image exist in file prior and delete it
        if isImageInFile:
            deleteRes = await deleteFile(image_path)
            return deleteRes
    return False
