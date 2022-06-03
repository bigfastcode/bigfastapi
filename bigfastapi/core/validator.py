from bigfastapi.core import messages
from bigfastapi.models import organization_models, customer_models
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

async def validate_organization(org_id:str, db:Session):
    organization = await organization_models.fetchOrganization(orgId=org_id, db=db)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.INVALID_ORGANIZATION)

async def validate_org_member(org_id:str, user_id:str, db:Session):
    is_valid_member = await organization_models.is_organization_member(
        user_id=user_id, organization_id=org_id, db=db)
    if is_valid_member == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.NOT_ORGANIZATION_MEMBER)

async def validate_unique_id(org_id:str, unique_id:str, db:Session, model):
    objects = db.query(model).filter(model.organization_id==org_id).filter(
        model.unique_id==unique_id).all()
    if objects:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=messages.NON_UNIQUE_ID)
