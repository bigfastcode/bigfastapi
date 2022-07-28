
import datetime
from uuid import uuid4
import bigfastapi.db.database as db
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Integer
import sqlalchemy.orm as orm



class File(db.Base):
    __tablename__ = "files"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    filename = Column(String(255), index=True)
    bucketname = Column(String(255), index=True)
    filesize = Column(Integer, index=True)
    # file_link = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

def find_file(bucket: str, filename: str, db: orm.Session):
    return db.query(File).filter((File.bucketname == bucket) & (File.filename == filename)).first()