import datetime as _dt
from uuid import uuid4

import fastapi
import sqlalchemy.orm as _orm
from fastapi import APIRouter
from fastapi_pagination import Page, paginate, add_pagination
from starlette import status

from bigfastapi.db.database import get_db
from .auth_api import is_authenticated
from .models import credit_wallet_models as model, organisation_models, credit_wallet_conversion_models
from .schemas import credit_wallet_conversion_schemas as credit_wallet_conversion_schemas
from .schemas import credit_wallet_schemas as schema
from .schemas import users_schemas

app = APIRouter(tags=["CreditWallet"], )


@app.post("/credits/{organization_id}/fund", response_model=schema.CreditWalletResponse)
async def add_credit(body: schema.CreditWalletCreate,
                     organization_id: str,
                     user: users_schemas.User = fastapi.Depends(is_authenticated),
                     db: _orm.Session = fastapi.Depends(get_db)):
    await _get_organization(organization_id=organization_id, db=db, user=user)
    credit = db.query(model.CreditWallet).filter_by(organization_id=organization_id).first()
    if credit is None:
        credit = model.CreditWallet(id=uuid4().hex, organization_id=organization_id, amount=body.amount,
                                    type=body.type,
                                    last_updated=_dt.datetime.utcnow())

        db.add(credit)
        db.commit()
        db.refresh(credit)
    else:
        if body.amount <= 0:
            raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="Amount must be a positive number")

        credit.amount += body.amount
        credit.last_updated = _dt.datetime.utcnow()
        db.commit()
        db.refresh(credit)

    return credit


@app.get("/credits/{organization_id}/balance", response_model=schema.CreditWalletResponse)
async def get_credit(
        organization_id: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    """Gets the credit of an organization"""
    return await _get_credit(organization_id=organization_id, user=user, db=db)


@app.post("/credits/rates", response_model=credit_wallet_conversion_schemas.CreditWalletConversion)
async def add_rate(
        body: credit_wallet_conversion_schemas.CreditWalletConversion,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    rate = credit_wallet_conversion_models.CreditWalletConversion(id=uuid4().hex,
                                                                  credit_wallet_type=body.credit_wallet_type,
                                                                  rate=body.rate,
                                                                  currency_code=body.currency_code)

    db.add(rate)
    db.commit()
    db.refresh(rate)

    return rate


@app.get("/credits/rates", response_model=Page[credit_wallet_conversion_schemas.CreditWalletConversion])
async def get_rates(
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    rates = db.query(credit_wallet_conversion_models.CreditWalletConversion)
    return paginate(list(rates))


############
# Services #
############


async def _get_organization(organization_id: str, db: _orm.Session,
                            user: users_schemas.User = fastapi.Depends(is_authenticated)):
    organization = (
        db.query(organisation_models.Organization)
            .filter_by(creator=user.id)
            .filter(organisation_models.Organization.id == organization_id)
            .first()
    )

    if organization is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization does not exist")

    return organization


async def _get_credit(organization_id: str,
                      user: users_schemas.User,
                      db: _orm.Session):
    # verify if the organization exists under the user's account

    await _get_organization(organization_id=organization_id, user=user, db=db)

    credit = db.query(model.CreditWallet).filter_by(organization_id=organization_id).first()
    if credit is None:
        credit = model.CreditWallet(id=uuid4().hex, organization_id=organization_id, amount=0,
                                    last_updated=_dt.datetime.utcnow())

        db.add(credit)
        db.commit()
        db.refresh(credit)

    return credit


add_pagination(app)
