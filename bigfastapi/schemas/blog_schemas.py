
import datetime as _dt

import pydantic as _pydantic
from pydantic import Field
from uuid import UUID
from typing import List, Optional

class _BlogBase(_pydantic.BaseModel):
    title: str
    content: str
class Blog(_BlogBase):
    id: str
    creator: str
    date_created: _dt.datetime
    last_updated: _dt.datetime

    class Config:
        orm_mode = True

class BlogCreate(_BlogBase):
    pass

class BlogUpdate(_BlogBase):
    pass
