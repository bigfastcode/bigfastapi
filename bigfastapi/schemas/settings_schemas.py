

import datetime as _dt
from lib2to3.pgen2.token import OP

import pydantic as pydantic
from pydantic import Field
from uuid import UUID
from typing import List, Optional

from validators import email

from bigfastapi.schemas.organisation_schemas import _OrganizationBase
import bigfastapi.schemas.users_schemas as UserSchema

from datetime import date
from pydantic import BaseModel



# class SettingsBase(BaseModel):
#     # email : str
    


class SettingsBase(BaseModel):
    email: str
    location : str
    phone_number : Optional[str] = None
    organization_size : Optional[str] = None
    organization_type : Optional[str] = None
    country : Optional[str] = None
    state : Optional[str] = None
    city : Optional[str] = None
    zip_code : Optional[int] = None




class SettingsUpdate(SettingsBase):
    pass


class Settings(SettingsBase):
    pass

    class Config:
        orm_mode = True








# class SettingsUpdate(Settings):
#     location : str
#     phone_number : str
#     organization_size : Optional[str] = None
#     organization_type : Optional[str] = None
#     country : Optional[str] = None
#     state : Optional[str] = None
#     city : Optional[str] = None
#     zip_code : Optional[int] = None


















# class SettingsBase(pydantic.BaseModel):
#     location : str
#     phone_number : str
#     email :str
#     organization_size :Optional [str] = None
#     organization_type :Optional [str] = None
    


# class SettingsCreate(SettingsBase):
#     pass




# class SettingsUpdate(SettingsBase):
#     pass


#     # location : str
#     # phone_number = str
#     # email = str
#     # organization_size = str
#     # organization_type = str
#     # country = str
#     # state = str
#     # city = str
#     # zip_code = int


# # class SettingsOrg(SettingsBase):
# #     id: str
# #     organisation_id: str


# #     class Config:
# #         orm_mode = True
        
        
        
# class SettingsUsers(SettingsBase):
#     id: str
#     user_id : str



#     class Config:
#         orm_mode = True





# # class SettingsForOrganisation(_OrganizationBase):
# #     settings: List[SettingsOrg] = []

# #     class Config:
# #         orm_mode = True



# class SettingsForUsers(UserSchema.User):
#     settings: List[SettingsUsers] = []

#     class Config:
#         orm_mode = True