import fastapi, os
from fastapi import FastAPI
from fastapi import APIRouter
from .schemas import pdf_schema as pdfSchema
import pdfkit
import shutil
from uuid import uuid4
from bigfastapi.db.database import get_db
from .models import file_models as file_model
import sqlalchemy.orm as orm
from bigfastapi.utils import settings as settings
from .schemas import file_schemas as file_schema

app = APIRouter()

@app.post("/exporttopdf", response_model=file_schema.File)

def convert_to_pdf(body: pdfSchema.Format, db: orm.Session = fastapi.Depends(get_db)):

    if pdfkit.from_string(body.htmlString, body.pdfName):
        bucketname = 'pdfs' #bucketname
        filename = body.pdfName
        pdfDir = './'+filename

        # get file size
        filestat = os.stat(pdfDir)
        filesize = filestat.st_size

        # Create the base folder
        base_folder = os.path.realpath(settings.FILES_BASE_FOLDER)
        try:
            os.makedirs(base_folder)
        except:
            pass

        bucket_path = os.path.realpath(os.path.join(base_folder, bucketname))

        # Make sure bucket name exists
        try:
            os.makedirs(os.path.join(base_folder, bucketname))
        except:
            pass

        # move file
        shutil.move(pdfDir, bucket_path)

        #save to db
        file = file_model.File(id = uuid4().hex, filename=filename , bucketname=bucketname, filesize=filesize)
        db.add(file)
        db.commit()
        db.refresh(file)

        #response message
        return file_schema.File.from_orm(file)
