import datetime as _dt
from uuid import uuid4

import fastapi
import sqlalchemy.orm as _orm
from fastapi import APIRouter, status
from fastapi_pagination import Page, paginate, add_pagination
from sqlalchemy import desc

from bigfastapi.db.database import get_db
from .auth_api import is_authenticated
from .models import organisation_models as organisation_models, user_models
from .models import wallet_models as model
from .models import wallet_transaction_models as wallet_transaction_models
from .schemas import users_schemas
from .schemas import wallet_schemas as schema

app = APIRouter(tags=["Wallet"])


@app.post("/wallets", response_model=schema.Wallet)
async def create_wallet(body: schema.WalletCreate,
                        user: users_schemas.User = fastapi.Depends(is_authenticated),
                        db: _orm.Session = fastapi.Depends(get_db)):
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
    """Get all the wallets of an organization"""
    return await _get_organization_wallets(organization_id=organization_id, user=user, db=db)


@app.get("/wallets/{organization_id}/{currency}", response_model=schema.Wallet)
async def get_organization_wallet(
        organization_id: str,
        currency: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    """Gets the wallet of an organization"""
    return await _get_organization_wallet(organization_id=organization_id, currency=currency, user=user, db=db)


@app.get("/wallets/{organization_id}/{currency}/transactions", response_model=Page[schema.WalletTransaction])
async def get_wallet_transactions(
        organization_id: str,
        currency: str,
        user: users_schemas.User = fastapi.Depends(is_authenticated),
        db: _orm.Session = fastapi.Depends(get_db),
):
    """Get wallet transactions"""
    wallet = await _get_organization_wallet(organization_id=organization_id, currency=currency, user=user, db=db)
    return await _get_wallet_transactions(wallet_id=wallet.id, db=db)


############
# Services #
############

async def _get_organization(organization_id: str, db: _orm.Session,
                            user: users_schemas.User = fastapi.Depends(is_authenticated)):
    organization = (
        db.query(organisation_models.Organization)
            .filter_by(creator=user.id)
            .filter(organisation_models.Organization.id == organization_id)
            .first()
    )

    if organization is None:
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

    wallet_balance = await _get_wallet_balance(wallet_id=wallet.id, db=db)
    wallet.balance = wallet_balance

    return wallet


async def _get_wallet_transactions(wallet_id: str, db: _orm.Session):
    wallet_transactions = db.query(wallet_transaction_models.WalletTransaction).filter_by(wallet_id=wallet_id).order_by(
        desc(wallet_transaction_models.WalletTransaction.transaction_date))

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
    organization = db.query(organisation_models.Organization).filter_by(creator=admin.id).filter_by(
        is_deleted=False).first()
    wallet = db.query(model.Wallet).filter_by(organization_id=organization.id).filter_by(
        currency_code=currency).first()
    if wallet is None:
        wallet = await _create_wallet(organization_id=organization.id, db=db, currency_code=currency)

    return wallet


async def update_wallet(wallet, amount: float, db: _orm.Session, currency: str, wallet_transaction_id='', reason=''):
    # update the wallet
    # wallet.balance += amount
    # wallet.last_updated = _dt.datetime.utcnow()
    # db.commit()
    # db.refresh(wallet)

    if wallet_transaction_id == '':
        wallet_transaction = wallet_transaction_models.WalletTransaction(id=uuid4().hex, wallet_id=wallet.id,
                                                                         currency_code=currency, amount=amount,
                                                                         transaction_date=_dt.datetime.utcnow(),
                                                                         transaction_ref=reason, status=True)
        db.add(wallet_transaction)
        db.commit()
        db.refresh(wallet_transaction)

    else:
        # update a wallet transaction
        wallet_transaction = db.query(wallet_transaction_models.WalletTransaction).filter_by(
            id=wallet_transaction_id).first()
        wallet_transaction.status = True
        if reason != '':
            wallet_transaction.transaction_ref = reason
        db.commit()
        db.refresh(wallet_transaction)

    if amount < 0:
        amount = -amount
        # transfer money to admin wallet

        adminWallet = await _get_super_admin_wallet(db=db, currency=currency)
        # update admin wallet
        adminWallet.balance += amount
        adminWallet.last_updated = _dt.datetime.utcnow()
        db.commit()
        db.refresh(adminWallet)

        wallet_transaction = wallet_transaction_models.WalletTransaction(id=uuid4().hex, wallet_id=adminWallet.id,
                                                                         currency_code=currency, amount=amount,
                                                                         transaction_date=_dt.datetime.utcnow(),
                                                                         transaction_ref=reason, status=True)
        db.add(wallet_transaction)
        db.commit()
        db.refresh(wallet_transaction)

    return wallet


add_pagination(app)
