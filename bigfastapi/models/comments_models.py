import datetime as _dt
from sqlite3 import Timestamp
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Enum, DateTime, Boolean, ARRAY, Text
from sqlalchemy import ForeignKey
from uuid import UUID, uuid4
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql import func
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE
from bigfastapi.utils.utils import generate_short_id
import bigfastapi.db.database as _database

class Comment(_database.Base):
    __tablename__ = "comment"

    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    model_type = Column(String(255)) 
    rel_id = Column(String(255))
    commenter_id = Column(String(255))

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     model_type = Column(String) 
#     rel_id = Column(String)
#     commenter_id = Column(String)
# >>>>>>> dev
    
    email = Column(String(255))
    name = Column(String(255))
    text = Column(String(500))
    downvotes = Column(Integer, default=0, nullable=False)
    upvotes = Column(Integer, default=0, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    p_id = Column(String(255), ForeignKey("comment.id", ondelete="cascade"))
    parent = _orm.relationship("Comment", backref=_orm.backref('replies',  cascade="all, delete-orphan"), remote_side=[id], post_update=True, single_parent=True, uselist=True)

    def __init__(self, *args, **kwargs):
        super().__init__()
        
        self.model_type = kwargs["model_name"] 
        self.commenter_id = kwargs["commenter_id"] 
        self.rel_id = kwargs["rel_id"]
        self.email = kwargs["email"] 
        self.name = kwargs["name"] 
        self.text = kwargs["text"] 
        self.p_id = kwargs.get("p_id", None)

    @hybrid_method
    def upvote(self):
        self.upvotes += 1
    
    @hybrid_method
    def downvote(self):
        self.downvotes += 1
