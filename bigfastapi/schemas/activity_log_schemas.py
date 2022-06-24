import datetime
import pydantic
from pydantic import Field
from uuid import UUID
from typing import List, Optional
from datetime import date as date_type

class ActivitiesLogBase(pydantic.BaseModel):
    action : str = '' 
    object_url : str = ''
    organization_id: str

    class Config:
        orm_mode = True

class DeleteActivitiesLogBase(pydantic.BaseModel):
    organization_id: str

    class Config:
        orm_mode = True


class ActivitiesLogOutput(pydantic.BaseModel):
    id : str
    action : str = '' 
    object_id : str
    object_url : str = ''
    model_name: str
    user_id: str
    organization_id: str
    organization : list = []
    user : list = []
    user_id : str
    is_deleted : bool
    created_at : datetime.datetime

    class Config:
        orm_mode = True
