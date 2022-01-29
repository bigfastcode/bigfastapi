from uuid import uuid4

import requests
from fastapi import APIRouter, Request, status
import fastapi
from decouple import config

import sqlalchemy.orm as _orm
from .schemas import wallet_schemas as schema
from .schemas import users_schemas
from . import organization

from bigfastapi.db.database import get_db
from .auth import is_authenticated
from .models import wallet_models as model
import datetime as _dt
app = APIRouter(tags=["Wallet"])


@app.post("/wallets", response_model=schema.Wallet)
async def create_wallet(body: schema.WalletCreate,
                        user: users_schemas.User = fastapi.Depends(is_authenticated),
                        db: _orm.Session = fastapi.Depends(get_db)):
    wallet = db.query(model.Wallet).filter_by(organization_id=body.organization_id).first()
    if wallet is None:
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


@app.get("/wallets/organization/{organization_id}", response_model=schema.Wallet)
async def get_organization_wallet(
        organization_id: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    """Gets the wallet of an organization"""
    return await _get_organization_wallet(organization_id=organization_id, user=user, db=db)


@app.post('/wallets/{wallet_id}/debit', response_model=schema.Wallet)
async def debit_wallet(wallet_id: str,
                       body: schema.WalletUpdate, user: users_schemas.User = fastapi.Depends(is_authenticated),
                       db: _orm.Session = fastapi.Depends(get_db)):
    return await _debit_wallet(wallet_id=wallet_id, amount=body.amount, db=db, )


@app.post('/wallets/{wallet_id}/fund', response_model=schema.Wallet)
async def fund_wallet(
        wallet_id: str,
        body: schema.WalletFund,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db)):
    return await _fund_wallet(wallet_id=wallet_id, amount=body.amount, transaction_id=body.ref, db=db,
                              payment_provider=body.provider)


@app.delete('/wallets/{wallet_id}')
async def delete_wallet(
        wallet_id: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db)):
    wallet = await _get_wallet(wallet_id=wallet_id, user=user, db=db)
    db.delete(wallet)
    db.commit()
    return "deleted"


############
# Services #
############
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
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization does not have a wallet")

    return wallet


async def _get_wallet(wallet_id: str,
                      user: users_schemas.User,
                      db: _orm.Session):
    wallet = db.query(model.Wallet).filter_by(id=wallet_id).first()
    if wallet is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet does not exist")

    return wallet


async def _update_wallet(wallet, amount: float, db: _orm.Session):
    wallet.balance += amount
    wallet.last_updated = _dt.datetime.utcnow()
    db.commit()
    db.refresh(wallet)
    return wallet


async def _debit_wallet(wallet_id: str, amount: float, db: _orm.Session):
    if amount <= 0:
        raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount can not be negative")

    wallet = db.query(model.Wallet).filter_by(id=wallet_id).first()
    if wallet is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet does not exist")

    if wallet.balance - amount >= 0:
        return await _update_wallet(wallet, amount=-amount, db=db)
    else:
        raise fastapi.HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient balance in wallet")


async def _fund_wallet(wallet_id: str, amount: float, transaction_id: str, db: _orm.Session,
                       payment_provider: schema.PaymentProvider):
    if amount <= 0:
        raise fastapi.HTTPException(status_code=400, detail="Amount can not be negative")

    if payment_provider is schema.PaymentProvider.FLUTTERWAVE:
        flutterwaveKey = config('FLUTTERWAVE_SEC_KEY')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + flutterwaveKey}
        url = 'https://api.flutterwave.com/v3/transactions/' + transaction_id + '/verify'
        verificationRequest = requests.get(url, headers=headers)
        jsonResponse = verificationRequest.json()
        if jsonResponse['data']['status'] == 'pending':
            raise fastapi.HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Transaction is pending")
        elif jsonResponse['data']['status'] == 'successful':
            if amount == jsonResponse['data']['amount']:
                wallet = db.query(model.Wallet).filter_by(id=wallet_id).first()
                if wallet is None:
                    raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet does not exist")

                return await _update_wallet(wallet=wallet, amount=amount, db=db)
            else:
                raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                            detail="Transaction details do not match")
        elif jsonResponse['status'] == 'error':
            raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        else:
            raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not successful")
    else:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment method not supported")
