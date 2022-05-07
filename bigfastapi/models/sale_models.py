from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Boolean
from sqlalchemy import ForeignKey, Integer, desc
from bigfastapi.db.database import get_db
from uuid import  uuid4
from sqlalchemy.sql import func
from bigfastapi.schemas import sale_schemas
from bigfastapi.utils.utils import generate_short_id
from bigfastapi.db import database
from bigfastapi.models import product_models, customer_models, receipt_models

class Sale(database.Base):
    __tablename__ = "sales"
    sale_id = Column(String(255), index=True, primary_key=True, default=generate_short_id(size=12))
    unique_id = Column(String(255), index=True, nullable=False)
    creator_id = Column(String(255), ForeignKey("users.id"))
    product_id = Column(String(255), ForeignKey("products.id"))
    receipt_id = Column(String(255), ForeignKey("newreceipts.id"))
    customer_id = Column(String(255), ForeignKey("customer.customer_id"))
    organization_id = Column(String(255), ForeignKey("businesses.id"))
    amount = Column(Integer, nullable=False, index=True)
    sale_currency = Column(String(255), nullable=False, index=True)
    mode_of_payment = Column(String(255), index=True)
    payment_status = Column(String(255), index=True)
    sales_status = Column(String(255), index=True)
    description = Column(String(500), index=True)
    is_deleted = Column(Boolean,  index=True, default=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)


async def fetch_sales(
    organization_id: str,
    offset: int, size: int = 50,
    sort_dir: str = "asc",
    sorting_key: str = "date_created",
    db: Session = Depends(database.get_db)
    ):
    if sort_dir == "desc":
        sales = db.query(Sale).join(product_models.Product,  
            product_models.Product.id == Sale.product_id).filter(
            Sale.organization_id == organization_id).filter(Sale.is_deleted == False
            ).order_by(desc(getattr(Sale, sorting_key, "date_created"))
            ).offset(offset=offset).limit(limit=size).all()
            # , product_models.Product, customer_models.Customer, receipt_models.Receipt
    else:
        sales = db.query(Sale).join(product_models.Product,  
            product_models.Product.id == Sale.product_id).filter(
            Sale.organization_id == organization_id).filter(Sale.is_deleted == False
            ).order_by(getattr(Sale, sorting_key, "date_created")
            ).offset(offset=offset).limit(limit=size).all()
            # , product_models.Product, customer_models.Customer, receipt_models.Receipt
    total_items = db.query(Sale).join(product_models.Product,  
            product_models.Product.id == Sale.product_id).filter(
            Sale.organization_id == organization_id).filter(Sale.is_deleted == False
            ).count()
    return (list(map(sale_schemas.SaleBase.from_orm, sales)), total_items)


async def create_sale(    
    sale: sale_schemas.SaleBase,
    user_id:str,
    db: Session = Depends(get_db)
):
    sale_instance = Sale(
        sale_id= sale.sale_id,
        product_id =sale.product_id,
        unique_id = sale.unique_id,
        customer_id= sale.customer_id,
        organization_id = sale.organization_id,
        creator_id = user_id,
        amount = sale.amount,
        sale_currency = sale.sale_currency,
        mode_of_payment = sale.mode_of_payment,
        payment_status = sale.payment_status,
        sales_status= sale.sales_status,
        description= sale.description,
        is_deleted=sale.is_deleted,
        date_created = sale.date_created,
        last_updated = sale.last_updated,
        )
    db.add(sale_instance)
    db.commit()
    db.refresh(sale_instance)
    return sale_schemas.SaleBase.from_orm(sale_instance)


async def fetch_sale_by_id(sale_id:str, db:Session):
    sale = db.query(Sale).filter(
            Sale.sale_id == sale_id).first()
    if not sale:
        return {}
    return sale_schemas.SaleBase.from_orm(sale)


