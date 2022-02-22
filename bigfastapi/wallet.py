import datetime as _dt
import random
from uuid import uuid4

import fastapi
import requests
import sqlalchemy.orm as _orm
from decouple import config
from fastapi import APIRouter, status
from starlette.responses import RedirectResponse

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


@app.get("/wallets/callback")
async def verify_wallet_transaction(
        status: str,
        tx_ref: str,
        transaction_id: str,
        db: _orm.Session = fastapi.Depends(get_db),
):
    frontendUrl = config("FRONTEND_URL") + '/credits'
    if status == 'successful':
        flutterwaveKey = config('FLUTTERWAVE_SEC_KEY')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + flutterwaveKey}
        url = 'https://api.flutterwave.com/v3/transactions/' + transaction_id + '/verify'
        verificationRequest = requests.get(url, headers=headers)
        if verificationRequest.status_code == 200:
            jsonResponse = verificationRequest.json()
            if jsonResponse['status'] == 'success':
                if jsonResponse['data']['status'] == 'successful':
                    user_id, organization_id, _ = tx_ref.split('-')
                    amount = jsonResponse['data']['amount']
                    currency = jsonResponse['data']['currency']
                    wallet = db.query(model.Wallet).filter_by(organization_id=organization_id).first()
                    if wallet is None:
                        response = RedirectResponse(url=frontendUrl + '?status=error&message=Wallet does not exist')
                        return response
                    try:
                        await _update_wallet(wallet=wallet, amount=amount, db=db, currency=currency)
                    except fastapi.HTTPException:
                        response = RedirectResponse(
                            url=frontendUrl + '?status=error&message=An error occurred while refilling your wallet. Please try again')
                        return response

                    response = RedirectResponse(url=frontendUrl + '?status=success&message=Wallet refilled')
                    return response

                else:
                    response = RedirectResponse(url=frontendUrl + '?status=error&message=Transaction not found')
                    return response

        response = RedirectResponse(
            url=frontendUrl + '?status=error&message=An error occurred. Please try again')
        return response

    else:
        response = RedirectResponse(url=frontendUrl + '?status=error&message=Payment was not successful')
        return response


@app.post('/wallets/{organization_id}/fund')
async def fund_wallet(
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
    else:
        return await _generate_payment_link(organization_id=organization_id, user=user, amount=body.amount,
                                            currency=body.currency_code)


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


async def _generate_payment_link(organization_id: str,
                                 user: users_schemas.User, currency: str,
                                 amount: float):
    flutterwaveKey = config('FLUTTERWAVE_SEC_KEY')
    rootUrl = config('API_URL')
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + flutterwaveKey}
    url = 'https://api.flutterwave.com/v3/payments/'
    # prevents two payments with same transaction reference
    uniqueStr = ''.join([random.choice("qwertyuiopasdfghjklzxcvbnm1234567890") for x in range(10)])
    txRef = user.id + "-" + organization_id + "-wallet" + uniqueStr
    data = {
        "tx_ref": txRef,
        "amount": amount,
        "currency": currency,
        "redirect_url": rootUrl + '/wallets/callback',
        "customer": {
            "email": user.email,
            "phonenumber": user.phone_number,
            "name": user.first_name + " " + user.last_name
        },
        "customizations": {
            "description": 'Keep track of your debtors',
            "logo": 'https://customerpay.me/frontend/assets/img/favicon.png',
            "title": "CustomerPayMe",
        }}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        jsonResponse = response.json()
        link = (jsonResponse.get('data'))['link']
        return link
    else:
        raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="An error occurred. Please try again later")


async def _fund_walle2t(wallet_id: str, amount: float, transaction_id: str, db: _orm.Session,
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
