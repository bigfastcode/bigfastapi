
from pydantic import BaseModel
from datetime import date 
from typing import List, Dict , Any, Optional


class _CommentBase(BaseModel):
    text : str 
    name : str
    email : str

class Comment(_CommentBase):
    id : int
    rel_id : int
    downvotes : int
    upvotes : int

    class Config:
        orm_mode = True

class CommentCreate(_CommentBase):
    pass

class CommentUpdate(_CommentBase):
    pass

class _ActorBase(BaseModel):
    name : str
    birthday : date

class Actor(_ActorBase):
    id : int
    class Meta:
        orm_mode = True 

