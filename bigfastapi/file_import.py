from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Depends
from bigfastapi.models.file_import_models import FileImports
from bigfastapi.db.database import get_db
import sqlalchemy.orm as orm

app = APIRouter(tags=["import_progress"],)

@app.get("/import/details")
async def importDetails(model: str, organization_id: str, 
    db: orm.Session = Depends(get_db)):
    file_import = db.query(FileImports).\
        filter(FileImports.model == model).\
        filter(FileImports.organization_id == organization_id).\
        filter(FileImports.is_deleted == False).first()
    if file_import == None:
        return {}

    return {
        'error_message' : file_import.error_message,
        'current_line' : file_import.current_line,
        'status': file_import.status,
        'total_line' : file_import.total_line
    }
