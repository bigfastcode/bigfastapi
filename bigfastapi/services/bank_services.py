import json
from uuid import uuid4
import pkg_resources
from sqlalchemy.orm import Session
from fastapi import status, HTTPException
from bigfastapi.schemas import bank_schemas
from datetime import datetime
from bigfastapi.models.bank_models import BankModels


import requests
token = "xxxxxxxxxxxxxxxxxxx"


async def fetch_nigerian_banks():
    url = "https://api.okra.ng/v2/banks/list"
    headers = {
        "accept": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}"

    }
    response = requests.get(url, headers=headers)
    return json.loads(response.text)

async def get_nigerian_bank_by_id(bank_id: str):
    url = "https://api.okra.ng/v2/banks/getById"

    headers = {
        "accept": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    return json.loads(response.text)

async def verify_account_number(account_number: int, bank_id: str, bank_name: str=None ):
    url = "https://api.okra.ng/v2/products/kyc/nuban-name-verify"
    

    print(account_number)
    print(bank_id)

    payload = f"nuban={account_number}&bank={bank_id}"
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "authorization": f"Bearer {token}"
    }

    response = requests.post(url, data=payload, headers=headers)

    return json.loads(response.text)


async def fetch_bank(id:str, db:Session):
    bank = db.query(BankModels).filter(BankModels.id == id).filter(
        BankModels.is_deleted== False).first()
    if not bank:
        raise HTTPException(detail="Bank does not exist",
            status_code=status.HTTP_404_NOT_FOUND)
    return bank


async def add_bank(
    user_id:str,
    bank: bank_schemas.AddBank,
    db: Session
):
    addbank = BankModels(
        id=bank.id if bank.id else uuid4().hex,
        organization_id=bank.organization_id,
        creator_id=user_id,
        account_number=bank.account_number,
        bank_name=bank.bank_name,
        recipient_name=bank.recipient_name,
        country=bank.country,
        currency=bank.currency,
        frequency=bank.frequency,
        sort_code=bank.sort_code,
        swift_code=bank.swift_code,
        bank_address=bank.bank_address,
        is_preferred=bank.is_preferred,
        account_type=bank.account_type,
        aba_routing_number=bank.aba_routing_number,
        iban=bank.iban,
        date_created=bank.date_created if bank.date_created else datetime.now()
    )

    db.add(addbank)
    db.commit()
    db.refresh(addbank)
    return bank_schemas.BankResponse.from_orm(addbank)


async def get_organization_banks(
    db:Session,
    organization_id:str,
    offset= 1,
    limit= 50,
    datetime_constraint: datetime = None
):
    bank_query = db.query(BankModels).filter(
        BankModels.organization_id==organization_id).filter(
        BankModels.is_deleted==False)
    total_items = bank_query.count()

    if datetime_constraint:
        banks = bank_query.filter(
            BankModels.last_updated > datetime_constraint
            ).offset(offset).limit(limit).all()

        total_items = bank_query.filter(
            BankModels.last_updated > datetime_constraint).count()
    else:
        banks = bank_query.offset(offset).limit(limit).all()
    
    banks_list = list(map(bank_schemas.BankResponse.from_orm, banks))
    return (total_items, banks_list)


async def update_bank(
    bank: bank_schemas.UpdateBank,
    bank_account:BankModels, 
    db: Session
):
    if bank.account_number:           
        bank_account.account_number = bank.account_number
    if bank.bank_name:
        bank_account.bank_name = bank.bank_name
    if bank.recipient_name:
        bank_account.recipient_name = bank.recipient_name
    if bank.country:
        bank_account.country = bank.country
    if bank.sort_code:
        bank_account.sort_code = bank.sort_code
    if bank.swift_code:
        bank_account.swift_code = bank.swift_code
    if bank.bank_address:
        bank_account.bank_address = bank.bank_address
    if bank.account_type:
        bank_account.account_type = bank.account_type
    if bank.currency:
        bank_account.currency = bank.currency
    if bank.frequency:
        bank_account.frequency = bank.frequency
    if bank.is_preferred:
        bank_account.is_preferred = bank.is_preferred
    if bank.aba_routing_number:
        bank_account.aba_routing_number = bank.aba_routing_number 
    if bank.iban:
        bank_account.iban = bank.iban
    bank_account.last_updated = bank.last_updated if bank.last_updated else datetime.now()

    db.commit()
    db.refresh(bank_account)
    return bank_schemas.BankResponse.from_orm(bank_account)


# =================================== helper classes and functions =================================#

BANK_DATA_PATH = pkg_resources.resource_filename('bigfastapi', 'data/')

class BankValidator:

    def __init__(self) -> None:
        with open(BANK_DATA_PATH + "/bank.json") as file:
            self.country_info = json.load(file)

    async def get_country_data(self, country):
        print("country is ", country)
        if country in self.country_info:
            return self.country_info[country]
        else:
            return self.country_info['others']


BV = BankValidator()


