import datetime 
from uuid import uuid4
from typing import List
import fastapi
from sqlalchemy import orm 
from fastapi import APIRouter, status
from sqlalchemy import desc
from bigfastapi.db.database import get_db
from bigfastapi.services.auth_service import is_authenticated
from bigfastapi.core.helpers import Helpers
from bigfastapi.core import messages
from bigfastapi.models import organization_models, user_models, wallet_models as model
from bigfastapi.schemas import users_schemas, wallet_schemas as schema
from bigfastapi.utils import paginator


app = APIRouter(tags=["Wallet"])


@app.post("/wallets", response_model=schema.Wallet)
async def create_wallet(
    body: schema.WalletCreate,
    db: orm.Session = fastapi.Depends(get_db),
    user: users_schemas.User = fastapi.Depends(is_authenticated)
):
    """intro-->This endpoint allows you to create a wallet. 
        To use this endpoint you need to make a post request to the /wallets endpoint with s specified body of request
            
        reqBody-->organization_id: This is the user's current organization
        reqBody-->currency_code: This is the short code of the currency the wallet will accept
        reqBody-->user_id: This is the unique id of the user the wallet will be created for 
            
    returnDesc--> On sucessful request, it returns
        returnBody--> details of the newly created wallet
    """
    currency_code = body.currency_code.upper()
    wallet = db.query(model.Wallet).filter_by(organization_id=body.organization_id).filter_by(
        currency_code=currency_code).first()
    # todo: why is create wallet returning an error?
    # wallet = _create_wallet(organization_id=body.organization_id, db=db)
    if wallet is None:
        wallet = model.Wallet(id=uuid4().hex, organization_id=body.organization_id, balance=0,
                              currency_code=currency_code,
                              last_updated=datetime.datetime.utcnow())

        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        return wallet
    else:
        raise fastapi.HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Organization already has a " + body.currency_code + " wallet")


@app.get("/wallets/{organization_id}",
    response_model=List[schema.Wallet]
)
async def get_organization_wallets(
    organization_id: str,
    user: users_schemas.User = fastapi.Depends(is_authenticated),
    db: orm.Session = fastapi.Depends(get_db),
):  
    """intro-->This endpoint allows you to retrieve all the wallets in an organization. 
        To use this endpoint you need to make a get request to the /wallets/{organization_id} endpoint
            
    paramDesc-->On get request, the request url takes the  parameter organization id and two(2) optional query parameters 
        param-->organization_id: This is unique id of the organization of interest
        param-->page: This is the page of interest, this is 1 by default
        param-->size: This is the size per page, this is 10 by default

    returnDesc--> On sucessful request, it returns a
        returnBody--> list of queried wallets
    """
    #validate organization exist
    organization = db.query(organization_models.Organization).filter(
        organization_models.Organization.id == organization_id).first()
    if not organization:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=messages.INVALID_ORGANIZATION)

    #validate user belongs to org
    is_store_member = await Helpers.is_organization_member(user_id=user.id, organization_id=organization_id, db=db)
    if is_store_member == False:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=messages.NOT_ORGANIZATION_MEMBER)

    wallets = db.query(model.Wallet).filter_by(organization_id=organization_id).limit(50).all()
    if not wallets:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                 detail="Organization does not have a wallet")
    return wallets



@app.get("/wallet-balance/{organization_id}")
async def get_organization_wallet(
        organization_id: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: orm.Session = fastapi.Depends(get_db),
):  
    """intro-->This endpoint allows you to retrieve all the wallets in an organization. 
        To use this endpoint you need to make a get request to the /wallets/{organization_id} endpoint

        paramDesc-->On get request, the request url takes the  
            parameter organization id and two(2) optional query parameters 
            param-->organization_id: This is unique id of the organization of interest
            param-->page: This is the page of interest, this is 1 by default
            param-->size: This is the size per page, this is 10 by default

        returnDesc--> On sucessful request, it returns a
            returnBody--> list of queried wallets
    """
    organization = db.query(organization_models.Organization).filter(
        organization_models.Organization.id == organization_id).first()
    if not organization:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=messages.INVALID_ORGANIZATION)

    #validate user belongs to org
    is_store_member = await Helpers.is_organization_member(user_id=user.id, organization_id=organization_id, db=db)
    if is_store_member == False:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=messages.NOT_ORGANIZATION_MEMBER)

    wallet = db.query(model.Wallet).filter(model.Wallet.organization_id==organization_id).filter(
        model.Wallet.currency_code == organization.currency_code).first()
    if not wallet:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                 detail="Organization does not have a wallet")
    return wallet


