import datetime
from typing import Optional
from pydantic import BaseModel


class Format(BaseModel):
    htmlString: str
    pdfName: str
