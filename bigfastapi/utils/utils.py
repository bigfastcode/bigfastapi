import json
import random
import re

import fastapi
import pkg_resources
import requests
import stripe
import validators
from decouple import config
from starlette import status
from stripe.error import InvalidRequestError

from bigfastapi.schemas import users_schemas
from bigfastapi.schemas.wallet_schemas import PaymentProvider

DATA_PATH = pkg_resources.resource_filename('bigfastapi', 'data/')


def generate_short_id(size=9, chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    return ''.join(random.choice(chars) for _ in range(size))


def validate_email(email):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if (re.search(regex, email)):
        return {"status": True, "message": "Valid"}
    else:
        return {"status": False, "message": "Enter Valid E-mail"}


def ValidateUrl(url):
    valid = validators.url(url)
    if valid == True:
        return True
    else:
        return False


def paginate_data(data, page_size: int, page_number: int):
    start = (page_number - 1) * page_size
    end = start + page_size

    return {
        "data": data[start: end],
        "total_documents": data.__len__(),
        "page_limit": page_size
    }


def find_country(ctry):
    with open(DATA_PATH + "/countries.json") as file:
        cap_country = ctry.capitalize()
        countries = json.load(file)
        found_country = next((country for country in countries if country['name'] == cap_country), None)
        if found_country is None:
            raise fastapi.HTTPException(status_code=403, detail="This country doesn't exist")
        return found_country['name']


def dialcode(dcode):
    with open(DATA_PATH + "/dialcode.json") as file:
        dialcodes = json.load(file)
        found_dialcode = next((dialcode for dialcode in dialcodes if dialcode['dial_code'] == dcode), None)
        if found_dialcode is None:
            raise fastapi.HTTPException(status_code=403, detail="This is an invalid dialcode")
        return found_dialcode['dial_code']


def generate_code(new_length: int = None):
    length = 6
    if new_length is not None:
        length = new_length
    if length < 4:
        raise fastapi.HTTPException(status_code=400, detail="Minimum code lenght is 4")
    code = ""
    for i in range(length):
        code += str(random.randint(0, 9))
    return code


async def generate_payment_link(api_redirect_url: str,
                                user: users_schemas.User,
                                currency: str,
                                tx_ref: str,
                                amount: float,
                                provider: PaymentProvider,
                                front_end_redirect_url='',
                                ):
    if provider == PaymentProvider.STRIPE:
        stripe.api_key = config('STRIPE_SEC_KEY')
        try:
            session = stripe.checkout.Session.create(
                line_items=[{
                    'price_data': {
                        'currency': currency,
                        'product_data': {
                            'name': 'Stripe Payment',
                        },
                        'unit_amount': int(amount)
                    },
                    'quantity': 1,
                }],
                client_reference_id=tx_ref,
                metadata={'redirect_url': front_end_redirect_url},
                mode='payment',
                success_url=api_redirect_url + "?status=successful&tx_ref=" + tx_ref + "&transaction_id={CHECKOUT_SESSION_ID}",
                cancel_url=api_redirect_url + "?status=cancelled&tx_ref=" + tx_ref + "&transaction_id={CHECKOUT_SESSION_ID}",
            )
            return session.url
        except InvalidRequestError as e:
            raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=str(e))
    else:
        flutterwaveKey = config('FLUTTERWAVE_SEC_KEY')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + flutterwaveKey}
        url = 'https://api.flutterwave.com/v3/payments/'
        username = user.email if user.first_name is None else user.first_name
        username += '' if user.last_name is None else ' ' + user.last_name
        data = {
            "tx_ref": tx_ref,
            "amount": amount,
            "currency": currency,
            "redirect_url": api_redirect_url,
            "customer": {
                "email": user.email,
                "phonenumber": user.phone_number,
                "name": username
            },
            "meta": {
                "redirect_url": front_end_redirect_url
            }
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            jsonResponse = response.json()
            link = (jsonResponse.get('data'))['link']
            return link
        else:
            raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="An error occurred. Please try again later")


def row_to_dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))
    return d
