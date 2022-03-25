from sqlite3 import IntegrityError
from uuid import uuid4
from sqlalchemy import ForeignKey
import bigfastapi.db.database as database
from datetime import datetime
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Text, JSON

from bigfastapi.schemas import plan_schemas
from bigfastapi.auth_api import is_authenticated
from fastapi import Depends
import sqlalchemy.orm as orm
from bigfastapi.schemas import users_schemas
import json


class Plan(database.Base):
    __tablename__ = "plans"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    created_by = Column(String(255), ForeignKey("users.id"))
    title = Column(String(255), unique=True, index=True, default="")
    description = Column(String(700), index=True, default="")
    price_offers = Column(JSON(), default=None)
    available_geographies = Column(JSON(), default=None)
    features = Column(JSON(), default=None)
    date_created = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)


def db_selector(plan_id: str, db: orm.Session = Depends(database.get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    return plan or None
        
def get_all_plans(db: orm.Session = Depends(database.get_db)):
    plans = db.query(Plan).all()
    return list(map(plan_schemas.Plan.from_orm, plans))


def get_plan_by_id(plan_id: str, db: orm.Session = Depends(database.get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if plan:
        return plan_schemas.Plan.from_orm(plan)
    else:
        return None


def get_plan_by_title(title: str, db: orm.Session = Depends(database.get_db)):
    plan = db.query(Plan).filter(Plan.title == title).first()
    if plan:
        return plan_schemas.Plan.from_orm(plan)
    else:
        return None


def get_plans_by_geography(geography: str, db: orm.Session = Depends(database.get_db)):
    plan = db.query(Plan).filter(Plan.available_geographies.contains(geography)).all()
    if plan:
        return list(map(plan_schemas.Plan.from_orm, plan))
    else:
        return None


def create_plan(
    plan: plan_schemas.PlanDTO,
    db: orm.Session = Depends(database.get_db),
    user: users_schemas.User = Depends(is_authenticated),
):

    plan_search = get_plan_by_title(title=plan.title, db=db)
    if plan_search is None:
        if user.is_superuser == True:
            try:
                plan = Plan(id=uuid4().hex, created_by=user.id, **plan.dict())
                db.add(plan)
                db.commit()
                db.refresh(plan)
                return plan_schemas.Plan.from_orm(plan)
            except IntegrityError:
                raise LookupError("plan title already exists")
        raise PermissionError("only an admin can create a plan")
    raise LookupError("plan title already exists")


def update_plan(
    plan: plan_schemas.PlanDTO,
    plan_id: str,
    db: orm.Session = Depends(database.get_db),
    user: users_schemas.User = Depends(is_authenticated),
):

    plan_db =  db_selector(plan_id, db)
    if plan_db:
        if user.is_superuser == True:
            if get_plan_by_title(title=plan.title, db=db) is None:
                try:
                    update_data = plan.dict(exclude_unset=True)
                    update_data['last_updated'] = datetime.utcnow()
                    for key, value in update_data.items():
                        setattr(plan_db, key, value)
                        
                    # plan_db.copy(update=update_data)
                    # plan_db.last_updated = datetime.utcnow()
                    db.commit()
                    db.refresh(plan_db)
                    return plan_schemas.Plan.from_orm(plan_db) 
                except IntegrityError:
                    raise LookupError("plan title already exists")
            raise LookupError("plan title already exists")
        raise PermissionError("only an admin can update a plan")
    raise LookupError("plan does not exist")


def delete_plan(
    plan_id: str,
    db: orm.Session = Depends(database.get_db),
    user: users_schemas.User = Depends(is_authenticated),
):

    plan_db = get_plan_by_id(plan_id=plan_id, db=db)
    if plan_db:
        if user.is_superuser == True:
            db.delete(plan_db)
            db.commit()
            return {"message": "Plan deleted succesfully"}
        else:
            raise PermissionError("only an admin can delete a plan")
    else:
        raise LookupError("plan does not exist")
