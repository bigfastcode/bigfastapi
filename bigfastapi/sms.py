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


class SendSMS():
    providers: Dict[str, str] = {
        "nuobject": "https://cloud.nuobjects.com/api/send"
    }

    @app.post("/sms/send", response_model=ResponseModel)
    async def send_sms(
        sms_details: sms_schema.SMS,
        db: orm.Session = fastapi.Depends(get_db)
    ):

        """
            An endpoint used to send an sms

            Returns:
                object (dict): status code, message
        """
        print(sms_details)
        if (sms_details.provider == "nuobject"):
            req = requests.put(
                SendSMS.providers.get("nuobject"),
                params={
                    "user": sms_details.user,
                    "pass": sms_details.passkey,
                    "from": sms_details.sender,
                    "to": sms_details.recipient,
                    "msg": sms_details.body
                }
            )
            if(req.status_code == 200):
                sms = sms_models.SMS(
                    id=uuid4().hex,
                    sender=sms_details.sender,
                    recipient=sms_details.recipient,
                    body=sms_details.body
                )

                db.add(sms)
                db.commit()
                db.refresh(sms)
            return {"code": req.status_code, "message": req.text}

        return {"message": "An error occured while sending sms"}

    async def send_sms_reminder(
        username: str, passkey: str, sender: str, recipient: str, body: str
    ):

        req = requests.put(
            SendSMS.providers.get("nuobject"),
            params={
                "user": username,
                "pass": passkey,
                "from": sender,
                "to": recipient,
                "msg": body
            }
        )
        return req
