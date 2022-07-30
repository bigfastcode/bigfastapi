import datetime
from typing import Optional
from pydantic import BaseModel


class Format(BaseModel):
    htmlString: Optional[str] = None
    pdfName: str
    FilePath: Optional[str] = None
    url: Optional[str] = None
