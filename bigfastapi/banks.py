from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import HttpUrl
from bigfastapi.schemas import bank_schemas, users_schemas
from bigfastapi.db.database import get_db
import sqlalchemy.orm as Session
from bigfastapi.models import bank_models
from uuid import uuid4
from .auth import is_authenticated
from fastapi.responses import JSONResponse
from typing import List

router = APIRouter()




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
    try:
        addbank = bank_models.Bank(id=uuid4().hex,
                        account_number=bank.account_number, 
                        bank_name=bank.bank_name, 
                        account_name=bank.account_name,
                        bank_sort_code=bank.bank_sort_code, 
                        country=bank.country, 
                        created_by=bank.created_by,
                        date_created=bank.date_created )
        db.add(addbank)
        db.commit()
        db.refresh(addbank)
    except:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, 
                    detail=f"failed to add bank details")
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
    try:
        banks = db.query(bank_models.Bank).all()
    except:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, 
                    detail=f"failed to fetch banks")
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


#=================================== Bank Service =================================#
    
async def fetch_bank(user: users_schemas.User, id: str, db: Session):
    try:
        bank = db.query(bank_models.Bank).filter(bank_models.Bank.id == id).first()
    except: 
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, 
                    detail=f"failed to fetch bank details")
    if not bank:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"This bank detail does not exist here")
    return bank

async def validate_bank_details(details:list, validator: HttpUrl):
    return "bank details valid"