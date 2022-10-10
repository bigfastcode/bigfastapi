from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Boolean
from uuid import uuid4
from bigfastapi.db.database import Base
from sqlalchemy import JSON


class FileImports(Base):
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


class FailedFileImports(Base):
    __tablename__ = "failed_imports"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    error = Column(String(255), default=None)
    import_id = Column(String(255), ForeignKey("imports.id"))
    line = Column(String(50), default=None)
    is_deleted= Column(Boolean, default=False)
    date_created = Column(DateTime, default=datetime.now())
    last_updated = Column(DateTime, default=datetime.now())


class FileExports(Base):
    __tablename__= "Exports"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    organization_id = Column(String(255), index=True)
    biz_partner_id = Column(String(255), ForeignKey("biz_partners.id"), index=True)
    biz_partner_type = Column(String(255),)
    business_name = Column(String(255),)
    file_name = Column(String(255), unique=True)
    file_id = Column(String(255), ForeignKey("files.id"))
    user_id = Column(String(255))
    report_type = Column(String(255))
    settings = Column(JSON())
    last_id = Column(String(255))
    current_line = Column(String(255))
    totat_count = Column(String(255))
    is_deleted= Column(Boolean, default=False)
    date_created = Column(DateTime, default=datetime.now())
    last_updated = Column(DateTime, default=datetime.now())
