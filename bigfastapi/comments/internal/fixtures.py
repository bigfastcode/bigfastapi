from sqlalchemy import Column, String, Integer, Date, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from bigfastapi.database import Base
# bigfastapi\bigfastapi\database.py
from bigfastapi.comments.models import commentable

@commentable
class Actor(Base):
    __tablename__ = 'actors'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    birthday = Column(Date)

    def __init__(self, name, birthday):
        super().__init__()
        self.name = name
        self.birthday = birthday
