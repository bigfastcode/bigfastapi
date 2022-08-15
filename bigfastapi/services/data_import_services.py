import os
import csv

from uuid import uuid4

from bigfastapi.models.data_import_models import FileImports, FailedFileImports
import sqlalchemy.orm as orm
from bigfastapi.utils.settings import FILES_BASE_FOLDER

MAX_ROWS = 100


def create_import_start_point(user_id:str,file_name, current_line, total_line, model_name, organization_id: str, 
    db: orm.Session):
    file_import = FileImports(
        id=uuid4().hex, file_name=file_name, current_line=current_line, total_line=total_line,
        model_name=model_name, organization_id=organization_id, user_id=user_id
    )
    db.add(file_import)
    db.commit()
    db.refresh(file_import)

    return file_import

async def update_import_current_line(id:str, current_line:str,
    db: orm.Session):
    db.query(FileImports).filter(FileImports.id == id).\
        update({'current_line': current_line})
    db.commit()
    return


# async def deleteImportProgess(organization_id: str, model:str, 
#     db: orm.Session):

#     db.query(FileImports).\
#         filter(FileImports.organization_id == organization_id).\
#         filter(FileImports.model == 'debts').\
#         update({'is_deleted': True})
#     db.commit()
#     return

async def log_import_error(line, error, import_id: str, 
    db: orm.Session):
    failedImport = FailedFileImports(
        id=uuid4().hex, line=line, error=error, import_id=import_id
    )
    db.add(failedImport)
    db.commit()
    db.refresh(failedImport)
    #  return failedImport and line +1
    return failedImport

# async def deleteImportError(organization_id: str, model: str, 
#     db: orm.Session):

#     db.query(FailedFileImports).filter(FailedFileImports.organization_id == organization_id).\
#         filter(FailedFileImports.model == model).update({'is_deleted': True})
#     db.commit()
#     return

def isEmpty(imports):
    if len(imports) != 0:
        return True
    return False




"""
This is to get the file from the folder after querying the imports table
"""
def retrieve_file(import_filename, bucket_name):
    folder = os.path.join(os.path.realpath(FILES_BASE_FOLDER), bucket_name, import_filename)
    # base_folder = os.path.join(FILES_BASE_FOLDER)
    file = open(folder, "rt")
    return file



def total_csv_rows(field):

    countrdr = csv.DictReader(field)
    totalrows = 0

    for row in countrdr:

        totalrows += 1

    return totalrows


