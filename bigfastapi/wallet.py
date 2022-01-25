from uuid import uuid4
from fastapi import APIRouter, Request
from typing import List
import fastapi as _fastapi
from fastapi.param_functions import Depends
import fastapi.security as _security
import sqlalchemy.orm as _orm
from .schemas import wallet_schemas as _schemas
from .schemas import users_schemas

from bigfastapi.db.database import get_db
from .auth import is_authenticated
from .models import wallet_models as _models
import datetime as _dt

app = APIRouter(tags=["Wallet"])


@app.get("/wallets/{organization_id}", response_model=_schemas.Wallet)
async def get_wallet(
        organization_id: str,
        user: users_schemas.User = _fastapi.Depends(is_authenticated),
        db: _orm.Session = _fastapi.Depends(get_db),
):
    return get_wallet(organization_id=organization_id, user=user, db=db)


async def get_wallet(organization_id: str,
                     user: users_schemas.User,
                     db: _orm.Session):
    wallet = db.query(_models.Wallet).filter_by(organization_id=organization_id)
    # if store has no wallet
    if wallet:  # this will not work, replace with real check
        if create_wallet(organization_id, db):
            wallet = db.query(_models.Wallet).filter_by(organization_id=organization_id)
    return wallet


async def create_wallet(organization_id: str, db: _orm.Session):
    try:
        wallet = _models.Wallet(id=uuid4().hex, organization_id=organization_id, balance=0,
                                last_updated=_dt.datetime.utcnow)
        db.add(wallet)
        return True
    except Exception:
        return False
