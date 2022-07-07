import fastapi, os

from .models import file_models as model
from .schemas import file_schemas as schema

from uuid import uuid4
import sqlalchemy.orm as orm
from typing import List
from bigfastapi.db.database import get_db
from bigfastapi.utils import settings as settings
from fastapi.responses import FileResponse
from datetime import datetime

# Import the Router
app = fastapi.APIRouter()

@app.get("/files/{bucket_name}/", response_model=List[schema.File])
def get_all_files(db: orm.Session = fastapi.Depends(get_db)):
    """intro-->This endpoint returns all files that are in a single bucket. To use this endpoint you need to make a get request to the /files/{bucket_name}/ endpoint 
            paramDesc-->On get request the url takes a query parameter bucket_name
                param-->bucket_name: This is the name of the bucket containing files of interest
    returnDesc--> On successful request, it returns 
        returnBody--> a list of all files in the bucket
    """
    files = db.query(model.File).all()
    return list(map(schema.File.from_orm, files))


@app.get("/files/{bucket_name}/{file_name}", response_class=FileResponse)
def get_file(bucket_name: str, file_name: str, db: orm.Session = fastapi.Depends(get_db)):

    """Download a single file from the storage

    Args:
        bucket_name (str): the bucket to list all the files.
        file_name (str): the file that you want to retrieve

    Returns:
        A stream of the file
    """

    existing_file = model.find_file(bucket_name, file_name, db)
    if existing_file:
        local_file_path = os.path.join(os.path.realpath(settings.FILES_BASE_FOLDER), existing_file.bucketname, existing_file.filename)

        common_path = os.path.commonpath((os.path.realpath(settings.FILES_BASE_FOLDER), local_file_path))
        if os.path.realpath(settings.FILES_BASE_FOLDER) != common_path:
            raise fastapi.HTTPException(status_code=403, detail="File reading from unallowed path")

        return FileResponse(local_file_path)
    else:
        raise fastapi.HTTPException(status_code=404, detail="File not found")

    

@app.post("/upload-file/{bucket_name}/", response_model=schema.File)
async def upload_file(bucket_name: str, file: fastapi.UploadFile = fastapi.File(...),file_rename:bool =False, db: orm.Session = fastapi.Depends(get_db)):
    """intro-->This endpoint allows you to upload a file to a bucket/storage. To use this endpoint you need to make a post request to the /upload-file/{bucket_name}/ endpoint 
            paramDesc-->On post request the url takes the query parameter bucket_name
                param-->bucket_name: This is the name of the bucket you want to save the file to, You can request a list of files in a single folder if you nee to iterate.
                param-->file_rename: This is a boolean value that if set to true renames the hex values
    returnDesc--> On successful request, it returns 
        returnBody--> details of the file just created
    """
    
    # Make sure the base folder exists
    if settings.FILES_BASE_FOLDER == None or len(settings.FILES_BASE_FOLDER) < 2:
        raise fastapi.HTTPException(status_code=404, detail="Blog title already exists")

    # Make sure the bucket name does not contain any paths
    if bucket_name.isalnum() == False:
        raise fastapi.HTTPException(status_code=406, detail="Bucket name has to be alpha-numeric")

    # Create the base folder
    base_folder = os.path.realpath(settings.FILES_BASE_FOLDER)
    try:
        os.makedirs(base_folder)
    except:
        pass

    # Make sure bucket name exists
    try:
        os.makedirs(os.path.join(base_folder, bucket_name))
    except:
       pass
    if file_rename == True:
        file_type = file.filename.split(".")[-1]
        file.filename= str(uuid4().hex + "." + file_type)

    full_write_path = os.path.realpath(os.path.join(base_folder, bucket_name, file.filename))
    
    # Make sure there has been no exit from our core folder
    common_path = os.path.commonpath((full_write_path, base_folder))
    if base_folder != common_path:
        raise fastapi.HTTPException(status_code=403, detail="File writing to unallowed path")

    contents = await file.read()

    # Try to write file. Throw exception if anything bad happens
    try:
        with open(full_write_path, 'wb') as f:
            f.write(contents)
    except OSError:
        raise fastapi.HTTPException(status_code=423, detail="Error writing to the file")

    # Retrieve the file size from what we wrote on disk, so we are sure it matches
    filesize = os.path.getsize(full_write_path)

    # Check if the file exists
    existing_file = model.find_file(bucket_name, file.filename, db)
    if existing_file:
        existing_file.filesize = filesize
        existing_file.last_updated = datetime.utcnow()
        db.commit()
        db.refresh(existing_file)

        return schema.File.from_orm(existing_file)
    else:
        # Create a db entry for this file. 
        file = model.File(id=uuid4().hex, filename=file.filename, bucketname=bucket_name, filesize=filesize)
        db.add(file)
        db.commit()
        db.refresh(file)

        return schema.File.from_orm(file)
    

async def upload_image( file: fastapi.UploadFile = fastapi.File(...),  db: orm.Session = fastapi.Depends(get_db), bucket_name = str):
    
    # Make sure the base folder exists
    if settings.FILES_BASE_FOLDER == None or len(settings.FILES_BASE_FOLDER) < 2:
        raise fastapi.HTTPException(status_code=404, detail="base folder does not exist or base folder length too short")

    # Make sure the bucket name does not contain any paths
    if bucket_name.isalnum() == False:
        raise fastapi.HTTPException(status_code=406, detail="Bucket name has to be alpha-numeric")

    # Create the base folder
    base_folder = os.path.realpath(settings.FILES_BASE_FOLDER)
    try:
        os.makedirs(base_folder)
    except:
        pass

    # Make sure bucket name exists
    try:
        os.makedirs(os.path.join(base_folder, bucket_name))
    except:
       pass

    full_write_path = os.path.realpath(os.path.join(base_folder, bucket_name, file.filename))
    
    # Make sure there has been no exit from our core folder
    common_path = os.path.commonpath((full_write_path, base_folder))
    if base_folder != common_path:
        raise fastapi.HTTPException(status_code=403, detail="File writing to unallowed path")

    contents = await file.read()

    # Try to write file. Throw exception if anything bad happens
    try:
        with open(full_write_path, 'wb') as f:
            f.write(contents)
    except OSError:
        raise fastapi.HTTPException(status_code=423, detail="Error writing to the file")

    # Retrieve the file size from what we wrote on disk, so we are sure it matches
    filesize = os.path.getsize(full_write_path)

    # Check if the file exists
    existing_file = model.find_file(bucket_name, file.filename, db)
    if existing_file:
        existing_file.filesize = filesize
        existing_file.last_updated = datetime.utcnow()
        db.commit()
        db.refresh(existing_file)

        return existing_file.filename
    else:
        # Create a db entry for this file. 
        file = model.File(id=uuid4().hex, filename=file.filename, bucketname=bucket_name, filesize=filesize)
        db.add(file)
        db.commit()
        db.refresh(file)

        return file.filename
    
async def isFileExist(filePath: str):
     """Check the existence of a file in directory

    Args:
        File path (str): path to the file example "/testImages/test.png".
        
    Returns:
        Boolean: true or false depending if file exist
    """
     basePath = os.path.abspath("filestorage")
     fullPath =  basePath + filePath
     return os.path.exists(fullPath)

 
async def deleteFile(filePath: str):
    """Delete a file from directory

    Args:
        File path (str): path to the file example "/testImages/test.png".
        
    Returns:
        Boolean: true or false depending if operation is successful
    """
    try:
        basePath = os.path.abspath("filestorage")
        fullPath =  basePath + filePath
        os.remove(fullPath)
        return True
    except Exception as e:
        print(e)
        return False