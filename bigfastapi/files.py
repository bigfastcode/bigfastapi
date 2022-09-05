import fastapi, os

from bigfastapi.models.user_models import User
from bigfastapi.utils.image_utils import generate_thumbnail_for_image

from .models import file_models as model
from .models.extra_info_models import ExtraInfo
from .schemas import file_schemas as schema

from uuid import uuid4
import sqlalchemy.orm as orm
from sqlalchemy import and_
from typing import List
from bigfastapi.db.database import get_db
from bigfastapi.utils import settings as settings
from fastapi.responses import FileResponse
from datetime import datetime
from bigfastapi.auth_api import is_authenticated

# Import the Router
app = fastapi.APIRouter()

@app.get("/files/{bucket_name}/", 
# response_model=List[schema.File]
)
def get_all_files(
    bucket_name:str,
    db: orm.Session = fastapi.Depends(get_db)
):
    """intro-->This endpoint returns all files that are in a single bucket. To use this endpoint you need to make a get request to the /files/{bucket_name}/ endpoint 
            paramDesc-->On get request the url takes a query parameter bucket_name
                param-->bucket_name: This is the name of the bucket containing files of interest
    returnDesc--> On successful request, it returns 
        returnBody--> a list of all files in the bucket
    """
    files = db.query(model.File).filter(model.File.bucketname == bucket_name).all()
    response = []
    for file in files:
        local_file_path = os.path.join(os.path.realpath(settings.FILES_BASE_FOLDER), file.bucketname, file.filename)
        common_path = os.path.commonpath((os.path.realpath(settings.FILES_BASE_FOLDER), local_file_path))
        if os.path.realpath(settings.FILES_BASE_FOLDER) != common_path:
            raise fastapi.HTTPException(status_code=403, detail="File reading from unallowed path")

        response.append(FileResponse(local_file_path))
    return response


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
async def upload_file(
    bucket_name: str, 
    file: fastapi.UploadFile = fastapi.File(...),
    file_rename:bool =False, 
    db: orm.Session = fastapi.Depends(get_db)
):
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


@app.post("/upload-cdn-link", response_model=schema.File)
async def upload_image_cdn_link(
    body: schema.CDNImage,
    db: orm.Session = fastapi.Depends(get_db),
    user: User = fastapi.Depends(is_authenticated)
):

    """
    Saves a cdn image url to files table. Doesn't create a new file
    :param bucket_name: unique id or name to use as relationship
    :param filename: name of file in cdn
    :param db: Database Session object
    """

    try:
        # check if file exists
        file = db.query(model.File).filter(and_(
            model.File.filename==body.filename,
            model.File.bucketname==body.bucketname
        )).first()
            
        # Create a db entry for this file if not exists.
        if not file:
            file = model.File(
                id=uuid4().hex,
                filename=body.filename,
                bucketname=body.bucketname,
                filesize=0
            )

            db.add(file)
            db.commit()
            db.refresh(file)

        return file
    except Exception as ex:
        print(ex)
        raise fastapi.HTTPException(status_code=400, detail=str(ex))


@app.get("/images/thumbnail/{bucketname}/{filename}")
def get_thumbnail(
    bucketname: str,
    filename: str,
    scale: str = "",
    width: int = 0,
    height: int = 0,
    db: orm.Session = fastapi.Depends(get_db),
    user: User = fastapi.Depends(is_authenticated)
):
    """
    Fetch thumbnail of specific size for filename if exists or create new if file exists
    :param bucketname: Unique id of original file
    :param filename: Original filename
    :param scale: How to scale image if create; options are width, height and empty means None
    :param width: Thumbnail width
    :param height: Thumbnail height
    :param db: Database Session object
    """

    root_location = os.path.abspath(os.environ.get("FILES_BASE_FOLDER", "filestorage"))
    image_folder = os.environ.get("IMAGES_FOLDER", "images")
    try:
        key = f"{filename}_{bucketname}_{(width, height)}"
        thumbnail = db.query(ExtraInfo).filter(ExtraInfo.key==key).first()
        if thumbnail:
            return FileResponse(os.path.join(root_location, image_folder, thumbnail.value))
        
        else:
            file = db.query(model.File).filter(and_(
                model.File.bucketname==bucketname,
                model.File.filename==filename
            )).first()

            if file:
                full_path_1 = os.path.join(root_location, image_folder, bucketname, filename)
                full_path_2 = os.path.join(root_location, bucketname.strip("/"), filename)
                full_path = full_path_1 if os.path.exists(full_path_1) else full_path_2

                thumbnail = generate_thumbnail_for_image(
                    full_image_path=full_path,
                    unique_id=bucketname,
                    width=width,
                    height=height,
                    scale=scale
                )
                
                if thumbnail:
                    return FileResponse(os.path.join(root_location, image_folder, thumbnail.value))
                
            raise fastapi.HTTPException(status_code=404, detail="No file to generate a thumbnail")
    except Exception as ex:
        print(ex)
        raise fastapi.HTTPException(status_code=400, detail=str(ex)) 


@app.post("/images/{bucket_name}/", response_model=schema.File)
async def upload_image(
    file: fastapi.UploadFile = fastapi.File(...),
    db: orm.Session = fastapi.Depends(get_db),
    bucket_name = str,
    user: User = fastapi.Depends(is_authenticated)
):
    
    """intro-->This endpoint allows you to upload an image to a bucket/storage. To use this endpoint you need to make a post request to the /images/{bucket_name}/ endpoint 
            paramDesc-->On post request the url takes the query parameter bucket_name
                param-->bucket_name: This is the name of the bucket you want to save the file to, You can request a list of files in a single folder if you nee to iterate.
                param-->file_rename: This is a boolean value that if set to true renames the hex values
    returnDesc--> On successful request, it returns 
        returnBody--> details of the file just created
    """

    # Make sure the base folder exists
    if settings.FILES_BASE_FOLDER == None or len(settings.FILES_BASE_FOLDER) < 2:
        raise fastapi.HTTPException(status_code=404, detail="base folder does not exist or base folder length too short")

    # Make sure the bucket name does not contain any paths
    if bucket_name.isalnum() == False:
        raise fastapi.HTTPException(status_code=406, detail="Bucket name has to be alpha-numeric")

    # Create the base folder
    base_folder = os.path.realpath(settings.FILES_BASE_FOLDER)
    image_folder = os.environ.get("IMAGES_FOLDER", "images")
    try:
        os.makedirs(os.path.join(base_folder, image_folder))
    except:
        pass

    # Make sure bucket name exists
    try:
        os.makedirs(os.path.join(base_folder, image_folder, bucket_name))
    except:
       pass

    full_write_path = os.path.realpath(
        os.path.join(base_folder, image_folder, bucket_name, file.filename)
    )
    
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