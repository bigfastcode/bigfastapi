import os
import csv
import itertools
from uuid import uuid4
from typing import Any

from bigfastapi.models.file_import_models import FileImports, FailedFileImports
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
This is to convert file to list  starting from the last line processed
"""
#return list of items after line processed in chunks
def read_file_to_list(file:Any, line_processed: int = 1, file_for:str="Debt", field=None, is_length:bool=False):

    file_length = list(csv.DictReader(file))
    # print("reader_file length",file_length)


    if is_length ==True:
        return len(file_length)

    if field != None:
        fields = list(field)
    #  check this urgently
    
    line_no =int(line_processed)
    if line_no == 0:
        line_no = 1
    counter = itertools.count(line_no)
    
    if file_for == "Debt":
        list_file_content=[dict(x, **{"line":next(counter)}) for x in file_length[int(line_processed):MAX_ROWS + 1]]
        print(list_file_content)

    elif file_for == "customers":
        list_file_content = [dict(x, **{"line":next(counter), "other_info":[{"key":i, "value":x[i]} for i in x.keys() if x not in fields]}) for x in file_length[int(line_processed):MAX_ROWS +1]]
        print(list_file_content)
    
    return list_file_content

"""
This is to get the file from the folder after querying the imports table
"""
def retrieve_file(import_filename, bucket_name):
    base_folder = os.path.realpath(FILES_BASE_FOLDER)
    file = open(base_folder +"/" + bucket_name + "/"+import_filename, "rt")
    return file





