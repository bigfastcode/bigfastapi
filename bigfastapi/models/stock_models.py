import datetime as datetime
from fastapi import Depends
import sqlalchemy.orm as orm
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Text, Float, BOOLEAN, Integer
from sqlalchemy import ForeignKey, Integer, desc
from uuid import uuid4
import bigfastapi.db.database as database
import bigfastapi.schemas.users_schemas as schema
import bigfastapi.schemas.product_schemas as product_schema
from operator import and_, or_


class Stock(database.Base):
    __tablename__ = 'product_stock'
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    name = Column(String(255), index=True, nullable=False)
    product_id = Column(String(255), ForeignKey("products.id"))
    quantity = Column(Integer, index=True, nullable=False)
    price = Column(Float, index=True, nullable=False)
    status = Column(BOOLEAN, default=False)
    created_by = Column(String(255), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(String(255), ForeignKey("users.id"))
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_deleted = Column(BOOLEAN, default=False)


class StockPriceHistory(database.Base):
    __tablename__ = 'stock_price_history'
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    stock_id = Column(String(255), ForeignKey("product_stock.id"))
    price = Column(Float, index=True, nullable=False)
    created_by = Column(String(255), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
