import datetime as _dt
from uuid import uuid4

import fastapi
import sqlalchemy.orm as _orm
from fastapi import APIRouter
from fastapi_pagination import Page, paginate, add_pagination
from starlette import status

from bigfastapi.db.database import get_db
from .auth_api import is_authenticated
from .models import credit_wallet_models as model, organisation_models, credit_wallet_conversion_models, wallet_models, \
    wallet_transaction_models
from .schemas import credit_wallet_schemas as schema, credit_wallet_conversion_schemas
from .schemas import users_schemas

app = APIRouter(tags=["CreditWallet"], )


@app.post("/credits/{organization_id}/fund", response_model=schema.CreditWalletResponse)
async def add_credit(body: schema.CreditWalletFund,
                     organization_id: str,
                     user: users_schemas.User = fastapi.Depends(is_authenticated),
                     db: _orm.Session = fastapi.Depends(get_db)):
    organization = await _get_organization(organization_id=organization_id, db=db, user=user)
    conversion = await _get_credit_wallet_conversion(currency=body.currency, db=db)
    if conversion is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Currency " + body.currency + " does not have a conversion rate")
    if body.amount <= 0:
        raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Amount must be a positive number")
    credit = db.query(model.CreditWallet).filter_by(organization_id=organization_id).first()
    if credit is None:
        credit = model.CreditWallet(id=uuid4().hex, organization_id=organization_id, amount=body.amount,
                                    type=body.type,
                                    last_updated=_dt.datetime.utcnow())

        db.add(credit)
        db.commit()
        db.refresh(credit)

    await _debit_wallet(organization_id=organization_id, currency=organization.currency, amount=body.amount, db=db)
    credits_to_add = body.amount * conversion.rate
    credit.amount += credits_to_add
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
    conversion = await _get_credit_wallet_conversion(currency=body.currency_code, db=db)
    if conversion is not None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Currency " + body.currency_code + " already has a conversion rate")

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


@app.get("/credits/rates/{currency_code}", response_model=credit_wallet_conversion_schemas.CreditWalletConversion)
async def get_rate(
        currency_code: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    rate = db.query(credit_wallet_conversion_models.CreditWalletConversion).filter_by(
        currency_code=currency_code).first()
    if rate is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Currency " + currency_code + " does not have a conversion rate")

    return rate


############
# Services #
############


async def _debit_wallet(organization_id: str, currency: str, amount: float, db: _orm.Session):
    wallet = await _get_wallet(organization_id=organization_id, db=db)
    if wallet.balance - amount < 0:
        raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient fund in wallet")
    else:
        wallet_transaction = wallet_transaction_models.WalletTransaction(id=uuid4().hex, wallet_id=wallet.id,
                                                                         currency_code=currency,
                                                                         amount=-amount,
                                                                         transaction_date=_dt.datetime.utcnow())
        db.add(wallet_transaction)
        db.commit()
        db.refresh(wallet_transaction)

        # update the wallet
        wallet.balance -= amount
        wallet.last_updated = _dt.datetime.utcnow()
        db.commit()
        db.refresh(wallet)


async def _get_organization(organization_id: str, db: _orm.Session,
                            user: users_schemas.User):
    organization = (
        db.query(organisation_models.Organization)
            .filter_by(creator=user.id)
            .filter(organisation_models.Organization.id == organization_id)
            .first()
    )

    if organization is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization does not exist")

    return organization


async def _get_credit_wallet_conversion(currency: str, db: _orm.Session):
    conversion = (
        db.query(credit_wallet_conversion_models.CreditWalletConversion)
            .filter_by(currency_code=currency)
            .first()
    )

    return conversion


async def _get_wallet(organization_id: str, db: _orm.Session):
    wallet = db.query(wallet_models.Wallet).filter_by(organization_id=organization_id).first()
    if wallet is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization does not have a wallet")

    return wallet


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
