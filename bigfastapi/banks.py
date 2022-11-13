from bigfastapi.utils import paginator
import sqlalchemy.orm as orm
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from bigfastapi.db.database import get_db
from bigfastapi.schemas import bank_schemas, users_schemas
from bigfastapi.services.auth_service import is_authenticated
from bigfastapi.core.helpers import Helpers
from bigfastapi.core import messages
from datetime import datetime
from bigfastapi.services import bank_services
from bigfastapi.models.organization_models import Organization
from bigfastapi.services import anchorapi_services


router = APIRouter()


@router.post("/banks", 
    status_code=status.HTTP_201_CREATED, 
    response_model=bank_schemas.BankResponse
)
async def add_bank_detail(
    bank: bank_schemas.AddBank,
    user: users_schemas.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)
):
    """intro-->This endpoint allows you to bank detail object. 
        To use this endpoint you need to make a post request to the /banks endpoint

    reqBody-->account_number: This is the user's bank account number
    reqBody-->bank_name: This is the user's bank name
    reqBody-->recipient_name: This is the name of the account owner
    reqBody-->account_type: This is the type of bank account
    reqBody-->organization_id: This is the organization Id of the organization requiring the bank detail
    reqBody-->bank_addres: This is the branch address of the user's account creation 
    reqBody-->swift_code: This is the bank's swift code
    reqBody-->sort_code: This is the bank's sort code
    reqBody-->country: This is the country where the bank exists
    reqBody-->aba_routing_number: This is the accounts's routing number
    reqBody-->iban: This is account's international bank account number
    reqBody-->is_preferred: This is a boolean account preference value
    reqBody-->date_created: This is the date of creation of the bank account

    returnDesc--> On sucessful request, it returns 
        returnBody--> the newly created bank details

    Args:
        request: A pydantic schema that defines the room request parameters
        db (Session): The database for storing the article object
    Returns:
        HTTP_201_CREATED (new bank details added)
    Raises
        HTTP_424_FAILED_DEPENDENCY: failed to create bank object
        HTTP_403_FORBIDDEN: incomplete details
    """
    organization = (db.query(Organization).filter(
        Organization.id == bank.organization_id).first())
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.INVALID_ORGANIZATION)

    is_store_member = await Helpers.is_organization_member(user_id=user.id, organization_id=bank.organization_id, db=db)
    if not is_store_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to add a bank account to this organization")

    return await bank_services.add_bank(user_id=user.id, bank=bank, db=db)


@router.get("/banks", 
    status_code=status.HTTP_200_OK,
    response_model=bank_schemas.PaginatedBankResponse
)
async def get_organization_bank_accounts(
    organization_id: str, 
    size: int = 50,
    page: int = 1, 
    user: users_schemas.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db), 
    datetime_constraint:datetime = None
):
    """intro-->This endpoint allows you retrieve all available bank details in the database. 
        To use this endpoint you need to make a get request to the /banks/organizations/{organization_id} endpoint

    paramDesc-->On get request, the request url takes the query parameter organization id and four(4)
        other optional query parameters
        param-->org_id: This is the organization Id of the user's current organization
        
    returnDesc--> On sucessful request, it returns a 
        returnBody--> details of queried bank accounts
    
    Args:
        user: authenticates that the user is a logged in user
        db (Session): The database for storing the article object
    Returns:
        HTTP_200_OK (list of all registered bank details)
    Raises
        HTTP_424_FAILED_DEPENDENCY: failed to fetch banks
    """

    is_store_member = await Helpers.is_organization_member(user_id=user.id, organization_id=organization_id, db=db)
    if not is_store_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this resource")

    page_size = 50 if size < 1 or size > 100 else size
    page_number = 1 if page <= 0 else page
    offset = await paginator.off_set(page=page_number, size=page_size)

    total_items, banks_list =await bank_services.get_organization_banks(db=db, organization_id=organization_id,
        offset=offset, limit= page_size, datetime_constraint=datetime_constraint)

    pointers = await paginator.page_urls(page=page_number, size=page_size,
                                         count=total_items, endpoint="/banks")

    response = {"page": page_number, "size": page_size, "total": total_items,
                "previous_page": pointers['previous'], "next_page": pointers["next"], "items": banks_list}
    return response


