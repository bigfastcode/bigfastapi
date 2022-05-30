import sqlalchemy.orm as orm

from bigfastapi.schemas import file_schemas

from ..models.file_models import File

async def get_file_by_id(bucket: str, file_id: str, db: orm.Session):
    """
        This function returns the file that matches the id in the specified bucket from the database.
    """
    file = db.query(File).filter((File.bucketname == bucket) & (File.id == file_id)).first()
    if not file:
        return {}
    return file_schemas.File.from_orm(file)