import datetime as datetime
import sqlalchemy.orm as orm
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Text, Float, BOOLEAN, Integer
from sqlalchemy import ForeignKey, Integer
from uuid import uuid4
import bigfastapi.db.database as database
import bigfastapi.schemas.users_schemas as schema

class Product(database.Base):
    __tablename__ = 'products'
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, index=True, nullable=True)
    price = Column(Float, index=True, nullable=False)
    discount = Column(Float, nullable=True)
    business_id = Column(String(255), ForeignKey("businesses.id", ondelete="CASCADE"))
    images = Column(Text, nullable=True)
    created_by = Column(String(255), ForeignKey("users.id"))
    unique_id = Column(String(255), index=True, nullable=False)
    quantity =  Column(Integer, index=True, nullable=False)
    status = Column(BOOLEAN, default=False)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    updated = Column(DateTime, default=datetime.datetime.utcnow)
    is_deleted = Column(BOOLEAN, default=False)


class PriceHistory(database.Base):
    __tablename__ = 'price_history'
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    product_id = Column(String(255), ForeignKey("products.id"))
    price = Column(Float, index=True, nullable=False)
    created_by = Column(String(255), ForeignKey("users.id"))
    created = Column(DateTime, default=datetime.datetime.utcnow)


def select_product(product_id: str, business_id: str, db: orm.Session):
    product = db.query(Product).filter(Product.business_id == business_id, Product.id == product_id).first()
    return product

def get_product_by_id(id: str, db: orm.Session):
    return db.query(Product).filter(Product.id == id).first()

