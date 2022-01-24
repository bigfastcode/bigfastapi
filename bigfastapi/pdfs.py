import fastapi
from fastapi import APIRouter
from .schemas import pdf_schema as pdf_schema
import pdfkit

app = APIRouter()

@app.get("/exporttopdf")
def convertToPdf(body: pdf_schema.Format):
    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    
    if pdfkit.from_string(body.htmlString, body.pdfName, configuration=config):
        return {"message" : "successful"}