@app.get("/wallet-transactions/{organization_id}")
async def get_organization_wallet_transactions(
    organization_id: str,
    search_value: str = None,
    sorting_key: str = "date_created",
    datetime_constraint:datetime.datetime = None,
    page: int = 1,
    size: int = 50,
    reverse_sort: bool = True,
    db: orm.Session = fastapi.Depends(get_db),
    user: users_schemas.User = fastapi.Depends(is_authenticated),
):
    """intro-->This endpoint allows you to retrieve the wallet of an organization. 
        To use this endpoint you need to make a get request to the /wallets/{organization_id}/{currency} endpoint
            
        paramDesc-->On get request, the request url takes two(2) parameters, organization id and currency
            param-->organization_id: This is unique id of the organization of interest
            param-->currency: This is the currency you want to retrieve the organization's wallet in
            
    returnDesc--> On sucessful request, it returns 
        returnBody--> details of the queried organization's wallet
    """
    sort_dir = "desc" if reverse_sort == True else "asc"
    page_size = 50 if size < 1 or size > 100 else size
    page_number = 1 if page <= 0 else page
    offset = await paginator.off_set(page=page_number, size=page_size)

    #validate organization exist
    organization = db.query(organization_models.Organization).filter(
        organization_models.Organization.id == organization_id).first()
    if not organization:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=messages.INVALID_ORGANIZATION)

    #validate user belongs to org
    is_store_member = await Helpers.is_organization_member(user_id=user.id, organization_id=organization_id, db=db)
    if is_store_member == False:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=messages.NOT_ORGANIZATION_MEMBER)

    transactions =await get_org_wallet_transactions(organization_id=organization_id,
        limit=page_size, offset=page_number, db=db)
    return transactions


@app.get("/wallets/{organization_id}/{currency}/transactions")
async def get_wallet_transactions(
        organization_id: str,
        currency: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: orm.Session = fastapi.Depends(get_db),
):
    """intro-->This endpoint allows you to retrieve an organization's wallet transactions. To use this endpoint you need to make a get request to the /wallets/{organization_id}/{currency}/transactions endpoint
            
            paramDesc-->On get request, the request url takes two(2) parameters, organization id and currency and two(2) optional query parameters
                param-->organization_id: This is unique id of the organization of interest
                param-->currency: This is the currency you want to retrieve the organization's wallet in
                param-->page: This is the page of interest, this is 1 by default
                param-->size: This is the size per page, this is 10 by default
            
    returnDesc--> On sucessful request, it returns 
        returnBody--> wallet transactions details of the queried organization
    """
    wallet = await get_organization_wallet(organization_id=organization_id, currency=currency, user=user, db=db)
    print(wallet)
    return await get_wallet_transactions(wallet_id=wallet.id, db=db)


############
# Services #
############


async def create_wallet(organization_id: str,
                         db: orm.Session, currency_code: str):
    wallet = model.Wallet(id=uuid4().hex, organization_id=organization_id, balance=0,
                          last_updated=datetime.datetime.utcnow(), currency_code=currency_code)

    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


async def get_wallet_balance(wallet_id: str, db: orm.Session):
    query = db.execute(
        'select round(sum(amount),2) as amount from wallet_transactions where status = 1 and wallet_id="' + wallet_id + '"')

    wallet_balance = query.first()[0]

    if wallet_balance is None:
        return 0
    else:
        return wallet_balance


async def get_organization_wallet(organization_id: str,
                                   currency: str,
                                   user: users_schemas.User,
                                   db: orm.Session):
    # verify if the organization exists under the user's account

    wallet = db.query(model.Wallet).filter_by(organization_id=organization_id).filter_by(currency_code=currency).first()
    if wallet is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Organization does not have a " + currency + " wallet")

    # wallet_balance = await _get_wallet_balance(wallet_id=wallet.id, db=db)
    # wallet.balance = wallet_balance

    return wallet


async def get_org_wallet_transactions(
    organization_id: str,
    db: orm.Session,
    offset:int=1,
    limit:int=50
):
    wallets = db.query(model.Wallet).filter_by(organization_id=organization_id).limit(50).all()
    wallet_ids = [item.id for item in wallets]

    wallet_trnx = db.query(model.WalletTransaction).filter(
        model.WalletTransaction.wallet_id.in_(wallet_ids)).offset(
        offset=offset).limit(limit=limit).all()

    return wallet_trnx


