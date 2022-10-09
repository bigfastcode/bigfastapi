import datetime as datetime
from uuid import uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, String

from bigfastapi.db.database import Base


class VirtualTable(Base):
    __tablename__ = "virtual_tables"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    name = Column(String(255), index=True)
    parent_object_name = Column(String(255), index=True)
    organization_id = Column(String(255), index=True)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)


class VirtualTableData(Base):
    __tablename__ = "virtual_table_data"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    virtual_table_id = Column(String(255), ForeignKey("organizations.id"), index=True)
    str_column_1 = Column(String(191))
    str_column_2 = Column(String(191))
    str_column_3 = Column(String(191))
    int_column_1 = Column(String(191))
    int_column_2 = Column(String(191))
    int_column_3 = Column(String(191))
    organization_id = Column(String(255), index=True)
    date_created = Column(DateTime, default=datetime.datetime.now())
    last_updated = Column(DateTime, default=datetime.datetime.now())


class VirtualTableColumn(Base):
    __tablename__ = "virtual_table_columns"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    virtual_table_id = Column(String(255), ForeignKey("organizations.id"), index=True)
    virtual_column_name = Column(String(191))
    db_table_name = Column(String(191))
    db_table_column_name = Column(String(191))
    type = Column(String(50), nullable=True)
    organization_id = Column(String(255), index=True)
    date_created = Column(DateTime, default=datetime.datetime.now())
    last_updated = Column(DateTime, default=datetime.datetime.now())
