from .models import sms_models
from .schemas import sms_schema
from typing import Optional
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Response
from bigfastapi.db.database import get_db
from fastapi import BackgroundTasks
from pydantic import BaseModel
import fastapi
import sqlalchemy.orm as orm
from bigfastapi.utils import settings
import time

app = APIRouter(tags=["Transactional Emails 📧"])


class ResponseModel(BaseModel):
    message: str


class SendSMS():

    @app.post("/sms/send", response_model=ResponseModel)
    def send_sms(
        sms_details: sms_schema.SMS,
        db: orm.Session = fastapi.Depends(get_db)
    ):

        """An endpoint used to send an sms
        
        Returns:
            object (dict): a message
        """
        

        # send_sms(sms_details=sms_details, background_tasks=background_tasks, template=template, db=db)

        return { "message": "SMS sent successfully" }

    