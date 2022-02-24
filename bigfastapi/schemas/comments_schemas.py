import datetime
import pydantic
from pydantic import Field
from uuid import UUID
from typing import List, Optional


class CommentBase(pydantic.BaseModel):
    text : str 
    name : str
    email : str
    commenter_id: str = None

class Comment(CommentBase):
    id : str
    rel_id : str
    commenter_id: str = None
    downvotes : int
    upvotes : int
    time_created : datetime.datetime
    time_updated : datetime.datetime
    replies : List["Comment"]
    class Config:
        orm_mode = True

class CommentCreate(CommentBase):
    pass

class CommentUpdate(CommentBase):
    pass
        
