from fastapi import APIRouter, Depends, status, HTTPException
from bigfastapi.schemas import bank_schemas, users_schemas
from bigfastapi.db.database import get_db
import sqlalchemy.orm as Session
from bigfastapi.models import bank_models
from uuid import uuid4
from .auth_api import is_authenticated
from fastapi.responses import JSONResponse
import pkg_resources
import json
from fastapi_pagination import Page, add_pagination, paginate

router = APIRouter()

BANK_DATA_PATH = pkg_resources.resource_filename('bigfastapi', 'data/')


@router.post("/bank", status_code=status.HTTP_201_CREATED,
            response_model=bank_schemas.BankResponse)
async def add_bank_detail(bank: bank_schemas.AddBank,
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
        HTTP_403_FORBIDDEN: incomplete details
    """
    if user.is_superuser is False:
        return JSONResponse({"message": "User not authorised to add bank details"}, 
                        status_code=status.HTTP_403_FORBIDDEN)
                                    
    if bank.country == "Nigeria":
        if not bank.bank_type:
            return JSONResponse({"message": "Account type is required"}, 
                         status_code=status.HTTP_403_FORBIDDEN)

        addbank = bank_models.BankModels(id=uuid4().hex,
                    organisation_id= bank.organisation_id,
                    creator_id= user.id,
                    account_number= bank.account_number,
                    bank_name= bank.bank_name,
                    account_name= bank.account_name,
                    bank_type=bank.bank_type,
                    sort_code=bank.sort_code,
                    country=bank.country,
                    date_created=bank.date_created)
        
        return await bank_models.add_bank( user=user, addbank=addbank, db=db)

    if bank.country and bank.bank_name and bank.account_name and bank.aba_routing_number and bank.swift_code and bank.sort_code and bank.iban:             
        addbank = bank_models.BankModels(id=uuid4().hex,
                        organisation_id= bank.organisation_id,
                        creator_id= user.id,
                        account_number= bank.account_number,
                        bank_name= bank.bank_name,
                        account_name= bank.account_name,
                        country=bank.country,
                        sort_code=bank.sort_code,
                        swift_code=bank.swift_code,
                        address=bank.address, 
                        account_type = bank.bank_type, 
                        aba_routing_number =bank.aba_routing_number,
                        iban=bank.iban,
                        date_created=bank.date_created)
    else: 
        return JSONResponse({"message": "missing required fields"}, 
                         status_code=status.HTTP_403_FORBIDDEN)                       
    return await bank_models.add_bank( user=user, addbank=addbank, db=db)


@router.get("/banks", status_code=status.HTTP_200_OK,
            response_model=Page[bank_schemas.BankResponse])
async def get_all_banks(user: users_schemas.User = Depends(is_authenticated),
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
    banks = db.query(bank_models.BankModels).all()
    banks_list = list(map(bank_schemas.BankResponse.from_orm, banks))
    return paginate(banks_list)



@router.get("/bank/{bank_id}", status_code=status.HTTP_200_OK,
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
    bank = await bank_models.fetch_bank(user=user, id=bank_id, db=db)
    return bank_schemas.BankResponse.from_orm(bank)
     



@router.delete("/bank/{bank_id}", status_code=status.HTTP_200_OK)
async def delete_bank(bank_id:str,
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
    if user.is_superuser is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                                    detail="User not authorised to delete bank details")
    bank = await bank_models.fetch_bank(user=user, id=bank_id, db=db)
    db.delete(bank)
    db.commit()
    return JSONResponse({"detail": f"bank details with {bank_id} successfully deleted"},
                 status_code=status.HTTP_200_OK)


@router.get("/bank/schema", status_code=status.HTTP_200_OK)
async def get_country_schema(country: str):
    """Fetches the schema valid for each country    .
    Args:
        country: Country whose schema structure is to be fetched.
    Returns:
        HTTP_200_OK (bank object)
    Raises: 
        HTTP_4O4_NOT_FOUND: Country not in the list of supported countries.
    """
    schema = await BV.get_country_data(country=country, info ="schema")
    return {"schema": dict(schema)}

    

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
    country_info = await BV.validate_supported_country(country)
    return country_info





#=================================== Bank Service =================================#


           
class BankValidator:
    
    def __init__(self) -> None:
        with open(BANK_DATA_PATH + "/bank.json") as file:
                self.country_info = json.load(file)

    async def get_country_data(self, country, info=None): 
        if country not in self.country_info and info is None:
            return self.country_info["others"]
        elif country not in self.country_info:
            return self.country_info["others"][info]
        if info:
            country_info = self.country_info[country][info]
            return country_info
        return self.country_info[country]
        
    
            
    async def validate_supported_country(self, country):
        for data in self.country_info:
            if data == country:
                return True
        return False


BV = BankValidator()
add_pagination(router)