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
from bigfastapi import models

from bigfastapi.db.database import get_db
from bigfastapi.services.auth_service import is_authenticated
from bigfastapi.core.helpers import Helpers
from bigfastapi.models import credit_wallet_models as model, organization_models, wallet_models
from bigfastapi.schemas import credit_wallet_schemas as schema, credit_wallet_conversion_schemas
from bigfastapi.schemas import users_schemas
from bigfastapi.schemas.wallet_schemas import PaymentProvider
from bigfastapi.utils.utils import generate_payment_link
from bigfastapi.wallet import update_wallet

app = APIRouter(tags=["CreditWallet"], )


@app.post("/credits/rates", response_model=credit_wallet_conversion_schemas.CreditWalletConversion)
async def add_rate(
        body: credit_wallet_conversion_schemas.CreditWalletConversion,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    """intro-->This endpoint allows a super user to add a credit rate. To use this endpoint you need to make a post request to the /credits/rates endpoint

        reqBody-->rate: This is the value of the credit rate
        reqBody-->currency_code: This is the short code of the currency of interest

    returnDesc--> On sucessful request, it returns  
        returnBody--> details of the newly created credit rate
    """
    if user.is_superuser:
        conversion = await _get_credit_wallet_conversion(currency=body.currency_code, db=db)
        if conversion is not None:
            raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail="Currency " + body.currency_code.upper() + " already has a conversion rate")

        rate = model.CreditWalletConversion(id=uuid4().hex,
                                                                      rate=body.rate,
                                                                      currency_code=body.currency_code.upper())

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
    """intro-->This endpoint allows you to retrieve all available credit rates. To use this endpoint you need to make a get request to the /credits/rates endpoint

        ParamDesc-->On get request, the request url takes two(2) optional query parameters
            param-->page: This is the page of interest, this is 1 by default
            param-->size: This is the size per page, this is 10 by default

    returnDesc--> On sucessful request, it returns  
        returnBody--> a list of all available credit rates
    """
    rates = db.query(model.CreditWalletConversion)
    return paginate(list(rates))


