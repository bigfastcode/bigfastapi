import datetime as dt
import json
import os
import random
import re
from random import randrange
from typing import Union

import fastapi
import pkg_resources
import requests
import stripe
import validators
from decouple import config
from jinja2 import Template
from sqlalchemy import inspect
from starlette import status
from stripe.error import InvalidRequestError

from bigfastapi.db.database import Base
from bigfastapi.schemas import users_schemas
from bigfastapi.schemas.wallet_schemas import PaymentProvider

DATA_PATH = pkg_resources.resource_filename("bigfastapi", "data/")


def generate_short_id(size=9, chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"):
    return "".join(random.choice(chars) for _ in range(size))


def generate_random_int(begin=0, end=1000):
    return randrange(begin, end)


def validate_email(email):
    regex = r"^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$"
    if re.search(regex, email):
        return {"status": True, "message": "Valid"}
    else:
        return {"status": False, "message": "Enter Valid E-mail"}


def ValidateUrl(url):
    valid = validators.url(url)
    if valid is True:
        return True
    else:
        return False


def paginate_data(data, page_size: int, page_number: int):
    start = (page_number - 1) * page_size
    end = start + page_size

    return {
        "message": "success",
        "data": data[start:end],
        "total_documents": data.__len__(),
        "page_limit": page_size,
    }


def find_country(ctry):
    with open(DATA_PATH + "/countries.json") as file:
        cap_country = ctry.upper()
        countries = json.load(file)
        found_country = next(
            (country for country in countries if country["iso2"] == cap_country), None
        )
        if found_country is None:
            raise fastapi.HTTPException(
                status_code=403, detail="This country doesn't exist"
            )
        return found_country["name"]


def validate_phone_dialcode(dcode) -> Union[str, None]:
    with open(DATA_PATH + "/dialcode.json") as file:
        dialcodes = json.load(file)
        found_dialcode = next(
            (dialcode for dialcode in dialcodes if dialcode["dial_code"] == dcode), None
        )
        if found_dialcode is None:
            return None
        return found_dialcode["dial_code"]


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


async def generate_payment_link(
    api_redirect_url: str,
    customer: dict,
    currency: str,
    tx_ref: str,
    amount: float,
    provider: PaymentProvider,
    email: str = "",
    phone_number: str = "",
    phone_country_code: str = "",
    front_end_redirect_url="",
):
    if provider == PaymentProvider.STRIPE:
        stripe.api_key = config("STRIPE_SEC_KEY")
        try:
            session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "currency": currency,
                            "product_data": {
                                "name": "Stripe Payment",
                            },
                            "unit_amount": int(amount),
                        },
                        "quantity": 1,
                    }
                ],
                client_reference_id=tx_ref,
                metadata={"redirect_url": front_end_redirect_url},
                mode="payment",
                success_url=api_redirect_url
                + "?status=successful&tx_ref="
                + tx_ref
                + "&transaction_id={CHECKOUT_SESSION_ID}",
                cancel_url=api_redirect_url
                + "?status=cancelled&tx_ref="
                + tx_ref
                + "&transaction_id={CHECKOUT_SESSION_ID}",
            )
            return session.url
        except InvalidRequestError as e:
            raise fastapi.HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )
    else:
        flutterwaveKey = config("FLUTTERWAVE_SEC_KEY")
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + flutterwaveKey,
        }
        url = "https://api.flutterwave.com/v3/payments/"
        username=""
        if customer.biz_partner_type == "supplier":
            username = customer.business_name
        else:
            username = customer.email if customer.first_name is None else customer.first_name
            username += "" if customer.last_name is None else " " + customer.last_name

        

        data = {
            "tx_ref": tx_ref,
            "amount": amount,
            "currency": currency,
            "redirect_url": api_redirect_url,
            "customer": {
                "email": email,
                "phonenumber": phone_country_code+phone_number,
                "name": username,
            },
            "meta": {"redirect_url": front_end_redirect_url},
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            jsonResponse = response.json()
            link = (jsonResponse.get("data"))["link"]
            return link
        else:
            raise fastapi.HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An error occurred. Please try again later",
            )


def row_to_dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))
    return d


def object_as_dict(obj) -> dict:
    if isinstance(obj, Base) is False:
        raise TypeError("Input is not a valid database object")
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def convert_template_to_html(template_dir, template_file, template_data):
    """Substitute template variables and return html formatted"""
    file_path = os.path.join(template_dir, template_file)

    with open(file_path) as f:
        html_text = f.read()
        html_text = Template(html_text).render(template_data)

    return html_text


def gen_max_age():
    return dt.datetime.utcnow() + dt.timedelta(days=365)
