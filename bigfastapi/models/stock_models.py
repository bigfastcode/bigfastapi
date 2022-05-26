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
from bigfastapi.models.product_models import Product
from operator import and_, or_


class Stock(database.Base):
    __tablename__ = 'product_stock'
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    product_id = Column(String(255), ForeignKey("products.id"))
    quantity = Column(Integer, index=True, nullable=False)
    price = Column(Float, index=True, nullable=False)
    status = Column(BOOLEAN, default=False)
    created_by = Column(String(255), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_deleted = Column(BOOLEAN, default=False)


# class StockPriceHistory(database.Base):
#     __tablename__ = 'stock_price_history'
#     id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
#     stock_id = Column(String(255), ForeignKey("product_stock.id"))
#     price = Column(Float, index=True, nullable=False)
#     created_by = Column(String(255), ForeignKey("users.id"))
#     created_at = Column(DateTime, default=datetime.datetime.utcnow)

#drop stock_price_history on migrations.py


#==============================Database Services=============================#

def create_stock(db, product_id, quantity, price, user_id):
    #set status
    if quantity > 0:
        stock_status = True
    else:
        stock_status = False

    #Add stock to database
    stock = Stock(id=uuid4().hex, product_id = product_id, quantity=quantity, 
                  price=price, status=stock_status,created_by=user_id)
    
    db.add(stock)
    db.commit()
    db.refresh(stock)

    return stock

def fetch_all_stocks_in_business(db, business_id):
    stocks = db.query(Stock).join(Product).filter(Product.business_id == business_id).all()
    return stocks

def fetch_stock_by_id(db, stock_id):
    stock = db.query(Stock).filter(Stock.id==stock_id, Stock.is_deleted==False).first()
    return stock

def reduce_stock_quantity(db, stock_id, number):
    stock = fetch_stock_by_id(db=db, stock_id=stock_id)
    new_quantity = stock.quantity - number
    stock.quantity = new_quantity
    db.commit()
