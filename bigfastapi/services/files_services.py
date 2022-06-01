from sqlalchemy import and_
import sqlalchemy.orm as orm

from bigfastapi.schemas import file_schemas

from ..models.file_models import File

async def get_file(bucket: str, filename: str, db: orm.Session):
    """
        This function returns the file that matches the id in the specified bucket from the database.
    """
    return db.query(File).filter(and_(File.bucketname == bucket, File.filename == filename)).first()