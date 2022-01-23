
import datetime
from uuid import uuid4
import bigfastapi.db.database as db
import sqlalchemy.orm as orm
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Integer


class File(db.Base):
    __tablename__ = "files"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    filename = Column(String(255))
    bucketname = Column(String(255))
    filesize = Column(Integer)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)



def find_file(bucket: str, filename: str, db: orm.Session):
    return db.query(File).filter((File.bucketname == bucket) & (File.filename == filename)).first()