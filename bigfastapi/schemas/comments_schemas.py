import datetime
import pydantic
from pydantic import Field
from uuid import UUID
from typing import List, Optional


class CommentBase(pydantic.BaseModel):
    id: Optional[str]
    text: Optional[str]
    name: Optional[str]
    email: Optional[str]
    commenter_id: str = None
    org_id: Optional[str] = None
    date_created: Optional[datetime.datetime] = datetime.datetime.now()
    last_updated: Optional[datetime.datetime] = datetime.datetime.now()


class Comment(CommentBase):
    id: str
    rel_id: str
    commenter_id: str = None
    downvotes: int
    upvotes: int
    date_created: Optional[datetime.datetime]
    last_updated: Optional[datetime.datetime]
    replies: List["Comment"]

    class Config:
        orm_mode = True


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    pass
