import datetime as _dt
import os
from typing import Optional
from uuid import uuid4

import fastapi as _fastapi
from fastapi.responses import JSONResponse
import sqlalchemy.orm as orm
from decouple import config
from fastapi import APIRouter, HTTPException, status
from fastapi import BackgroundTasks
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import and_

from bigfastapi.db.database import get_db
from bigfastapi.email import send_email
from bigfastapi.models import organization_models
from bigfastapi.services.menu_service import add_default_menu_list, get_organization_menu

from bigfastapi.auth_api import is_authenticated
from bigfastapi.core.helpers import Helpers
from bigfastapi.files import upload_image
from bigfastapi.models import credit_wallet_models as credit_wallet_models
from bigfastapi.schemas import organization_schemas as _schemas
from bigfastapi.schemas.organization_schemas import _OrganizationBase, AddRole, OrganizationUserBase
from bigfastapi.models.organization_models import OrganizationInvite, OrganizationUser, Role
from bigfastapi.models import organization_models as _models
from bigfastapi.models import user_models
from bigfastapi.models import user_models
from bigfastapi.models import wallet_models as wallet_models
from bigfastapi.schemas import users_schemas
from bigfastapi.utils.utils import paginate_data, row_to_dict

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
