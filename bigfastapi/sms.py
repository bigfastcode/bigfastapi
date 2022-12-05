from .schemas import sms_schema
from .models import sms_models
from typing import Optional, Dict
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter
from bigfastapi.db.database import get_db
from pydantic import BaseModel
import fastapi
import sqlalchemy.orm as orm
from bigfastapi.utils import settings
import json
import requests

app = APIRouter(tags=["SMS"])


class ResponseModel(BaseModel):
    message: str


SMS_API = settings.SMS_API
ORGANIZATION_ID = settings.TELEX_ORGANIZATION_ID
ORGANIZATION_KEY = settings.TELEX_ORGANIZATION_KEY

@app.post("/sms/send")
async def SendSMS(
        sms_details: sms_schema.SMS,
        db: orm.Session = fastapi.Depends(get_db)
    ):

    """intro-->This endpoint allows you to send an sms. To use this endpoint you need to make a post request to the /sms/send endpoint

        reqBody-->sender: This is the name of the sender
        reqBody-->recipient: This is the recipient of the sms
        reqBody-->body: This is the content of the sms
        reqBody-->provider: This is the network provider
        reqBody-->user: This the current user 
        reqBody-->passkey: This is unique passkey
    
    returnDesc--> On sucessful request, it returns message,
        returnBody--> "success"
    """ 
 
    data={
        "sender": sms_details.sender,
        "message_type": sms_details.message_type,
        "customers": sms_details.recipient,
        "content": sms_details.content         
    }

    headers={
        'Content-Type': 'application/json',
        "ORGANIZATION-KEY":ORGANIZATION_KEY, 
        "ORGANIZATION-ID": ORGANIZATION_ID
    }

    req = requests.post(
        url=SMS_API, 
        json=data,
        headers=headers
    )

    if req.text["status"] == True:
        sms = sms_models.SMS(
                id=uuid4().hex,
                sender=sms_details.sender,
                recipient=sms_details.recipient,
                body=sms_details.body
            )

        db.add(sms)
        db.commit()
        db.refresh(sms)

    return json.loads(req.text)


async def send_sms(
        sender: str,
        recipient: list,
        content: str,
        message_type: str = "sms"
    ):

 
    data={
        "sender": sender,
        "message_type": message_type,
        "customers": recipient,
        "content": content         
    }

    headers={
        'Content-Type': 'application/json',
        "ORGANIZATION-KEY":ORGANIZATION_KEY, 
        "ORGANIZATION-ID": ORGANIZATION_ID
    }

    req = requests.post(
        url=SMS_API, 
        json=data,
        headers=headers
    )

    return json.loads(req.text)