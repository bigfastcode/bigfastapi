import datetime as dt

import fastapi
import requests
import sqlalchemy.orm as _orm
from decouple import config
from fastapi import APIRouter
from starlette.responses import RedirectResponse

from bigfastapi.db.database import get_db
from .auth_api import is_authenticated
from .models import credit_models as credit_models
from .models import organisation_models as organization_models
from .schemas import payment_schemas as schema
from .schemas import users_schemas

app = APIRouter(tags=["Payment"])


@app.post("/payments", response_model=schema.PaymentLink)
async def generate_payments_link(body: schema.Payment, user: users_schemas.User = fastapi.Depends(is_authenticated),
                                 db: _orm.Session = fastapi.Depends(get_db)):
    secretKey = config("FLUTTERWAVE_SEC_KEY")
    ref = user.id + "-" + body.type + "-" + body.organization_id + "-" + str(body.type_id)
    organization = (
        db.query(organization_models.Organization)
            .filter_by(creator=user.id)
            .filter(organization_models.Organization.id == body.organization_id)
            .first()
    )

    if organization is None:
        raise fastapi.HTTPException(status_code=404, detail="Organization does not exist")

    customizations = {
        "title": 'CustomerPayMe subscription payment',
        "description": 'Keep track of your debtors',
        "logo": 'https://customerpay.me/frontend/assets/img/favicon.png',
    }

    customer = {
        "customer": {
            "email": user.email,
            "phonenumber": user.phone_number,
            "name": user.first_name + " " + user.last_name
        }
    }

    response = requests.post("https://api.flutterwave.com/v3/payments",
                             headers={"Authorization": "Bearer " + secretKey},
                             json={"amount": body.amount, "currency": organization.currency,
                                   "tx_ref": ref, "payment_options": "card",
                                   "redirect_url": "http://localhost:7001/payments/callback"} | customer | customizations)
    if response.status_code == 200:
        return response.json().get('data')
    else:
        raise fastapi.HTTPException(status_code=404, detail="An error occurred while generating payment link")


# status=successful&tx_ref=de91521830d7455fb9bb2faf70923eb8-credit-f6f54248c5184053a876d6a20b01e689-None&transaction_id=3110150
@app.get("/payments/callback")
async def add_credit(status: str, tx_ref: str, transaction_id: str, db: _orm.Session = fastapi.Depends(get_db)):
    if status == 'successful':
        verification_status, amount = await _verify_payment(transaction_id=transaction_id)
        if verification_status:
            user_id, transaction_type, organization_id, type_id = tx_ref.split('-')
            if transaction_type == 'credit':
                credit = db.query(credit_models.Credit).filter_by(organization_id=organization_id).first()
                if credit is None:
                    # redirect to a frontend url that will be set
                    response = RedirectResponse(
                        url='https://staging.customerpay.me/payment/error/' + tx_ref)
                    return response
                else:
                    credit.amount += amount
                    credit.last_updated = dt.datetime.utcnow()
                    db.commit()
                    response = RedirectResponse(
                        url='https://staging.customerpay.me/payment/error/?status=success')
                    return response
        else:
            response = RedirectResponse(
                url='https://staging.customerpay.me/payment/error/' + tx_ref)
            return response
    elif status == 'cancelled':
        response = RedirectResponse(url='https://staging.customerpay.me/payment/error/' + tx_ref + '?is_cancelled=true')
        return response
    else:
        raise fastapi.HTTPException(status_code=400, detail="An error occurred while processing payment")


############
# Services #
############

async def _verify_payment(transaction_id: str):
    flutterwaveKey = config('FLUTTERWAVE_SEC_KEY')
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + flutterwaveKey}
    url = 'https://api.flutterwave.com/v3/transactions/' + transaction_id + '/verify'
    verificationRequest = requests.get(url, headers=headers)
    jsonResponse = verificationRequest.json()
    print(jsonResponse['data']['status']);
    if jsonResponse['data']['status'] == 'successful':
        return True, jsonResponse['data']['amount']
    else:
        return False, ''
