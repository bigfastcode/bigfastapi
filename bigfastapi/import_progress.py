from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Depends
from bigfastapi.models.import_progress_models import ImportProgress, FailedImports
from bigfastapi.db.database import get_db
import sqlalchemy.orm as orm

app = APIRouter(tags=["import_progress"],)

@app.get("/import/details")
async def importDetails(model: str, organization_id: str, 
    db: orm.Session = Depends(get_db)):
    importProgress = db.query(ImportProgress).\
        filter(ImportProgress.model == model).\
        filter(ImportProgress.organization_id == organization_id).\
        filter(ImportProgress.is_deleted == False).first()
    if importProgress == None:
        return {}

    return {
        'error_message' : importProgress.error_message,
        'current_line' : importProgress.current_line,
        'total_line' : importProgress.total_line
    }


def saveImportProgress(current_line, total_line, model, organization_id: str, 
    db: orm.Session = Depends(get_db)):
    importProgress = ImportProgress(
        id=uuid4().hex, current_line=current_line, total_line=total_line,
        model=model, organization_id=organization_id, 
        is_deleted=False, created_at= datetime.now(), 
        updated_at= datetime.now()
    )
    db.add(importProgress)
    db.commit()
    db.refresh(importProgress)

    return importProgress

async def updateImportProgress(id:str, current_line:str, error_message:str='', status:bool=True, 
    db: orm.Session = Depends(get_db)):
    db.query(ImportProgress).filter(ImportProgress.id == id).\
        update({'current_line': current_line, 'error_message':error_message, 'status':status})
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

async def logImportError(line, error, organization_id: str, model: str, 
    db: orm.Session = Depends(get_db)):
    failedImport = FailedImports(
        id=uuid4().hex, line=line,
        model=model, error=error, organization_id=organization_id, 
        is_deleted=False, created_at= datetime.now(), 
        updated_at= datetime.now()
    )
    db.add(failedImport)
    db.commit()
    db.refresh(failedImport)

    return failedImport

async def deleteImportError(organization_id: str, model: str, 
    db: orm.Session = Depends(get_db)):

    db.query(FailedImports).filter(FailedImports.organization_id == organization_id).\
        filter(FailedImports.model == model).update({'is_deleted': True})
    db.commit()
    return

def isEmpty(imports):
    if len(imports) != 0:
        return True
    return False