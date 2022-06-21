from datetime import datetime
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Boolean
from uuid import uuid4
from bigfastapi.db import database

class ImportProgress(database.Base):
    __tablename__ = "import_progress"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    model = Column(String(255))
    current_line = Column(String(255))
    total_line = Column(String(255))
    error_message = Column(String(255))
    status = Column(Boolean, default=True)
    organization_id = Column(String(255))
    is_deleted= Column(Boolean, default=False)
    updated_at=Column(DateTime, default=datetime.now())
    created_at=Column(DateTime, default=datetime.now())


class FailedImports(database.Base):
    __tablename__ = "failed_import"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    model = Column(String(255))
    error = Column(String(255))
    line = Column(String(255), default=None)
    organization_id = Column(String(255))
    is_deleted= Column(Boolean, default=False)
    updated_at=Column(DateTime, default=datetime.now())
    created_at=Column(DateTime, default=datetime.now())


