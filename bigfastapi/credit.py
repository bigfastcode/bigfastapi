import datetime as _dt
import time
from uuid import uuid4

import fastapi
import requests
import sqlalchemy.orm as _orm
import stripe
from decouple import config
from fastapi import APIRouter
from fastapi_pagination import Page, paginate, add_pagination
from sqlalchemy import desc
from starlette import status
from starlette.responses import RedirectResponse

from bigfastapi.db.database import get_db
from .auth_api import is_authenticated
from .models import credit_wallet_models as model, organisation_models, credit_wallet_conversion_models, wallet_models, \
    wallet_transaction_models, credit_wallet_history_models
from .schemas import credit_wallet_schemas as schema, credit_wallet_conversion_schemas
from .schemas import users_schemas
from .schemas.wallet_schemas import PaymentProvider
from .utils.utils import generate_payment_link
from .wallet import update_wallet

app = APIRouter(tags=["CreditWallet"], )


@app.post("/credits/rates", response_model=credit_wallet_conversion_schemas.CreditWalletConversion)
async def add_rate(
        body: credit_wallet_conversion_schemas.CreditWalletConversion,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    if user.is_superuser:
        conversion = await _get_credit_wallet_conversion(currency=body.currency_code, db=db)
        if conversion is not None:
            raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail="Currency " + body.currency_code + " already has a conversion rate")

        rate = credit_wallet_conversion_models.CreditWalletConversion(id=uuid4().hex,
                                                                      rate=body.rate,
                                                                      currency_code=body.currency_code)

        db.add(rate)
        db.commit()
        db.refresh(rate)

        return rate
    else:
        raise fastapi.HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="You are not allowed to perform this request", )


