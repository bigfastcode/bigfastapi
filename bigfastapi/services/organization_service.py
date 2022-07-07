from uuid import uuid4
from bigfastapi.models import credit_wallet_models as credit_wallet_models
from bigfastapi.schemas import organization_schemas as _schemas
from bigfastapi.models import organization_models as _models
from sqlalchemy import orm
from bigfastapi.models import wallet_models as wallet_models
from bigfastapi.schemas import users_schemas


def create_organization(user: users_schemas.User, db: orm.Session, organization: _schemas.OrganizationCreate):
    organization_id = uuid4().hex
    newOrganization = _models.Organization(id=organization_id, user_id=user.id, mission=organization.mission,
                                           vision=organization.vision, name=organization.name,
                                           business_type=organization.business_type,
                                           tagline=organization.tagline, image_url=organization.image_url, is_deleted=False,
                                           currency_code=organization.currency_code)

    db.add(newOrganization)
    db.commit()
    db.refresh(newOrganization)
    return newOrganization
