from datetime import datetime
from random import randrange
from typing import List
from uuid import uuid4
from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, BackgroundTasks
from bigfastapi.models.failed_imports_models import FailedImports
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

@app.get("/import/details")

async def importDetails(model: str, organization_id: str, 
    db: orm.Session = Depends(get_db)):
    failedImports = db.query(FailedImports).\
        filter(FailedImports.organization_id == organization_id).\
        filter(FailedImports.model == model).\
        filter(FailedImports.is_deleted == False).all()
    
    importProgress = db.query(ImportProgress).\
        filter(ImportProgress.model == model).\
        filter(ImportProgress.organization_id == organization_id).\
        filter(ImportProgress.is_deleted == False).first()
    
    if importProgress == None or len(failedImports) == 0:
        return []
        
    return {
        'failed_imports' : failedImports,
        'current_line' : importProgress.current,
        'total_line' : importProgress.end
    }

async def saveImportProgress(current, end, model, organization_id: str, 
    db: orm.Session = Depends(get_db)):
    importProgress = ImportProgress(
        id=uuid4().hex, current=current, end=end,
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
    db.commit()
    return

async def deleteImportProgess(organization_id: str, model:str, 
    db: orm.Session = Depends(get_db)):

    db.query(ImportProgress).\
        filter(ImportProgress.organization_id == organization_id).\
        filter(ImportProgress.model == 'debts').\
        update({'is_deleted': True})
    db.commit()
    return