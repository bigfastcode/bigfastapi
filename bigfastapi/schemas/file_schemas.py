import datetime
from typing import Optional
from pydantic import BaseModel


class File(BaseModel):
    id: str
    filename: str
    bucketname: str
    filesize: int
    file_rename:Optional[bool]
    date_created: Optional[datetime.datetime]
    last_updated: Optional[datetime.datetime]

    class Config:
        schema_extra = {
            "example": {
                "filename": "test.jpeg",
                "fileid": "Ki7n2ZD4hyP3FyW3XX",
                "bucketid": "photos",
                "filesize": 2333,
            }
        }
        orm_mode = True

class Image(File):
    width: int
    Height: int

