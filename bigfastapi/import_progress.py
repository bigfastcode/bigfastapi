from datetime import datetime
from random import randrange
from typing import List
from uuid import uuid4
from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, BackgroundTasks
from bigfastapi.models.import_progress_models import ImportProgress
from bigfastapi.models.organisation_models import Organization
from bigfastapi.models.customer_models import Customer
from bigfastapi.schemas import customer_schemas, failed_imports_schemas, users_schemas
from bigfastapi.models import customer_models
from sqlalchemy.orm import Session
from bigfastapi.db.database import get_db
from fastapi.responses import JSONResponse
from .auth_api import is_authenticated
from bigfastapi.utils import paginator
import sqlalchemy.orm as orm

app = APIRouter(tags=["import_progress"],)


async def saveImportProgress(current, end, model, organization_id: str, 
    db: orm.Session = Depends(get_db)):
    importProgress = ImportProgress(
        id=uuid4().hex, current=current,
        model=model, organization_id=organization_id, 
        is_deleted=False, created_at= datetime.now(), 
        updated_at= datetime.now()
    )
    db.add(importProgress)
    db.commit()
    db.refresh(importProgress)

    return importProgress

async def updateImportProgress(current:str, id:str, 
    db: orm.Session = Depends(get_db)):
    db.query(ImportProgress).filter(ImportProgress.id == id).\
        update({'current': current})
    return

