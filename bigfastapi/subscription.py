from typing import List
from bigfastapi import db
from uuid import uuid4
from bigfastapi.models import subscription_model
from bigfastapi.schemas import subscription_schema
from bigfastapi.db.database import get_db
import sqlalchemy.orm as _orm
import fastapi as _fastapi
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.param_functions import Depends
from fastapi import APIRouter, HTTPException, status
import fastapi

app = APIRouter(tags=["Subscription"])


@app.get("/subscriptions/{org_Id}", response_model=subscription_schema.ResponseList)
async def indexSubPerOrg(org_Id: str,  db: _orm.Session = _fastapi.Depends(get_db)):
    subs = await getSubs(org_Id, db)
    return buildSuccessRess(list(map(subscription_schema.SubcriptionBase.from_orm, subs)),
                            'subscription list', True)


@app.post('/subscriptions', response_model=subscription_schema.ResponseSingle)
async def subscribe(
        subscription: subscription_schema._SubBAse,
        db: _orm.Session = _fastapi.Depends(get_db)
):
    createdSubscrcription = await createSub(subscription, db)
    return buildSuccessRess(createdSubscrcription, 'subscription', False)

# ///
# SERVICE LAYER


async def getSubs(org_Id: str, db: _orm.Session):
    return db.query(subscription_model.Subscription).filter(
        subscription_model.Subscription.organization_id == org_Id).all()


async def createSub(sub: subscription_schema.CreateSubscription, db: _orm.Session):
    subObject = subscription_model.Subscription(
        id=uuid4().hex, plan=sub.plan, organization_id=sub.organization_id, is_paid=True)
    db.add(subObject)
    db.commit()
    db.refresh(subObject)
    return subObject


def buildSuccessRess(resData, type: str, isList: bool):
    if isList:
        return subscription_schema.ResponseList(status='success', resource_type=type, data=resData)
    else:
        return subscription_schema.ResponseSingle(status='success', resource_type=type, data=resData)
