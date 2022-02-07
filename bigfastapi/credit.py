import datetime as _dt
from uuid import uuid4

import fastapi
import sqlalchemy.orm as _orm
from fastapi import APIRouter, status

from bigfastapi.db.database import get_db
from . import organization
from .auth_api import is_authenticated
from .models import credit_models as model
from .schemas import credit_schemas as schema
from .schemas import users_schemas

app = APIRouter(tags=["Credit"])


@app.post("/credits", response_model=schema.Credit)
async def add_credit(body: schema.Credit,
                     user: users_schemas.User = fastapi.Depends(is_authenticated),
                     db: _orm.Session = fastapi.Depends(get_db)):
    credit = db.query(model.Credit).filter_by(organization_id=body.organization_id).first()
    if credit is None:
        credit = model.Credit(id=uuid4().hex, organization_id=body.organization_id, amount=body.amount,
                              last_updated=_dt.datetime.utcnow())

        db.add(credit)
        db.commit()
        db.refresh(credit)
    else:
        credit.amount += body.amount
        credit.last_updated = _dt.datetime.utcnow()
        db.commit()
        db.refresh(credit)


# @app.get("/credits/organization/{organization_id}", response_model=schema.CreditResponse)
# response_model=schema.CreditResponse is giving errors todo: find out why
@app.get("/credits/organization/{organization_id}")
async def get_credit(
        organization_id: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    """Gets the credit of an organization"""
    return await _get_credit(organization_id=organization_id, user=user, db=db)


############
# Services #
############


async def _get_credit(organization_id: str,
                      user: users_schemas.User,
                      db: _orm.Session):
    # verify if the organization exists under the user's account
    try:
        await organization.get_organization(organization_id=organization_id, user=user, db=db)
    except fastapi.HTTPException:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization does not exist")

    credit = db.query(model.Credit).filter_by(organization_id=organization_id).first()
    if credit is None:
        credit = model.Credit(id=uuid4().hex, organization_id=organization_id, amount=0,
                              last_updated=_dt.datetime.utcnow())

        db.add(credit)
        db.commit()
        db.refresh(credit)

    return credit


async def _update_credit(credit, amount: float, db: _orm.Session):
    credit.amount += amount
    credit.last_updated = _dt.datetime.utcnow()
    db.commit()
    db.refresh(credit)
    return credit


async def debit_credit(organization_id: str,
                       amount: float, db: _orm.Session, user: users_schemas.User = fastapi.Depends(is_authenticated)):
    if amount <= 0:
        raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount can not be negative")

        # verify if the organization exists under the user's account
    try:
        await organization.get_organization(organization_id=organization_id, user=user, db=db)
    except fastapi.HTTPException:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization does not exist")

    credit = _get_credit(organization_id=organization_id, db=db, user=user)

    if credit.amount - amount >= 0:
        return await _update_credit(credit, amount=-amount, db=db)
    else:
        raise fastapi.HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient credit balance")
