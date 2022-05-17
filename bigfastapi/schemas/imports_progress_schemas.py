from datetime import datetime
from pydantic import BaseModel

class FailedImportOutput(BaseModel):
    id: str
    model: str
    error:str
    line:str
    organization_id: str
    is_deleted: str
    updated_at: datetime
    created_at: datetime

    class Config:
        orm_mode = True