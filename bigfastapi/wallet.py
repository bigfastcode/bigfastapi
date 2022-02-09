import datetime as _dt
from uuid import uuid4

import fastapi
import sqlalchemy.orm as _orm
from fastapi import APIRouter, status

from bigfastapi.db.database import get_db
from . import organization
from .auth_api import is_authenticated
from .models import wallet_models as model
from .schemas import users_schemas
from .schemas import wallet_schemas as schema

app = APIRouter(tags=["Wallet"])


@app.post("/wallets", response_model=schema.Wallet)
async def create_wallet(body: schema.WalletCreate,
                        user: users_schemas.User = fastapi.Depends(is_authenticated),
                        db: _orm.Session = fastapi.Depends(get_db)):
    wallet = db.query(model.Wallet).filter_by(organization_id=body.organization_id).first()
    if wallet is None:
        # todo: why is create wallet returning an error?
        # wallet = _create_wallet(organization_id=body.organization_id, db=db)
        wallet = model.Wallet(id=uuid4().hex, organization_id=body.organization_id, balance=0,
                              last_updated=_dt.datetime.utcnow())

        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        return wallet
    else:
        raise fastapi.HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Organization already has a wallet")


@app.get("/wallets/{wallet_id}", response_model=schema.Wallet)
async def get_wallet(
        wallet_id: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    """Gets a wallet"""
    return await _get_wallet(wallet_id=wallet_id, user=user, db=db)


@app.get("/wallets/{organization_id}/balance", response_model=schema.Wallet)
async def get_organization_wallet(
        organization_id: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    """Gets the wallet of an organization"""
    return await _get_organization_wallet(organization_id=organization_id, user=user, db=db)


############
# Services #
############

async def _create_wallet(organization_id: str,
                         db: _orm.Session):
    wallet = model.Wallet(id=uuid4().hex, organization_id=organization_id, balance=0,
                          last_updated=_dt.datetime.utcnow())

    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


async def _get_organization_wallet(organization_id: str,
                                   user: users_schemas.User,
                                   db: _orm.Session):
    # verify if the organization exists under the user's account
    try:
        await organization.get_organization(organization_id=organization_id, user=user, db=db)
    except fastapi.HTTPException:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization does not exist")

    wallet = db.query(model.Wallet).filter_by(organization_id=organization_id).first()
    if wallet is None:
        # todo: why is create wallet returning an error?
        # wallet = _create_wallet(organization_id=body.organization_id, db=db)
        wallet = model.Wallet(id=uuid4().hex, organization_id=organization_id, balance=0,
                              last_updated=_dt.datetime.utcnow())

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
