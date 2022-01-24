import fastapi
from fastapi import APIRouter
from .schemas import pdf_schema as pdfSchema
from .schemas import file_schemas as fileSchema
import pdfkit
import httpx
from uuid import uuid4

app = APIRouter()

@app.get("/exporttopdf")
def convertToPdf(body: pdfSchema.Format, file: fileSchema):
    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    
    if pdfkit.from_string(body.htmlString, body.pdfName, configuration=config):
        bucketname = 'users'
        savePdfAsFile(body.pdfName, id=uuid4().hex, bucketname, )
        return {"message" : "successful"}


def savePdfAsFile():
    data = {
        "filename": filename,
        "fileid": fileid,
        "bucketid": bucketid,
        "filesize": filesize,
    }

    httpx.post("/upload-file/{bucket_name}/", data)
    