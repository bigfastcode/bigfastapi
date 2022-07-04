from datetime import datetime
from email.policy import default
from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Boolean
from uuid import uuid4
from bigfastapi.db import database

class FileImports(database.Base):
    __tablename__ = "imports"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    file_name = Column(String(255))
    model_name = Column(String(255))
    current_line = Column(String(255))
    total_line = Column(String(255))
    in_progress = Column(Boolean, default=False)
    organization_id = Column(String(255))
    user_id = Column(String(255))
    is_deleted= Column(Boolean, default=False)
    date_created = Column(DateTime, default=datetime.now())
    last_updated = Column(DateTime, default=datetime.now())


class FailedFileImports(database.Base):
    __tablename__ = "failed_imports"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    error = Column(String(255), default=None)
    import_id = Column(String(255), ForeignKey("imports.id"))
    line = Column(String(50), default=None)
    is_deleted= Column(Boolean, default=False)
    date_created = Column(DateTime, default=datetime.now())
    last_updated = Column(DateTime, default=datetime.now())
