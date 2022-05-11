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