from datetime import datetime
from random import randrange
from typing import List
from uuid import uuid4
from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, BackgroundTasks
from bigfastapi.models.organisation_models import Organization
from bigfastapi.models.customer_models import Customer
from bigfastapi.schemas import customer_schemas, failed_imports_schemas, users_schemas
from bigfastapi.models import customer_models
from sqlalchemy.orm import Session
from bigfastapi.db.database import get_db
from fastapi.responses import JSONResponse
from .auth_api import is_authenticated
from bigfastapi.models.failed_imports_models import FailedImports
from bigfastapi.utils import paginator
import sqlalchemy.orm as orm

app = APIRouter(tags=["failed_imports"],)


@app.get("/failedimports")
async def failedImports(
    organization_id: str,
    db: Session = Depends(get_db),
    #user: users_schemas.User = Depends(is_authenticated)
):
    failedImports = db.query(FailedImports).\
        filter(FailedImports.organization_id == organization_id).\
        filter(FailedImports.is_deleted == False).all()
    
    if isEmpty(failedImports):
        return list(map(failed_imports_schemas.FailedImportOutput.from_orm, failedImports))

    return []  


async def logImportError(line, error, organization_id: str, 
    db: orm.Session = Depends(get_db)):
    failedImport = FailedImports(
        id=uuid4().hex, line=line,
        model='debts', error=error, organization_id=organization_id, 
        is_deleted=False, created_at= datetime.now(), 
        updated_at= datetime.now()
    )
    db.add(failedImport)
    db.commit()
    db.refresh(failedImport)

    return failedImport

def isEmpty(imports):
    if len(imports) != 0:
        return True
    return False
