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


# =================================== EMAIL SERVICES =================================#
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_TLS=False,
    MAIL_SSL=True,
    # MAIL_STARTTLS=False,
    # MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=os.path.join(settings.TEMPLATE_FOLDER, "email"),
)



async def send_email(
    background_tasks: BackgroundTasks,
    code: int = None,
    template: str = "",
    title: str = "",
    email_details: dict = None,
    recipients: list = None,
    template_body: dict = None,
    custom_template_dir: str = "",
    file: Union[UploadFile, None] = None,
    db: orm.Session = fastapi.Depends(get_db)
):
    if email_details is None:
        email_details = {}
    if recipients is None:
        recipients = []
    if template_body is None:
        template_body = {}
    try:
        if code:
            template_body["code"] = code

        if email_details:
            template_body["details"] = email_details

        if custom_template_dir != "":
            conf.TEMPLATE_FOLDER = custom_template_dir
        
        if file is not None:
            message = MessageSchema(
                subject=title,
                recipients=recipients,
                template_body=template_body,
                subtype="html",
                attachments=[file],
            )
        else:
            message = MessageSchema(
                subject=title,
                recipients=recipients,
                template_body=template_body,
                subtype="html",
            )

        fm = FastMail(conf)
        background_tasks.add_task(fm.send_message, message, template_name=template)

    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        ) from ex
