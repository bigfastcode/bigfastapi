import os
import time
from datetime import datetime
from typing import List, Optional, Union
from uuid import uuid4

import fastapi
import sqlalchemy.orm as orm
from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, status
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import BaseModel

from bigfastapi.db.database import get_db
from bigfastapi.schemas import receipt_schemas
from bigfastapi.utils import settings

from .models import email_models
from .schemas import email_schema

app = APIRouter(tags=["Emails 📧"])


class ResponseModel(BaseModel):
    message: str


@app.post("/email/send", response_model=ResponseModel)
def send_email(
    email_details: email_schema.Email,
    background_tasks: BackgroundTasks,
    email_type: str = "base",
    is_scheduled: bool = False,
    schedule_at: datetime = None,
    db: orm.Session = fastapi.Depends(get_db),
):
    """intro-->This endpoint is used to send an email. To use this endpoint you need to make a post request to the /email/send endpoint with a specified body of request

        reqBody-->subject: This is the subject of the email
        reqBody-->recipient: This is an array of emails you want to send the email to
        reqBody-->title: This is the title of the email
        reqBody-->first_name: This is the first name of the user
        reqBody-->sender_address: This is the address of the user
        reqBody-->sender_city: This is the city of the user
        reqBody-->sender_state: This is the state of the user
        reqBody-->body: This is the body of the email

    returnDesc--> On sucessful request, it returns message,
        returnBody--> "Email will be sent in the background"
    """

    email_map = {
        "base": "base_email.html",
        "notification": "notification_email.html",
        "invoice": "invoice_email.html",
        "receipt": "receipt_email.html",
        "welcome": "welcome_email.html",
        "verification": "verification_email.html",
        "marketing": "marketing_email.html"
    }

    if is_scheduled == True and schedule_at != None:
        if schedule_at <= datetime.now():
            raise fastapi.HTTPException(
                status_code=404,
                detail="The scheduled date/time can't be less than or equal to the current date/time",
        )

        scheduled_time = schedule_at - datetime.now()
        scheduled_time_in_secs = int(round(scheduled_time.total_seconds()))
        time.sleep(scheduled_time_in_secs)
        send_email(
            email_details=email_details,
            background_tasks=background_tasks,
            template=email_map[email_type],
            db=db,
        )

        return {"message": "Scheduled Email will be sent in the background"}

    send_email(
        email_details=email_details,
        background_tasks=background_tasks,
        template=email_map[email_type],
        db=db,
    )

    return {"message": "Email will be sent in the background"}

