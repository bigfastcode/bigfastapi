from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import HttpUrl, Json
from bigfastapi.schemas import bank_schemas, users_schemas
from bigfastapi.db.database import get_db
import sqlalchemy.orm as Session
from bigfastapi.models import bank_models
from uuid import uuid4
from .auth import is_authenticated
from fastapi.responses import JSONResponse
from typing import List
import pkg_resources
import json

router = APIRouter()

BANK_DATA_PATH = pkg_resources.resource_filename('bigfastapi', 'data/')


@router.post("/organisation/{org_id}/bank", status_code=status.HTTP_201_CREATED,
            response_model=bank_schemas.BankResponse)
async def add_bank_detail(org_id: str, bank: bank_schemas.AddBank,
     user: users_schemas.User = Depends(is_authenticated), 
    db:Session = Depends(get_db)
    ):
                        
    """Creates a new bank object.
    Args:
        request: A pydantic schema that defines the room request parameters
        db (Session): The database for storing the article object
    Returns:
        HTTP_201_CREATED (new bank details added)
    Raises
        HTTP_424_FAILED_DEPENDENCY: failed to create bank object
    """
    addbank = bank_models.BankDetails(id=uuid4().hex,
                    organisation_id= bank.organisation_id,
                    creator_id= bank.creator_id,
                    account_number= bank.account_number,
                    bank_name= bank.bank_name,
                    account_name= bank.account_name,
                    address=bank.address,
                    swift_code=bank.swift_code,
                    sort_code=bank.sort_code,
                    postcode=bank.postcode,
                    country=bank.country,
                    date_created=bank.date_created)
    db.add(addbank)
    db.commit()
    db.refresh(addbank)
   
    return bank_schemas.BankResponse.from_orm(addbank)




@router.get("/organisation/{org_id}/banks", status_code=status.HTTP_200_OK,
            response_model=List[bank_schemas.BankResponse])
async def get_all_banks(org_id: str, user: users_schemas.User = Depends(is_authenticated),
    db:Session = Depends(get_db)):

    """Fetches all available bank details in the database.
    Args:
        user: authenticates that the user is a logged in user
        db (Session): The database for storing the article object
    Returns:
        HTTP_200_OK (list of all registered bank details)
    Raises
        HTTP_424_FAILED_DEPENDENCY: failed to fetch banks
    """
    banks = db.query(bank_models.BankDetails).all()
    return list(map(bank_schemas.BankResponse.from_orm, banks))



@router.get("/organisation/{org_id}/bank/{bank_id}", status_code=status.HTTP_200_OK,
            response_model=bank_schemas.BankResponse)
async def get_single_bank(org_id: str, bank_id:str,
            user: users_schemas.User = Depends(is_authenticated),
            db:Session = Depends(get_db)):

    """Fetches single bank detail given bank_id.
    Args:
        bank_id: a unique identifier of the bank object.
        user: authenticates that the user is a logged in user.
        db (Session): The database for storing the article object.
    Returns:
        HTTP_200_OK (bank object)
    Raises
        HTTP_424_FAILED_DEPENDENCY: failed to create bank object
        HTTP_4O4_NOT_FOUND: Bank does not exist.
    """
    bank = await fetch_bank(user=user, id=bank_id, db=db)
    return bank_schemas.BankResponse.from_orm(bank)
     



@router.delete("/organisation/{org_id}/bank/{bank_id}", status_code=status.HTTP_200_OK)
async def delete_bank(org_id: str, bank_id:str,
            user: users_schemas.User = Depends(is_authenticated),
            db:Session = Depends(get_db)):
    """delete a given bank of id bank_id.
    Args:
        bank_id: a unique identifier of the bank object.
        user: authenticates that the user is a logged in user.
        db (Session): The database for storing the article object.
    Returns:
        HTTP_200_OK (sucess response))
    Raises
        HTTP_424_FAILED_DEPENDENCY: failed to delete bank details
        HTTP_4O4_NOT_FOUND: Bank does not exist.
    """
    bank = await fetch_bank(user=user, id=bank_id, db=db)
    db.delete(bank)
    db.commit()
    return JSONResponse({"detail": f"bank details with {bank_id} successfully deleted"},
                 status_code=status.HTTP_200_OK)


@router.get("/bank/schema", status_code=status.HTTP_200_OK)
async def get_single_bank(country: str):
    """Fetches details needed to add bank details based on country provided.
    Args:
        country: Country whose schema structure is to be fetched.
    Returns:
        HTTP_200_OK (bank object)
    Raises
        HTTP_4O4_NOT_FOUND: Country not in the list of supported countries.
    """
    return "schema"

    

@router.get("/bank/validator", status_code=status.HTTP_200_OK)
async def validate_bank_details(country: str):
    """Fetches details needed to add bank details based on country provided.
    Args:
        country: Country whose schema structure is to be fetched.
    Returns:
        HTTP_200_OK (bank object)
    Raises
        HTTP_4O4_NOT_FOUND: Country not in the list of supported countries.
    """
    return "valid"





#=================================== Bank Service =================================#
    
async def fetch_bank(user: users_schemas.User, id: str, db: Session):
    bank = db.query(bank_models.BankDetails).filter(bank_models.AccountDetails.id == id).first()
    if not bank:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"This bank detail does not exist here")
    return bank


class IdentityValidator:

    async def validate_org():
        pass

    async def user_in_org():
        pass


async def get_country_data(country, info=None): 
    with open(BANK_DATA_PATH + "/bank.json") as file:
        country_data = json.load(file)
    try:
        if info:
            country_info = country_data[country][info]
        country_info= country_data[country]
        return country_info
    except ValueError:
        return country_data["others"]


async def validate_supported_country(country):
    
    pass

async def validate_schema_format(country, schema):
    
    

async def validate_bank_details(details:list, validator: HttpUrl):
    return "bank details valid"


