import fastapi
import os
from fastapi import APIRouter, Depends
from uuid import uuid4
from bigfastapi.schemas import schedule_schemas as Schema
from bigfastapi.models import schedule_models as ScheduleModels

from bigfastapi.schemas import users_schemas as UserSchema
from bigfastapi.email import send_email_user
from bigfastapi.models import organisation_models as OrgModels

from bigfastapi.models.customer_models import get_customer_by_id
from bigfastapi.organization import get_organization
from bigfastapi.db.database import get_db
import sqlalchemy.orm as orm

from bigfastapi.auth_api import is_authenticated
from bigfastapi.organization import get_organization


app = APIRouter()


@app.post("/schedule")
async def create_schedule(schedule: Schema.CreateReminderSchedule, user: UserSchema.User = fastapi.Depends(is_authenticated),  db: orm.Session = Depends(get_db)):
    organization = await get_organization(organization_id=schedule.organization_id, user=user, db=db)
    if organization == None:
        raise fastapi.HTTPException(
            status_code=403, detail="organization does not exist or you dont have access to this organization")

    return await create_schedule(schedule, db=db)


@app.get("/schedule")
async def get_schedules(organization_id: str = "", user: UserSchema.User = fastapi.Depends(is_authenticated),  db: orm.Session = Depends(get_db)):
    schedules = await get_schedule(db, organization_id)
    return schedules


@app.put("/schedule/{schedule_id}")
async def update_schedule(schedule_id: str, schedule: Schema.UpdateSchedule, user: UserSchema.User = fastapi.Depends(is_authenticated),  db: orm.Session = Depends(get_db)):
    db_schedule = await get_schedule_by_id(db, schedule_id)
    organization = await get_organization(organization_id=db_schedule.organization_id, user=user, db=db)
    if organization.creator != user.id:
        raise fastapi.HTTPException(
            status_code=403, detail="you dont have access to this organization")
    updated_schedule = await update_schedule(schedule, db_schedule, db)
    return updated_schedule


@app.delete("/schdule/{schdule_id}")
async def delete_schedule(schedule_id: str, schedule: Schema.DeleteSchedule, user: UserSchema.User = fastapi.Depends(is_authenticated),  db: orm.Session = Depends(get_db)):
    db_schedule = await get_schedule_by_id(db, schedule_id)
    organization = await get_organization(organization_id=db_schedule.organization_id, user=user, db=db)
    if organization.creator != user.id:
        raise fastapi.HTTPException(
            status_code=403, detail="you dont have access to this organization")
    deleted_schedule = await delete_schedule(schedule, db_schedule, db)
    return deleted_schedule


async def create_schedule(schedule: Schema.CreateReminderSchedule, db: orm.Session):
    schedule_obj = ScheduleModels.Schedule(
        id=uuid4().hex, organization_id=schedule.organization_id,
        schedule_type=schedule.schedule_type,
        start_reminder=schedule.start_reminder,
        frequency_of_reminder_before_due_date=schedule.frequency_of_reminder_before_due_date,
        first_template=schedule.first_template,
        second_template=schedule.second_template,
        third_template=schedule.third_template,
        template_after_due_date=schedule.template_after_due_date,
        frequency_of_reminder_after_due_date=schedule.frequency_of_reminder_after_due_date,
        is_deleted=False,
    )

    db.add(schedule_obj)
    db.commit()
    db.refresh(schedule_obj)
    return schedule_obj


async def get_schedule(db: orm.Session, organization_id):
    if organization_id != "":
        return db.query(ScheduleModels.Schedule).filter(
            ScheduleModels.Schedule.organization_id == organization_id and ScheduleModels.Schedule.is_deleted == False).all()


async def get_schedule_by_id(db: orm.Session, schedule_id):
    return db.query(ScheduleModels.Schedule).filter(
        ScheduleModels.Schedule.id == schedule_id and ScheduleModels.Schedule.is_deleted == False).first()


async def update_schedule(schedule: Schema.UpdateSchedule, db_schedule, db: orm.Session):
    if schedule.schedule_type != None:
        db_schedule.schedule_type = schedule.schedule_type
    if schedule.start_reminder != None:
        db_schedule.start_reminder = schedule.start_reminder
    if schedule.frequency_of_reminder_before_due_date != None:
        db_schedule.frequency_of_reminder_before_due_date = schedule.frequency_of_reminder_before_due_date
    if schedule.first_template != None:
        db_schedule.first_template = schedule.first_template
    if schedule.template_after_due_date != None:
        db_schedule.template_after_due_date = schedule.template_after_due_date
    if schedule.frequency_of_reminder_after_due_date != None:
        db_schedule.frequency_of_reminder_after_due_date = schedule.frequency_of_reminder_after_due_date

    db.commit()
    db.refresh(db_schedule)

    return db_schedule


async def delete_schedule(db_schedule, db: orm.Session):
    db_schedule.is_deleted = True
    db.commit()
    db.refresh(db_schedule)
