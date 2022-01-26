from typing import List
from bigfastapi import db
from uuid import uuid4
from bigfastapi.models import plan_model
from bigfastapi.schemas import plan_schema
from bigfastapi.db.database import get_db
import sqlalchemy.orm as _orm
import fastapi as _fastapi
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.param_functions import Depends
from fastapi import APIRouter, HTTPException, status
import fastapi

app = APIRouter(tags=["Plan"])


@app.post('/plan', response_model=plan_schema.ResponseSingle)
async def addPlan(plan: plan_schema.PlanReqBase, db: _orm.Session = _fastapi.Depends(get_db)):
    addedPlan = await addNewPlan(plan, db)
    return buildSuccessRess(addedPlan, 'plan', False)


# SERVICE LAYER --------

# ADD A NEW PLAN
async def addNewPlan(newPlan: plan_schema.PlanReqBase, db: _orm.Session):
    planObj = plan_model.Plan(id=uuid4().hex, price=newPlan.price,
                              access_type=newPlan.access_type, duration=newPlan.duration)
    db.add(planObj)
    db.commit()
    db.refresh(planObj)
    return planObj


# GET ALL AVAILABLE PLANS
async def getAllPlans(db: _orm.Session):
    return db.query(plan_model.Plan).all()


# FETCH A SPECIFIC PLAN BY ITS ID
async def fetchPlan(planId: str, db: _orm.Session):
    return db.query(plan_model.Plan).filter(plan_model.Plan.id == planId).all()


# GENERIC STRUCTURED RESPONSE BUILDER
def buildSuccessRess(resData, type: str, isList: bool):
    if isList:
        return plan_schema.ResponseList(status='success', resource_type=type, data=resData)
    else:
        return plan_schema.ResponseSingle(status='success', resource_type=type, data=resData)
