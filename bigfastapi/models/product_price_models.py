from calendar import WEDNESDAY
import datetime as datetime
import sqlalchemy.orm as orm
import bigfastapi.db.database as database
import bigfastapi.schemas.users_schemas as schema
import bigfastapi.schemas.product_schemas as product_schema
from fastapi import Depends
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Text, Float, BOOLEAN, Integer
from sqlalchemy import Date, ForeignKey, Integer, desc
from uuid import uuid4
from operator import and_, or_

# # product price table, when, which customer, priority, currency, day of week
class ProductPrice(database.Base):
    __tablename__ = 'product_price'
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    product_id = Column(String(255), ForeignKey("products.id"))
    stock_id = Column(String(255), ForeignKey("product_stock.id"))
    price = Column(Float, index=True, nullable=False)
    start = Column(Date)
    end = Column(Date)
    monday = Column(BOOLEAN, default=True)
    tuesday = Column(BOOLEAN, default=True)
    wednesday = Column(BOOLEAN, default=True)
    thursday = Column(BOOLEAN, default=True)
    friday = Column(BOOLEAN, default=True)
    saturday = Column(BOOLEAN, default=True)
    sunday = Column(BOOLEAN, default=True)
    customer_group = Column(String(255), index=True, nullable=False)
    currency = Column(String(255), index=True, nullable=False)
    priority = Column(Integer, default=5)
    created_by = Column(String(255), ForeignKey("users.id"))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    is_deleted = Column(BOOLEAN, default=False)


#==============================Database Services=============================# 

def fetch_product_prices(db: orm.Session, product_id: str):
    product_prices = db.query(ProductPrice).filter(ProductPrice.product_id==product_id, ProductPrice.is_deleted == False).all()

    return product_prices

def fetch_product_price_by_id(db: orm.Session, price_id: str):
    product_price = db.query(ProductPrice).filter(ProductPrice.id==price_id, ProductPrice.is_deleted == False).first()

    return product_price