@app.get("/credits/rates/{currency}", response_model=credit_wallet_conversion_schemas.CreditWalletConversion)
async def get_rate(
        currency: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    """intro-->This endpoint allows you to retrieve the credit rate for a particular currency. To use this endpoint you need to make a get request to the /credits/rates/{currency} endpoint

        ParamDesc-->On get request, the request url takes the parameter, currency
            param-->currency: This is the currency of interest

    returnDesc--> On sucessful request, it returns
        returnBody--> the details of the queried currency
    """
    rate = db.query(model.CreditWalletConversion).filter_by(
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
    """intro-->This endpoint allows you to update the credit rate for a particular currency. To use this endpoint you need to make a put request to the /credits/rates/{currency} endpoint

        ParamDesc-->On get request, the request url takes the parameter, currency
            param-->currency: This is the currency of interest

            reqBody-->rate: This is the credit rate of the currency to be updated

    returnDesc--> On sucessful request, it returns
        returnBody--> the details of the updated rate
    """
    rate = db.query(model.CreditWalletConversion).filter_by(
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
    """intro-->This endpoint allows you to verify a stripe payment. To use this endpoint you need to make a get request to the /credits/callback/stripe endpoint

        ParamDesc-->On get request, the request url takes three(3) query parameters
            param-->status: This is the the status of the payment
            param-->tx_ref: This is the transaction reference 
            param-->transaction_id: This is the unique id of the transaction

    returnDesc--> On sucessful request, it returns the
        returnBody--> details of the transacation
    """
    stripe.api_key = config('STRIPE_SEC_KEY')
    session = stripe.checkout.Session.retrieve(transaction_id)
    frontendUrl = session.metadata.redirect_url
    if status == 'successful' and session.url is None:
        rootUrl = config('API_URL')
        retryLink = rootUrl + '/credits/callback&tx_ref=' + tx_ref + '&transaction_id=' + transaction_id
        ref = session.client_reference_id
        wallet_transaction = db.query(wallet_models.WalletTransaction).filter_by(id=ref).first()
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
    """intro-->This endpoint allows you to verify a flutterwave payment. To use this endpoint you need to make a get request to the /credits/callback/flutterwave endpoint

        ParamDesc-->On get request, the request url takes three(3) query parameters
            param-->status: This is the the status of the payment
            param-->tx_ref: This is the transaction reference 
            param-->transaction_id: This is the unique id of the transaction

    returnDesc--> On sucessful request, it returns the
        returnBody--> details of the transacation
    """
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
            wallet_transaction = db.query(wallet_models.WalletTransaction).filter_by(id=ref).first()
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
    """intro-->This endpoint allows you to retrieve the credit  detail for a particular organization. To use this endpoint you need to make a get request to the /credits/{organization_id} endpoint

        ParamDesc-->On get request, the request url takes the parameter, organization id
            param-->organization_id: This is the unique id of the organization
            

    returnDesc--> On sucessful request, it returns
        returnBody--> the details of the queried organization's credit
    """
    return await _get_credit(organization_id=organization_id, user=user, db=db)


@app.post("/credits/{organization_id}", response_model=schema.CreditWalletFundResponse)
async def add_credit(body: schema.CreditWalletFund,
                     organization_id: str,
                     user: users_schemas.User = fastapi.Depends(is_authenticated),
                     db: _orm.Session = fastapi.Depends(get_db)):
    """intro-->This endpoint allows you to add a credit detail for a particular organization, on creation it returns a payment link. To use this endpoint you need to make a post request to the /credits/{organization_id} endpoint with a specified body of request

        ParamDesc-->On get request, the request url takes the parameter, organization id
            param-->organization_id: This is the unique id of the organization
            
            reqBody-->currency: This is the currency of the credit detail
            reqBody-->amount: This is the amount/value of the credit action
            reqBody-->provider: This is the payment provider for the credit action
            reqBody-->redirect_url: This is the redirect url to the payment provider platform

    returnDesc--> On sucessful request, it returns 
        returnBody--> a payment link
    """
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
        wallet_transaction = wallet_models.WalletTransaction(id=transaction_id, wallet_id=wallet.id,
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
    """intro-->This endpoint allows you to retrieve the credit wallet history of a particular organization. To use this endpoint you need to make a get request to the /credits/{organization_id}/history endpoint

        ParamDesc-->On get request, the request url takes the parameter organization id and two(2) optional query parameters    
            param-->organization_id: This is the unique id of the organization
            param-->page: This is the page of interest, this is 1 by default
            param-->size: This is the size per page, this is 10 by default

    returnDesc--> On sucessful request, it returns the
        returnBody--> details of the credit wallet history of the queried organization
    """
    credit = await _get_credit(organization_id=organization_id, user=user, db=db)
    history = db.query(model.CreditWalletHistory).filter_by(credit_wallet_id=credit.id).order_by(
        desc(model.CreditWalletHistory.date))
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

    credit_wallet_history = model.CreditWalletHistory(id=uuid4().hex,
                                                                             credit_wallet_id=credit.id,
                                                                             amount=credits_to_add,
                                                                             date=_dt.datetime.utcnow(),
                                                                             reference=reference)
    db.add(credit_wallet_history)
    db.commit()
    db.refresh(credit_wallet_history)


async def _get_market_rate(currency: str, db: _orm.Session):
    usd_rate = db.query(model.CreditWalletConversion).filter_by(
        currency_code='USD').first()
    if usd_rate is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Currency " + currency + " does not have a conversion rate")
    currency = currency.upper()

    freeCurrencyApiKey = config("FREECURRENCY_API_KEY")
    url = 'https://api.currencyapi.com/v2/latest?apikey=' + freeCurrencyApiKey
    response = requests.get(url)
    if response.status_code == 200:
        jsonResponse = response.json()
        rates = jsonResponse['data']
        # rates['USD'] = 1
        if currency in rates:
            rate = usd_rate.rate * jsonResponse['data'][currency]
            conversion_rate = model.CreditWalletConversion(id=uuid4().hex,
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
        db.query(organization_models.Organization)
            .filter_by(user_id=user.id)
            .filter(organization_models.Organization.id == organization_id)
            .first()
    )

    if organization is None:
        is_store_member = await Helpers.is_organization_member(user_id=user.id, organization_id=organization_id, db=db)
        if is_store_member:
            organization = (
                db.query(organization_models.Organization)
                    .filter(organization_models.Organization.id == organization_id)
                    .first()
            )
        if (not is_store_member) or organization is None:
            raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization does not exist")

    return organization


async def _get_credit_wallet_conversion(currency: str, db: _orm.Session):
    conversion = (
        db.query(model.CreditWalletConversion)
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