@app.get("/credits/rates", response_model=Page[credit_wallet_conversion_schemas.CreditWalletConversion])
async def get_rates(
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    rates = db.query(credit_wallet_conversion_models.CreditWalletConversion)
    return paginate(list(rates))


@app.get("/credits/rates/{currency}", response_model=credit_wallet_conversion_schemas.CreditWalletConversion)
async def get_rate(
        currency: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    rate = db.query(credit_wallet_conversion_models.CreditWalletConversion).filter_by(
        currency_code=currency).first()
    if rate is None:
        freeCurrencyApiKey = config("FREECURRENCY_API_KEY")
        if freeCurrencyApiKey.strip() == '':
            raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail="Currency " + currency + " does not have a conversion rate")
        else:
            rate = await _get_market_rate(currency=currency, db=db)

    return rate


@app.put("/credits/rates/{currency}", response_model=credit_wallet_conversion_schemas.CreditWalletConversion)
async def update_rate(
        currency: str,
        body: credit_wallet_conversion_schemas.UpdateCreditWalletConversion,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    rate = db.query(credit_wallet_conversion_models.CreditWalletConversion).filter_by(
        currency_code=currency).first()
    if rate is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Currency " + currency + " does not have a conversion rate")
    else:
        rate.rate = body.rate
        db.commit()
        db.refresh(rate)

        return rate


@app.get("/credits/callback/stripe")
async def verify_stripe_payment(status: str, tx_ref: str, transaction_id: str,
                                db: _orm.Session = fastapi.Depends(get_db)):
    stripe.api_key = config('STRIPE_SEC_KEY')
    session = stripe.checkout.Session.retrieve(transaction_id)
    frontendUrl = session.metadata.redirect_url
    if status == 'successful' and session.url is None:
        rootUrl = config('API_URL')
        retryLink = rootUrl + '/credits/callback&tx_ref=' + tx_ref + '&transaction_id=' + transaction_id
        ref = session.client_reference_id
        wallet_transaction = db.query(wallet_transaction_models.WalletTransaction).filter_by(id=ref).first()
        if wallet_transaction is not None:
            ref = wallet_transaction.transaction_ref

            if wallet_transaction.status:
                response = RedirectResponse(
                    url=frontendUrl + '?status=error&message=Transaction already processed')
                return response

            user_id, organization_id, _ = ref.split('-')
            amount = session.amount_total
            currency = session.currency.upper()
            wallet = await _get_wallet(organization_id=organization_id, currency=currency, db=db)
            if currency == "NGN":
                amount /= 100

            try:
                # add money to wallet
                await update_wallet(wallet=wallet, amount=amount, db=db, currency=currency,
                                    wallet_transaction_id=wallet_transaction.id,
                                    reason="Stripe: " + currency + " " + str(amount) + " Top Up")

                conversion = await _get_credit_wallet_conversion(currency=currency, db=db)
                credits_to_add = round(amount / conversion.rate)

                # debit money from wallet to buy credits
                reference = str(credits_to_add) + ' credits Top Up'
                await update_wallet(wallet=wallet, amount=-amount, db=db, currency=currency,
                                    reason=organization_id + ": " + reference)

                # update credit here
                await _update_credit_wallet(organization_id=organization_id, reference=reference,
                                            credits_to_add=credits_to_add,
                                            db=db)

                response = RedirectResponse(url=frontendUrl + '?status=success&message=Credit refilled')
                return response
            except fastapi.HTTPException:
                response = RedirectResponse(
                    url=frontendUrl + '?status=error&message=An error occurred while refilling your credit. '
                                      'Please try again&link=' + retryLink)
                return response


        else:
            response = RedirectResponse(
                url=frontendUrl + '?status=error&message=Transaction not found Please try again&link=' + retryLink)
            return response

    else:
        response = RedirectResponse(url=frontendUrl + '?status=error&message=Payment was not successful')
        return response


@app.get("/credits/callback/flutterwave")
async def verify_flutterwave_payment(
        status: str,
        tx_ref: str,
        transaction_id='',
        db: _orm.Session = fastapi.Depends(get_db),
):
    frontendUrl = config("FRONTEND_URL")
    if status == 'successful':
        flutterwaveKey = config('FLUTTERWAVE_SEC_KEY')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + flutterwaveKey}
        url = 'https://api.flutterwave.com/v3/transactions/' + transaction_id + '/verify'
        verificationRequest = requests.get(url, headers=headers)
        rootUrl = config('API_URL')
        retryLink = rootUrl + '/credits/callback&tx_ref=' + tx_ref
        retryLink += '' if transaction_id == '' else ('&transaction_id=' + transaction_id)
        if verificationRequest.status_code == 200:
            jsonResponse = verificationRequest.json()
            ref = jsonResponse['data']['tx_ref']
            frontendUrl = jsonResponse['data']['meta']['redirect_url']
            wallet_transaction = db.query(wallet_transaction_models.WalletTransaction).filter_by(id=ref).first()
            if wallet_transaction is not None:
                ref = wallet_transaction.transaction_ref

                if wallet_transaction.status:
                    response = RedirectResponse(
                        url=frontendUrl + '?status=error&message=Transaction already processed')
                    return response

                if jsonResponse['status'] == 'success' and jsonResponse['data']['status'] == 'successful':
                    user_id, organization_id, _ = ref.split('-')
                    amount = jsonResponse['data']['amount']
                    currency = jsonResponse['data']['currency']
                    wallet = await _get_wallet(organization_id=organization_id, currency=currency, db=db)

                    try:
                        # add money to wallet
                        await update_wallet(wallet=wallet, amount=amount, db=db, currency=currency,
                                            wallet_transaction_id=wallet_transaction.id,
                                            reason="Flutterwave: " + currency + " " + str(amount) + " Top Up")

                        conversion = await _get_credit_wallet_conversion(currency=currency, db=db)
                        credits_to_add = round(amount / conversion.rate)

                        # debit money from wallet to buy credits
                        reference = str(credits_to_add) + ' credits Top Up'
                        await update_wallet(wallet=wallet, amount=-amount, db=db, currency=currency,
                                            reason=organization_id + ": " + reference)

                        # update credit here
                        await _update_credit_wallet(organization_id=organization_id, reference=reference,
                                                    credits_to_add=credits_to_add,
                                                    db=db)

                        response = RedirectResponse(url=frontendUrl + '?status=success&message=Credit refilled')
                        return response
                    except fastapi.HTTPException:
                        response = RedirectResponse(
                            url=frontendUrl + '?status=error&message=An error occurred while refilling your credit. '
                                              'Please try again&link=' + retryLink)
                        return response

                else:
                    response = RedirectResponse(url=frontendUrl + '?status=error&message=Transaction not found')
                    return response
            else:
                response = RedirectResponse(url=frontendUrl + '?status=error&message=Transaction not found')
                return response

        response = RedirectResponse(
            url=frontendUrl + '?status=error&message=An error occurred. Please try again&link=' + retryLink)
        return response

    else:
        response = RedirectResponse(url=frontendUrl + '?status=error&message=Payment was not successful')
        return response


@app.get("/credits/{organization_id}", response_model=schema.CreditWalletResponse)
async def get_credit(
        organization_id: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    """Gets the credit of an organization"""
    return await _get_credit(organization_id=organization_id, user=user, db=db)


@app.post("/credits/{organization_id}", response_model=schema.CreditWalletFundResponse)
async def add_credit(body: schema.CreditWalletFund,
                     organization_id: str,
                     user: users_schemas.User = fastapi.Depends(is_authenticated),
                     db: _orm.Session = fastapi.Depends(get_db)):
    """Creates and returns a payment link"""
    await _get_organization(organization_id=organization_id, db=db, user=user)
    conversion = await _get_credit_wallet_conversion(currency=body.currency, db=db)
    if conversion is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Currency " + body.currency + " does not have a conversion rate")
    if body.amount <= 0:
        raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Amount must be a positive number")
    wallet = db.query(wallet_models.Wallet).filter_by(organization_id=organization_id).filter_by(
        currency_code=body.currency).first()
    if wallet is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization does not have a wallet")
    else:
        # prevents two payments with same transaction reference
        # uniqueStr = ''.join([random.choice("qwertyuiopasdfghjklzxcvbnm1234567890") for x in range(10)])
        uniqueStr = time.time()
        txRef = user.id + "-" + organization_id + "-" + str(uniqueStr)
        rootUrl = config('API_URL')
        # create transaction
        transaction_id = uuid4().hex
        wallet_transaction = wallet_transaction_models.WalletTransaction(id=transaction_id, wallet_id=wallet.id,
                                                                         currency_code=body.currency,
                                                                         amount=body.amount,
                                                                         transaction_date=_dt.datetime.utcnow(),
                                                                         transaction_ref=txRef)
        db.add(wallet_transaction)
        db.commit()
        db.refresh(wallet_transaction)

        redirectUrl = rootUrl + '/credits/callback'
        amount = body.amount
        if body.provider == PaymentProvider.STRIPE:
            redirectUrl += '/stripe'
            if body.currency.upper() == "NGN":
                amount *= 100
        else:
            redirectUrl += '/flutterwave'
        link = await generate_payment_link(front_end_redirect_url=body.redirect_url, api_redirect_url=redirectUrl,
                                           user=user,
                                           amount=amount,
                                           currency=body.currency, tx_ref=transaction_id, provider=body.provider)
        return {"link": link}


@app.get("/credits/{organization_id}/history", response_model=Page[schema.CreditWalletHistory])
async def get_credit_history(
        organization_id: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db)):
    """Returns credit wallet history"""
    credit = await _get_credit(organization_id=organization_id, user=user, db=db)
    history = db.query(credit_wallet_history_models.CreditWalletHistory).filter_by(credit_wallet_id=credit.id).order_by(
        desc(credit_wallet_history_models.CreditWalletHistory.date))
    return paginate(list(history))


############
# Services #
############

async def _update_credit_wallet(organization_id: str, credits_to_add: int, reference: str, db: _orm.Session):
    credit = db.query(model.CreditWallet).filter_by(organization_id=organization_id).first()

    credit.amount += credits_to_add
    credit.last_updated = _dt.datetime.utcnow()
    db.commit()
    db.refresh(credit)

    credit_wallet_history = credit_wallet_history_models.CreditWalletHistory(id=uuid4().hex,
                                                                             credit_wallet_id=credit.id,
                                                                             amount=credits_to_add,
                                                                             date=_dt.datetime.utcnow(),
                                                                             reference=reference)
    db.add(credit_wallet_history)
    db.commit()
    db.refresh(credit_wallet_history)


async def _get_market_rate(currency: str, db: _orm.Session):
    currency = currency.upper()

    freeCurrencyApiKey = config("FREECURRENCY_API_KEY")
    url = 'https://freecurrencyapi.net/api/v2/latest?apikey=' + freeCurrencyApiKey
    response = requests.get(url)
    if response.status_code == 200:
        jsonResponse = response.json()
        rates = jsonResponse['data']
        rates['USD'] = 1
        if currency in rates:
            rate = jsonResponse['data'][currency]
            conversion_rate = credit_wallet_conversion_models.CreditWalletConversion(id=uuid4().hex,
                                                                                     rate=rate,
                                                                                     currency_code=currency)

            db.add(conversion_rate)
            db.commit()
            db.refresh(conversion_rate)

            return conversion_rate

    raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Could not get exchange rate. Please try again later")


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


async def _get_wallet(organization_id: str, currency: str, db: _orm.Session):
    wallet = db.query(wallet_models.Wallet).filter_by(organization_id=organization_id).filter_by(
        currency_code=currency).first()
    if wallet is None:
        wallet = wallet_models.Wallet(id=uuid4().hex, organization_id=organization_id, balance=0,
                                      currency_code=currency,
                                      last_updated=_dt.datetime.utcnow())

        db.add(wallet)
        db.commit()
        db.refresh(wallet)

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
