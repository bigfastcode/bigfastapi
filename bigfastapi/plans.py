from .schemas import plan_schemas, users_schemas
from .auth_api import is_authenticated
from .models import plan_models
from fastapi import APIRouter, Depends, HTTPException, status, responses
from bigfastapi.db.database import get_db
import sqlalchemy.orm as orm
from typing import List
from fastapi.encoders import jsonable_encoder


app = APIRouter(tags=["Plans"])


@app.post("/plans", response_model=List[plan_schemas.Plan])
def create_plan(
        plan: plan_schemas.PlanDTO,
        db: orm.Session = Depends(get_db),
        user: users_schemas.User = Depends(is_authenticated)):
    """Creates a new plan

    Args:
        plan (plan_schemas.PlanDTO): body of the request
        db (orm.Session, optional): [description]. Defaults to Depends(get_db).
        user (users_schemas.User, optional): [description]. user initiating the request

    Raises:
        HTTPException: if user is not an admin or if plan already exists

    Returns:
        [dict]: key value pair of the following keys:
            message (str): success message
            data (plan_schemas.Plan): the created plan
    """

    try:
        response = plan_models.create_plan(plan=plan, db=db, user=user)
        return responses.JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Plan created succesfully", "data": jsonable_encoder(response)})
    except PermissionError as exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exception))
    except LookupError as exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exception))


@app.put("/plans/{plan_id}", response_model=plan_schemas.Plan)
def update_plan(
        plan: plan_schemas.PlanDTO,
        plan_id: str,
        db: orm.Session = Depends(get_db),
        user: users_schemas.User = Depends(is_authenticated)):
    """Updates a plan

    Args:
        plan (plan_schemas.PlanDTO): body of the request
        plan_id (str): id of the plan to update
        db (orm.Session, optional): [description]. Defaults to Depends(get_db).
        user (plan_schemas.User, optional): [description]. user initiating the request

    Raises:
        HTTPException: if user is not an admin or if plan does not exist

    Returns:
        [dict]: key value pair of the following keys:
            message (str): success message
            data (plan_schemas.Plan): the updated plan
    """
    try:
        response = plan_models.update_plan(
            plan=plan, plan_id=plan_id, db=db, user=user)
        return responses.JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Plan updated succesfully",
                     "data": jsonable_encoder(response)})
    except PermissionError as exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exception))
    except LookupError as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exception))


@app.get("/plans", response_model=List[plan_schemas.Plan])
def get_all_plans(db: orm.Session = Depends(get_db)):
    """Retrieves all existing plans

    Args:
        db (orm.Session, optional): [description]. Defaults to Depends(get_db).

    Returns:
        [dict]: key value pair of the following keys:
            message (str): success message
            data (List[plan_schemas.Plan]): list of plans
    """
    plans = plan_models.get_all_plans(db=db)
    return responses.JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Plans retrieved succesfully", "data": jsonable_encoder(plans)})


@app.get("/plans/{plan_id}", response_model=plan_schemas.Plan)
def get_plan_by_id(plan_id: str, db: orm.Session = Depends(get_db)):
    """Retrieves a plan by id

    Args:
        plan_id (str): id of the plan
        db (orm.Session, optional): [description]. Defaults to Depends(get_db).

    Returns:
        [dict]: key value pair of the following keys:
            message (str): success message
            data (plan_schemas.Plan): the plan
    """
    plan = plan_models.get_plan_by_id(plan_id=plan_id, db=db)
    if plan:
        return responses.JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Plan retrieved succesfully", "data": jsonable_encoder(plan)})
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="plan does not exist")


@app.get("/plans/geography/{geography_id}", response_model=List[plan_schemas.Plan])
def get_plan_by_geography(geography_id: str, db: orm.Session = Depends(get_db)):
    """Retrieves a plan by geography id

    Args:
        geography_id (str): id of the geography
        db (orm.Session, optional): [description]. Defaults to Depends(get_db).

    Returns:
        [dict]: key value pair of the following keys:
            message (str): success message
            data (List[plan_schemas.Plan]): list of plans
    """
    plans = plan_models.get_plans_by_geography(geography=geography_id, db=db)
    if plans:
        return responses.JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Plans retrieved succesfully", "data": jsonable_encoder(plans)})
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="plan does not exist")


@app.delete("/plans/{plan_id}", response_model=plan_schemas.Plan)
def delete_plan(
        plan_id: str,
        db: orm.Session = Depends(get_db),
        user: users_schemas.User = Depends(is_authenticated)):
    """Deletes a plan by id

    Args:
        plan_id (str): id of the plan
        db (orm.Session, optional): [description]. Defaults to Depends(get_db).

    Returns:
        [dict]: key value pair of the following keys:
            message (str): success message
            data (plan_schemas.Plan): the deleted plan
    """
    try:
        response = plan_models.delete_plan(plan_id=plan_id, db=db, user=user)
        return responses.JSONResponse(status_code=status.HTTP_200_OK, content=response)
    except PermissionError as exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exception))
    except LookupError as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exception))
