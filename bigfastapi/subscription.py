from uuid import uuid4
from bigfastapi.schemas import subscription_schema
from bigfastapi.models import subscription_models
from bigfastapi.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, status

app = APIRouter(tags=["Subscription"])


@app.get("/subscriptions/{org_Id}", response_model=subscription_schema.ResponseList)
async def index_sub_per_org(org_Id: str,  db: Session = Depends(get_db)):
    """intro-->This endpoint is used to retrieve a users subscription details to an organization. To use this endpoint you need to make a get request to the /subscriptions/{org_Id} endpoint 
            paramDesc-->On get request the url takes in the parameter, org_id
                param-->org_id: This is the organization Id of the organization subscribed to

    returnDesc--> On sucessful request, it returns 
        returnBody--> details of the subscription
    """
    subs = await get_subs(org_Id, db)
    return build_success_ress(list(map(subscription_schema.SubcriptionBase.from_orm, subs)),
                            'subscription list', True)


@app.post('/subscriptions', response_model=subscription_schema.ResponseSingle)
async def subscribe(
        subscription: subscription_schema.SubBase,
        db: Session = Depends(get_db)
):
    """intro-->This endpoint is used to process subscription to an organization. To use this endpoint you need to make a post request to the /subscriptions endpoint with a specified body of request 

    returnDesc--> On sucessful request, it returns 
        returnBody--> details of the subscription
    """
    created_subscription = await create_subs(subscription, db)
    return build_success_ress(created_subscription, 'subscription', False)

# ///
# SERVICE LAYER


async def get_subs(org_Id: str, db: Session):
    return db.query(subscription_models.Subscription).filter(
        subscription_models.Subscription.organization_id == org_Id).all()


async def create_subs(sub: subscription_schema.CreateSubscription, db: Session):
    subObject = subscription_models.Subscription(
        id=uuid4().hex, plan=sub.plan, organization_id=sub.organization_id, is_paid=True)
    db.add(subObject)
    db.commit()
    db.refresh(subObject)
    return subObject


def build_success_ress(resData, type: str, isList: bool):
    if isList:
        return subscription_schema.ResponseList(status='success', resource_type=type, data=resData)
    else:
        return subscription_schema.ResponseSingle(status='success', resource_type=type, data=resData)
