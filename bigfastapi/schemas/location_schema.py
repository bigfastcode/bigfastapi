from ast import Str
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, root_validator


from bigfastapi.core import messages
from fastapi_utils.session import FastAPISessionMaker
# from bigfastapi.utils import settings as settings
from enum import Enum


# sessionmaker = FastAPISessionMaker(settings.DB_URL)


class Location(BaseModel):
    id: Optional[str]
    country: Optional[str]
    state: Optional[str]
    city: Optional[str]
    county: Optional[str]
    zip_code: Optional[str]
    full_address: Optional[str]
    street: Optional[str]
    significant_landmark: Optional[str]
    driving_instructions: Optional[str]
    contact: Optional[str]
    longitude: Optional[str]
    latitude: Optional[str]
    is_deleted: bool = False
    date_created: datetime = datetime.utcnow()
    last_updated: datetime = datetime.utcnow()

    class Config:
        orm_mode = True
