import datetime as _dt
from uuid import uuid4

import fastapi
import sqlalchemy.orm as _orm
from fastapi import APIRouter, status

from bigfastapi.db.database import get_db
from .auth_api import is_authenticated
from .models import organisation_models as organisation_models
from .models import wallet_models as model
from .models import wallet_transaction_models as wallet_transaction_models
from .schemas import users_schemas
from .schemas import wallet_schemas as schema

app = APIRouter(tags=["Wallet"])


@app.post("/wallets", response_model=schema.Wallet)
async def create_wallet(body: schema.WalletCreate,
                        user: users_schemas.User = fastapi.Depends(is_authenticated),
                        db: _orm.Session = fastapi.Depends(get_db)):
    wallet = db.query(model.Wallet).filter_by(organization_id=body.organization_id).first()
    # todo: why is create wallet returning an error?
    # wallet = _create_wallet(organization_id=body.organization_id, db=db)
    if wallet is None:
        wallet = model.Wallet(id=uuid4().hex, organization_id=body.organization_id, balance=0,
                              currency_code=body.currency_code,
                              last_updated=_dt.datetime.utcnow())

        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        return wallet
    else:
        raise fastapi.HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Organization already has a wallet")


@app.get("/wallets/{organization_id}/balance", response_model=schema.Wallet)
async def get_organization_wallet(
        organization_id: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    """Gets the wallet of an organization"""
    return await _get_organization_wallet(organization_id=organization_id, user=user, db=db)


@app.post('/wallets/{organization_id}/fund', response_model=schema.Wallet)
async def fund_wallet(
        organization_id: str,
        body: schema.WalletUpdate,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db)):
    await _get_organization(organization_id=organization_id, db=db, user=user)
    wallet = db.query(model.Wallet).filter_by(organization_id=organization_id).first()
    if wallet is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization does have a wallet")
    else:
        return await _update_wallet(wallet=wallet, amount=body.amount, db=db, currency=body.currency_code)


@app.post('/wallets/{organization_id}/debit', response_model=schema.Wallet)
async def debit_wallet(
        organization_id: str,
        body: schema.WalletUpdate,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db)):
    if body.amount <= 0:
        raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount can not be negative")

    await _get_organization(organization_id=organization_id, user=user, db=db)
    wallet = db.query(model.Wallet).filter_by(organization_id=organization_id).first()

    if wallet is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization does not have a wallet")
    elif wallet.balance - body.amount >= 0:
        return await _update_wallet(wallet, amount=-body.amount, db=db, currency=body.currency_code)
    else:
        raise fastapi.HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient balance in wallet")


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


async def _create_wallet(organization_id: str,
                         db: _orm.Session, currency_code: str):
    wallet = model.Wallet(id=uuid4().hex, organization_id=organization_id, balance=0,
                          last_updated=_dt.datetime.utcnow(), currency_code=currency_code)

    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


async def _get_organization_wallet(organization_id: str,
                                   user: users_schemas.User,
                                   db: _orm.Session):
    # verify if the organization exists under the user's account

    organization = await _get_organization(organization_id=organization_id, db=db, user=user)

    wallet = db.query(model.Wallet).filter_by(organization_id=organization_id).first()
    if wallet is None:
        # todo: why is create wallet returning an error?
        # wallet = _create_wallet(organization_id=body.organization_id, db=db)
        wallet = model.Wallet(id=uuid4().hex, organization_id=organization_id, balance=0,
                              last_updated=_dt.datetime.utcnow(), currency_code=organization.currency)

        db.add(wallet)
        db.commit()
        db.refresh(wallet)

    return wallet


async def _get_wallet(wallet_id: str,
                      user: users_schemas.User,
                      db: _orm.Session):
    wallet = db.query(model.Wallet).filter_by(id=wallet_id).first()
    if wallet is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet does not exist")

    return wallet


async def _update_wallet(wallet, amount: float, db: _orm.Session, currency: str):
    # create a wallet transaction
    wallet_transaction = wallet_transaction_models.WalletTransaction(id=uuid4().hex, wallet_id=wallet.id,
                                                                     currency_code=currency, amount=amount,
                                                                     transaction_date=_dt.datetime.utcnow())
    db.add(wallet_transaction)
    db.commit()
    db.refresh(wallet_transaction)

    # update the wallet
    wallet.balance += amount
    wallet.last_updated = _dt.datetime.utcnow()
    db.commit()
    db.refresh(wallet)
    return wallet