@router.get("/banks/{bank_id}", 
    status_code=status.HTTP_200_OK,
    response_model=bank_schemas.BankResponse
)
async def get_single_bank(
    bank_id: str,
    user: users_schemas.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)
):
    """intro-->This endpoint allows you retrieve a particular bank account. 
        To use this endpoint you need to make a get request to the /banks/{bank_id} endpoint

    paramDesc-->On get request, the request url takes the  parameters bank_id and a query parameter organization id 
        param-->bank_id: This is the bank id of the bank detail
        param-->organization_id: This is the organization Id of the user's current organization
        
    returnDesc--> On sucessful request, it returns a 
        returnBody--> details of queried bank account

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
    bank = await bank_services.fetch_bank(id=bank_id, db=db)
    return bank_schemas.BankResponse.from_orm(bank)


@router.put("/banks/{bank_id}", 
    status_code=status.HTTP_202_ACCEPTED,
    response_model=bank_schemas.BankResponse
)
async def update_bank_details(
    bank_id: str, 
    bank: bank_schemas.UpdateBank,
    user: users_schemas.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)
):
    """intro-->This endpoint allows you update a bank detail. To use this endpoint you need to make a put request to the /banks/{bank_id} endpoint

    paramDesc-->On put request, the request url takes the parameter bank_id 
        param-->bank_id: This is the bank id of the bank detail

        reqBody-->account_number: This is the user's bank account number
        reqBody-->bank_name: This is the user's bank name
        reqBody-->recipient_name: This is the name of the account owner
        reqBody-->account_type: This is the type of bank account
        reqBody-->organization_id: This is the organization Id of the organization requiring the bank detail
        reqBody-->bank_addres: This is the branch address of the user's account creation 
        reqBody-->swift_code: This is the bank's swift code
        reqBody-->sort_code: This is the bank's sort code
        reqBody-->country: This is the country where the bank exists
        reqBody-->aba_routing_number: This is the accounts's routing number
        reqBody-->iban: This is account's international bank account number
        reqBody-->is_preferred: This is a boolean account preference value
        reqBody-->date_created: This is the date of creation of the bank account
        
    returnDesc--> On sucessful request, it returns the
        returnBody--> updated bank details

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
    is_store_member = await Helpers.is_organization_member(user_id=user.id, organization_id=bank.organization_id, db=db)

    if not is_store_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="You are not allowed to carry out this operation")

    bank_account = await bank_services.fetch_bank(id=bank_id, db=db)  

    return await bank_services.update_bank(bank_account=bank_account, bank=bank, db=db)


@router.delete("/banks/{bank_id}", status_code=status.HTTP_200_OK)
async def delete_bank(
    bank_id: str,
    user: users_schemas.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db)
):
    """intro-->This endpoint allows you delete a particular bank detail. To use this endpoint you need to make a delete request to the /banks/{bank_id} endpoint

    paramDesc-->On delete request, the request url takes the  parameter bank_id  
        param-->bank_id: This is the bank id of the bank detail
        
    returnDesc--> On sucessful request, it returns the 
        returnBody-->  deleted bank detail

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

    bank = await bank_services.fetch_bank(id=bank_id, db=db)

    is_store_member = await Helpers.is_organization_member(user_id=user.id, organization_id=bank.organization_id, db=db)
    if not is_store_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="You are not allowed to carry out this operation")
    bank.is_deleted = True
    db.commit()
    db.refresh(bank)
    return JSONResponse({"detail": "bank details successfully deleted"},
        status_code=status.HTTP_200_OK)


@router.get("/banks/schema/{country}", status_code=status.HTTP_200_OK)
async def get_country_schema(country: str):
    """intro-->This endpoint allows you get the valid schema for every country. To use this endpoint you need to make a get request to the /banks/schema endpoint

    paramDesc-->On get request, the request url takes the query parameter country 
        param-->country: This is the country of interest
        
    returnDesc--> On sucessful request, it returns the 
        returnBody--> valid schema for queried country

    Args:
        country: Country whose schema structure is to be fetched.
    Returns:
        HTTP_200_OK (bank object)
    Raises: 
        HTTP_4O4_NOT_FOUND: Country not in the list of supported countries.
    """

    schema = await bank_services.BV.get_country_data(country=country)
    return schema


@router.get("/banks/list/nigeria", status_code=status.HTTP_200_OK)
def get_nigerian_banks():
    banks = anchorapi_services.fetch_nigerian_banks()
    return banks

@router.get("/banks/verify-nuban/{bank_code}/{account_number}", status_code=status.HTTP_200_OK)
def verify_nuban(bank_code: str, account_number: str):
    banks = anchorapi_services.verify_nuban(bank_code, account_number)
    return banks


###========= uncomment and use this endpoint if your last_updated is showing null====###
# from bigfastapi.db.database import db_engine
# @router.get("/banks-migration/upate-last_updated",
#          status_code=status.HTTP_200_OK)
# async def update_last_updated():
#     with db_engine.connect() as con:
#         rs = con.execute(
#             'UPDATE banks SET banks.last_updated = banks.date_created')
#     return rs
