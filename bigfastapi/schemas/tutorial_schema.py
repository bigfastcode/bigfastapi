import datetime as _dt
import string
from turtle import title
import pydantic
from uuid import UUID
from typing import List, Optional


class TutorialBase(pydantic.BaseModel):
    category: str
    title: str
    description: str
    thumbnail: Optional[str]
    stream_url: Optional[str]
    text: Optional[str]
    added_by: str


class TutorialDTO(TutorialBase):
    id: str
    date_created: _dt.datetime
    last_updated: _dt.datetime

    class Config:
        orm_mode = True


class TutorialResponseBase(pydantic.BaseModel):
    status_code: int
    resource_type: str


class TutorialRequest(TutorialBase):
    pass


class TutorialSingleRes(TutorialResponseBase):
    data: TutorialDTO


class TutorialListRes(TutorialResponseBase):
    data: List[TutorialDTO]
