from ast import Str
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, root_validator
from fastapi import HTTPException, status
from bigfastapi.core import messages
from fastapi_utils.session import FastAPISessionMaker
from enum import Enum

# sessionmaker = FastAPISessionMaker(settings.DB_URL)



class ContactType(str, Enum):
    phone_number = "phone_number"
    email = "email"
    other_type = "other_type"


class ContactInfo(BaseModel):
    id: Optional[str]
    contact_data:str
    contact_tag: Optional[str]
    contact_type: ContactType
    contact_title: Optional[str]
    phone_country_code:Optional[str]
    is_primary: bool = False
    is_deleted : bool = False
    description :Optional[str]
    date_created:datetime = datetime.utcnow()
    last_updated: datetime= datetime.utcnow()

    class Config:
        orm_mode = True
    
    @root_validator(pre=True)
    @classmethod
    def validate_phone_number(cls, values):
        """Validate the presence of a country code when a phone number is provided"""
        phone_country_code = values.get('phone_country_code') 
        contact_type =  values.get("contact_type")
        contact_data =values.get("contact_data")
        if (contact_data != None) and (contact_type == ContactType.phone_number) and (phone_country_code == None):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail='missing country code: Every phone number requires a valid country code')
        return values


