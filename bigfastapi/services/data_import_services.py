from datetime import datetime
from uuid import uuid4
from fastapi import Depends
from bigfastapi.models.file_import_models import FileImports, FailedFileImports
from bigfastapi.db.database import get_db
import sqlalchemy.orm as orm

FILE_BUCKET_NAME = 'imports'


def save_import_progress(user_id:str,file_name, current_line, total_line, model_name, organization_id: str, 
    db: orm.Session = Depends(get_db)):
    file_import = FileImports(
        id=uuid4().hex, file_name=file_name, current_line=current_line, total_line=total_line,
        model_name=model_name, organization_id=organization_id, user_id=user_id
    )
    db.add(file_import)
    db.commit()
    db.refresh(file_import)

    return file_import

async def update_imports(id:str, current_line:str,
    db: orm.Session = Depends(get_db)):
    db.query(FileImports).filter(FileImports.id == id).\
        update({'current_line': current_line})
    db.commit()
    return

# async def deleteImportProgess(organization_id: str, model:str, 
#     db: orm.Session = Depends(get_db)):

#     db.query(FileImports).\
#         filter(FileImports.organization_id == organization_id).\
#         filter(FileImports.model == 'debts').\
#         update({'is_deleted': True})
#     db.commit()
#     return

async def log_import_error(line, error, import_id: str, 
    db: orm.Session = Depends(get_db)):
    failedImport = FailedFileImports(
        id=uuid4().hex, line=line, error=error, import_id=import_id
    )
    db.add(failedImport)
    db.commit()
    db.refresh(failedImport)
    #  return failedImport and line +1
    return failedImport

# async def deleteImportError(organization_id: str, model: str, 
#     db: orm.Session = Depends(get_db)):

#     db.query(FailedFileImports).filter(FailedFileImports.organization_id == organization_id).\
#         filter(FailedFileImports.model == model).update({'is_deleted': True})
#     db.commit()
#     return

def isEmpty(imports):
    if len(imports) != 0:
        return True
    return False

#  rename and save fi