
class _CommentBase(_pydantic.BaseModel):
    text : str 
    name : str
    email : str

class Comment(_CommentBase):
    id : int
    rel_id : str
    downvotes : int
    upvotes : int
    time_created : _dt.datetime
    time_updated : _dt.datetime
    replies : List["Comment"]
    class Config:
        orm_mode = True

class CommentCreate(_CommentBase):
    pass

class CommentUpdate(_CommentBase):
    pass
        
