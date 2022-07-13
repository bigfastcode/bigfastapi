import datetime as _dt
from locale import currency
from uuid import uuid4

import fastapi
import sqlalchemy.orm as _orm
from fastapi import APIRouter, status
from fastapi_pagination import Page, paginate, add_pagination
from sqlalchemy import desc

from bigfastapi.db.database import get_db
from .auth_api import is_authenticated
from .core.helpers import Helpers
from .models import organization_models as organization_models, user_models
from .models import wallet_models as model
from .schemas import users_schemas
from .schemas import wallet_schemas as schema

app = APIRouter(tags=["Wallet"])


@app.post("/wallets", response_model=schema.Wallet)
async def create_wallet(body: schema.WalletCreate,
                        user: users_schemas.User = fastapi.Depends(is_authenticated),
                        db: _orm.Session = fastapi.Depends(get_db)):
    """intro-->This endpoint allows you to create a wallet. To use this endpoint you need to make a post request to the /wallets endpoint with s specified body of request
            
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
                              last_updated=_dt.datetime.utcnow())

        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        return wallet
    else:
        raise fastapi.HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Organization already has a " + body.currency_code + " wallet")


@app.get("/wallets/{organization_id}", response_model=Page[schema.Wallet])
async def get_organization_wallets(
        organization_id: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):  
    """intro-->This endpoint allows you to retrieve all the wallets in an organization. To use this endpoint you need to make a get request to the /wallets/{organization_id} endpoint
            
            paramDesc-->On get request, the request url takes the  parameter organization id and two(2) optional query parameters 
                param-->organization_id: This is unique id of the organization of interest
                param-->page: This is the page of interest, this is 1 by default
                param-->size: This is the size per page, this is 10 by default

            
    returnDesc--> On sucessful request, it returns a
        returnBody--> list of queried wallets
    """
    return await _get_organization_wallets(organization_id=organization_id, user=user, db=db)



@app.get("/wallet-balance/{organization_id}")
async def get_organization_wallet(
        organization_id: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):  
    """intro-->This endpoint allows you to retrieve all the wallets in an organization. To use this endpoint you need to make a get request to the /wallets/{organization_id} endpoint
            
            paramDesc-->On get request, the request url takes the  parameter organization id and two(2) optional query parameters 
                param-->organization_id: This is unique id of the organization of interest
                param-->page: This is the page of interest, this is 1 by default
                param-->size: This is the size per page, this is 10 by default

            
    returnDesc--> On sucessful request, it returns a
        returnBody--> list of queried wallets
    """
    return await get_org_wallet(organization_id=organization_id, user=user, db=db)


@app.get("/wallet-transactions/{organization_id}")
async def get_organization_wallet_transactions(
        organization_id: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    """intro-->This endpoint allows you to retrieve the wallet of an organization. To use this endpoint you need to make a get request to the /wallets/{organization_id}/{currency} endpoint
            
            paramDesc-->On get request, the request url takes two(2) parameters, organization id and currency
                param-->organization_id: This is unique id of the organization of interest
                param-->currency: This is the currency you want to retrieve the organization's wallet in

            
    returnDesc--> On sucessful request, it returns 
        returnBody--> details of the queried organization's wallet
    """
    return await get_org_wallet_transactions(organization_id=organization_id, user=user, db=db)


@app.get("/wallets/{organization_id}/{currency}/transactions", response_model=Page[schema.WalletTransaction])
async def get_wallet_transactions(
        organization_id: str,
        currency: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
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
    wallet = await _get_organization_wallet(organization_id=organization_id, currency=currency, user=user, db=db)
    return await _get_wallet_transactions(wallet_id=wallet.id, db=db)


############
# Services #
############

async def _get_organization(organization_id: str, db: _orm.Session,
                            user: users_schemas.User = fastapi.Depends(is_authenticated)):
    organization = (
        db.query(organization_models.Organization)
            .filter_by(user_id=user.id)
            .filter(organization_models.Organization.id == organization_id)
            .first()
    )

    is_store_member = await Helpers.is_organization_member(user_id=user.id, organization_id=organization_id, db=db)
    if is_store_member:
        organization = (
            db.query(organization_models.Organization)
                .filter(organization_models.Organization.id == organization_id)
                .first()
        )
    if (not is_store_member) and organization is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization does not exist")

    return organization


async def _create_wallet(organization_id: str,
                         db: _orm.Session, currency_code: str):
    wallet = model.Wallet(id=uuid4().hex, organization_id=organization_id, balance=0,
                          last_updated=_dt.datetime.utcnow(), currency_code=currency_code)

    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


async def _get_wallet_balance(wallet_id: str, db: _orm.Session):
    query = db.execute(
        'select round(sum(amount),2) as amount from wallet_transactions where status = 1 and wallet_id="' + wallet_id + '"')

    wallet_balance = query.first()[0]

    if wallet_balance is None:
        return 0
    else:
        return wallet_balance


async def _get_organization_wallet(organization_id: str,
                                   currency: str,
                                   user: users_schemas.User,
                                   db: _orm.Session):
    # verify if the organization exists under the user's account

    await _get_organization(organization_id=organization_id, db=db, user=user)
    wallet = db.query(model.Wallet).filter_by(organization_id=organization_id).filter_by(currency_code=currency).first()
    if wallet is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Organization does not have a " + currency + " wallet")

    # wallet_balance = await _get_wallet_balance(wallet_id=wallet.id, db=db)
    # wallet.balance = wallet_balance

    return wallet


async def get_org_wallet_transactions(organization_id: str,
                                   user: users_schemas.User,
                                   db: _orm.Session):
    # verify if the organization exists under the user's account

    await _get_organization(organization_id=organization_id, db=db, user=user)
    wallet = db.query(model.Wallet).filter_by(organization_id=organization_id).first()
    if wallet is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Organization does not have a wallet")
    wallet_trnx = db.query(model.WalletTransaction).filter_by(wallet_id=wallet.id).all()
    # wallet_balance = await _get_wallet_balance(wallet_id=wallet.id, db=db)
    # wallet.balance = wallet_balance

    return wallet_trnx


async def get_org_wallet(organization_id: str, user, db: _orm.Session):
    # verify if the organization exists under the user's account
    await _get_organization(organization_id=organization_id, db=db, user=user)
    wallet = db.query(model.Wallet).filter_by(organization_id=organization_id).first()
    if wallet is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Organization does not have a wallet")

    wallet_balance = await _get_wallet_balance(wallet_id=wallet.id, db=db)
    wallet.balance = wallet_balance

    return wallet

async def _get_wallet_transactions(wallet_id: str, db: _orm.Session):
    wallet_transactions = db.query(model.WalletTransaction).filter_by(wallet_id=wallet_id).order_by(
        desc(model.WalletTransaction.transaction_date))

    return paginate(list(wallet_transactions))


async def _get_organization_wallets(organization_id: str,
                                    user: users_schemas.User,
                                    db: _orm.Session):
    # verify if the organization exists under the user's account

    await _get_organization(organization_id=organization_id, db=db, user=user)

    wallets = db.query(model.Wallet).filter_by(organization_id=organization_id)
    for index, wallet in enumerate(wallets):
        wallets[index].balance = await _get_wallet_balance(wallet_id=wallet.id, db=db)

    return paginate(list(wallets))


async def _get_wallet(wallet_id: str,
                      user: users_schemas.User,
                      db: _orm.Session):
    wallet = db.query(model.Wallet).filter_by(id=wallet_id).first()
    if wallet is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet does not exist")

    return wallet


async def _get_super_admin_wallet(db: _orm.Session, currency: str):
    admin = db.query(user_models.User).filter_by(is_superuser=True).filter_by(is_deleted=False).first()
    organization = db.query(organization_models.Organization).filter_by(creator=admin.id).filter_by(
        is_deleted=False).first()
    wallet = db.query(model.Wallet).filter_by(organization_id=organizations.id).filter_by(
        currency_code=currency).first()
    if wallet is None:
        wallet = await _create_wallet(organization_id=organizations.id, db=db, currency_code=currency)

    return wallet


async def create_wallet_transaction(wallet, amount: float, db: _orm.Session, currency: str, reason=''):
    wallet_transaction = model.WalletTransaction(id=uuid4().hex, wallet_id=wallet.id,
                                                            currency_code=currency, amount=amount,
                                                            transaction_date=_dt.datetime.utcnow(),
                                                            transaction_ref=reason, status=True  )

    db.add(wallet_transaction)
    db.commit()
    db.refresh(wallet_transaction)

    wallet.balance += amount
    wallet.last_updated = _dt.datetime.utcnow()
    db.commit()
    db.refresh(wallet)






async def update_wallet(wallet, amount: float, db: _orm.Session, currency: str, wallet_transaction_id='', reason=''):
    # update the wallet
    # wallet.balance += amount
    # wallet.last_updated = _dt.datetime.utcnow()
    # db.commit()
    # db.refresh(wallet)

    if wallet_transaction_id == '':
        wallet_transaction = model.WalletTransaction(id=uuid4().hex, wallet_id=wallet.id,
                                                                         currency_code=currency, amount=amount,
                                                                         transaction_date=_dt.datetime.utcnow(),
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
    #     adminWallet.last_updated = _dt.datetime.utcnow()
    #     db.commit()
    #     db.refresh(adminWallet)

    #     wallet_transaction = model.WalletTransaction(id=uuid4().hex, wallet_id=adminWallet.id,
    #                                                                      currency_code=currency, amount=amount,
    #                                                                      transaction_date=_dt.datetime.utcnow(),
    #                                                                      transaction_ref=reason, status=True)
    #     db.add(wallet_transaction)
    #     db.commit()
    #     db.refresh(wallet_transaction)

    return wallet





add_pagination(app)
