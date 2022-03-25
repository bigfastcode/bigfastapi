import datetime as datetime
import sqlalchemy.orm as orm
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime
from sqlalchemy import ForeignKey
from uuid import uuid4
import bigfastapi.db.database as database
import bigfastapi.schemas.users_schemas as schema

class Blog(database.Base):
    __tablename__ = "blogs"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    creator = Column(String(255), ForeignKey("users.id"))
    title = Column(String(50), index=True, unique=True)
    content = Column(String(255), index=True)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)


def blog_selector(user: schema.User, id: str, db: orm.Session):
    blog = db.query(Blog).filter_by(creator=user.id).filter(Blog.id == id).first()
    return blog

def get_blog_by_title(title: str, db: orm.Session):
    return db.query(Blog).filter(Blog.title == title).first()