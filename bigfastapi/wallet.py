from uuid import uuid4
from fastapi import APIRouter, Request
import fastapi as _fastapi
from decouple import config

import sqlalchemy.orm as _orm
from .schemas import wallet_schemas as _schemas
from .schemas import users_schemas
from . import organization

from bigfastapi.db.database import get_db
from .auth import is_authenticated
from .models import wallet_models as _models
import datetime as _dt
import requests

from .utils.utils import PaymentProvider

app = APIRouter(tags=["Wallet"])


@app.get("/wallets/{organization_id}", response_model=_schemas.Wallet)
async def get_wallet(
        organization_id: str,
        user: users_schemas.User = _fastapi.Depends(is_authenticated),
        db: _orm.Session = _fastapi.Depends(get_db),
):
    """Gets the wallet of an organization"""
    return await _get_wallet(organization_id=organization_id, user=user, db=db)


############
# Services #
############
async def _get_wallet(organization_id: str,
                      user: users_schemas.User,
                      db: _orm.Session):
    # verify if the organization exists under the user's account
    try:
        await organization.get_organization(organization_id=organization_id, user=user, db=db)
    except _fastapi.HTTPException:
        raise _fastapi.HTTPException(status_code=404, detail="Organization does not exist")

    wallet = db.query(_models.Wallet).filter_by(organization_id=organization_id).first()
    if wallet is None:
        raise _fastapi.HTTPException(status_code=404, detail="Organization does not have a wallet")

    return wallet


async def create_wallet(organization_id: str, db: _orm.Session):
    wallet = _models.Wallet(id=uuid4().hex, organization_id=organization_id, balance=0,
                            last_updated=_dt.datetime.utcnow())
    db.add(wallet)
    db.commit()
    db.refresh(wallet)


async def _update_wallet(wallet, amount: float, db: _orm.Session):
    wallet.balance += amount
    wallet.last_updated = _dt.datetime.utcnow()
    db.commit()
    db.refresh(wallet)
    return wallet


async def debit_wallet(wallet_id: str, amount: float, db: _orm.Session):
    wallet = db.query(_models.Wallet).filter_by(id=wallet_id).first()
    if wallet is None:
        raise _fastapi.HTTPException(status_code=404, detail="Wallet does not exist")

    if wallet.balance - amount >= 0:
        return await _update_wallet(wallet, amount=-amount, db=db)
    else:
        raise _fastapi.HTTPException(status_code=403, detail="Insufficient balance in wallet")


async def fund_wallet(wallet_id: str, amount: float, transaction_id: str, db: _orm.Session,
                      payment_provider: PaymentProvider):
    if payment_provider is PaymentProvider.FLUTTERWAVE:
        flutterwaveKey = config('FLUTTERWAVE_SEC_KEY')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + flutterwaveKey}
        url = 'https://api.flutterwave.com/v3/transactions/' + transaction_id + '/verify'
        verificationRequest = requests.get(url, headers=headers)
        jsonResponse = verificationRequest.json()
        if jsonResponse['status'] == 'pending':
            raise _fastapi.HTTPException(status_code=402, detail="Transaction is pending")
        elif jsonResponse['status'] == 'success':
            if amount == jsonResponse['data']['amount']:
                wallet = db.query(_models.Wallet).filter_by(id=wallet_id).first()
                if wallet is None:
                    raise _fastapi.HTTPException(status_code=404, detail="Wallet does not exist")

                return await _update_wallet(wallet=wallet, amount=amount, db=db)
            else:
                raise _fastapi.HTTPException(status_code=400, detail="Transaction details do not match")
        else:
            raise _fastapi.HTTPException(status_code=404, detail="Transaction not successful")
    else:
        raise _fastapi.HTTPException(status_code=404, detail="Payment method not supported")