# async def get_org_wallet(organization_id: str, user, db: orm.Session):
#     # verify if the organization exists under the user's account
#     wallet = db.query(model.Wallet).filter_by(organization_id=organization_id).first()
#     if wallet is None:
#         raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                                     detail="Organization does not have a wallet")

#     wallet_balance = await get_wallet_balance(wallet_id=wallet.id, db=db)
#     wallet.balance = wallet_balance

#     return wallet

async def get_single_wallet_transactions(wallet_id: str, db: orm.Session):
    wallet_transactions = db.query(model.WalletTransaction).filter_by(wallet_id=wallet_id).order_by(
        desc(model.WalletTransaction.transaction_date))

    return wallet_transactions


async def get_organization_wallets(
    organization_id: str,
    db: orm.Session
):
    wallets = db.query(model.Wallet).filter_by(organization_id=organization_id)
    for index, wallet in enumerate(wallets):
        wallets[index].balance = await get_wallet_balance(wallet_id=wallet.id, db=db)

    return wallets


async def get_wallet(wallet_id: str,
                      user: users_schemas.User,
                      db: orm.Session):
    wallet = db.query(model.Wallet).filter_by(id=wallet_id).first()
    if wallet is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet does not exist")

    return wallet


async def get_super_admin_wallet(db: orm.Session, currency: str):
    admin = db.query(user_models.User).filter_by(is_superuser=True).filter_by(is_deleted=False).first()
    organization = db.query(organization_models.Organization).filter_by(creator=admin.id).filter_by(
        is_deleted=False).first()
    wallet = db.query(model.Wallet).filter_by(organization_id=organization.id).filter_by(
        currency_code=currency).first()
    if wallet is None:
        wallet = await create_wallet(organization_id=organization.id, db=db, currency_code=currency)

    return wallet


async def create_wallet_transaction(wallet, amount: float, db: orm.Session, currency: str, reason=''):
    wallet_transaction = model.WalletTransaction(id=uuid4().hex, wallet_id=wallet.id,
                                                            currency_code=currency, amount=amount,
                                                            transaction_date=datetime.datetime.utcnow(),
                                                            transaction_ref=reason, status=True  )

    db.add(wallet_transaction)
    db.commit()
    db.refresh(wallet_transaction)

    wallet.balance += amount
    wallet.last_updated = datetime.datetime.utcnow()
    db.commit()
    db.refresh(wallet)






async def update_wallet(wallet, amount: float, db: orm.Session, currency: str, wallet_transaction_id='', reason=''):
    # update the wallet
    # wallet.balance += amount
    # wallet.last_updated = datetime.datetime.utcnow()
    # db.commit()
    # db.refresh(wallet)

    if wallet_transaction_id == '':
        wallet_transaction = model.WalletTransaction(id=uuid4().hex, wallet_id=wallet.id,
                                                                         currency_code=currency, amount=amount,
                                                                         transaction_date=datetime.datetime.utcnow(),
                                                                         transaction_ref=reason, status=True)
        db.add(wallet_transaction)
        db.commit()
        db.refresh(wallet_transaction)

    else:
        # update a wallet transaction
        wallet_transaction = db.query(model.WalletTransaction).filter_by(
            id=wallet_transaction_id).first()
        wallet_transaction.status = True
        if reason != '':
            wallet_transaction.transaction_ref = reason
        db.commit()
        db.refresh(wallet_transaction)

    # if amount < 0:
    #     amount = -amount
    #     # transfer money to admin wallet

    #     adminWallet = await _get_super_admin_wallet(db=db, currency=currency)
    #     # update admin wallet
    #     adminWallet.balance += amount
    #     adminWallet.last_updated = datetime.datetime.utcnow()
    #     db.commit()
    #     db.refresh(adminWallet)

    #     wallet_transaction = model.WalletTransaction(id=uuid4().hex, wallet_id=adminWallet.id,
    #                                                                      currency_code=currency, amount=amount,
    #                                                                      transaction_date=datetime.datetime.utcnow(),
    #                                                                      transaction_ref=reason, status=True)
    #     db.add(wallet_transaction)
    #     db.commit()
    #     db.refresh(wallet_transaction)

    return wallet

