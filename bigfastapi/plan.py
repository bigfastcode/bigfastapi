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


@app.post('/plans', response_model=plan_schema.ResponseSingle)
async def addPlan(plan: plan_schema.PlanReqBase, db: _orm.Session = _fastapi.Depends(get_db)):
    addedPlan = await addNewPlan(plan, db)
    return buildSuccessRess(addedPlan, False)


@app.get('/plans', response_model=plan_schema.ResponseList)
async def getAll(db: _orm.Session = _fastapi.Depends(get_db)):
    plans = await getAllPlans(db)
    return buildSuccessRess(plans, True)


@app.get('/plans/{planId}', response_model=plan_schema.ResponseSingle)
async def getPlan(planId: str, db: _orm.Session = _fastapi.Depends(get_db)):
    plan = await fetchPlan(planId, db)
    return buildSuccessRess(plan, False)


# SERVICE LAYER
# ----------------------------------------------------------------------------
# ADD A NEW PLAN
async def addNewPlan(newPlan: plan_schema.PlanReqBase, db: _orm.Session):
    planObj = plan_model.Plan(id=uuid4().hex, credit_price=newPlan.credit_price,
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
    return db.query(plan_model.Plan).filter(plan_model.Plan.id == planId).first()


# GENERIC STRUCTURED RESPONSE BUILDER
def buildSuccessRess(resData, isList: bool):
    if isList:
        return plan_schema.ResponseList(status='success', resource_type='plan list', data=resData)
    else:
        return plan_schema.ResponseSingle(status='success', resource_type='plan', data=resData)
