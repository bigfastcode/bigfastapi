from datetime import datetime
from sqlalchemy.orm import Session, relationship, selectinload
from fastapi import Depends
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Boolean
from sqlalchemy import ForeignKey, Integer, desc
from bigfastapi.db.database import get_db
from uuid import  uuid4
from sqlalchemy.sql import func
from operator import or_
from bigfastapi.schemas import sale_schemas
from bigfastapi.utils.utils import generate_short_id
from bigfastapi.db import database
from bigfastapi.models import customer_models, product_models, receipt_models

class Sale(database.Base):
    __tablename__ = "sales"
    sale_id = Column(String(255), index=True, primary_key=True, default=generate_short_id(size=12))
    unique_id = Column(String(255), index=True, nullable=False)
    creator_id = Column(String(255), ForeignKey("users.id"))
    product_id = Column(String(255), ForeignKey("products.id"))
    receipt_id = Column(String(255), ForeignKey("newreceipts.id"))
    customer_id = Column(String(255), ForeignKey("customer.customer_id"))
    organization_id = Column(String(255), ForeignKey("businesses.id"))
    customer = relationship("Customer", backref=("customers"))
    product = relationship("Product", backref=("products"))
    receipt = relationship("Receipt", backref=("receipt"))
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
    datetime_constraint:datetime =None,
    sort_dir:str = "desc",
    sorting_key: str = "date_created",
    db: Session = Depends(database.get_db)
    ):

    total_items = db.query(Sale).filter(
            Sale.organization_id == organization_id).filter(
            Sale.is_deleted == False).count()

    if datetime_constraint:
        sales = db.query(Sale).filter(
            Sale.organization_id == organization_id).filter(
            Sale.is_deleted == False).filter(
            Sale.last_updated > datetime_constraint
            ).options(selectinload(Sale.customer) 
            ).options(selectinload(Sale.product)).order_by(
            desc(getattr(Sale, sorting_key, "date_created"))
            ).offset(offset=offset).limit(limit=size).all()
        total_items = db.query(Sale).filter(
            Sale.organization_id == organization_id).filter(
            Sale.is_deleted == False).filter(
            Sale.last_updated > datetime_constraint
            ).count()

    elif sort_dir == "desc":
        sales=db.query(Sale).filter(
            Sale.organization_id == organization_id).filter(
            Sale.is_deleted == False).options(selectinload(Sale.customer) 
            ).options(selectinload(Sale.product)).order_by(
            desc(getattr(Sale, sorting_key, "date_created"))
            ).offset(offset=offset).limit(limit=size).all()
    else:
        sales = db.query(Sale).filter(
            Sale.organization_id == organization_id).filter(
            Sale.is_deleted == False).options(selectinload(Sale.customer)
            ).options(selectinload(Sale.product)).order_by(
            getattr(Sale, sorting_key, "date_created")
            ).offset(offset=offset).limit(limit=size).all()
    return (sales, total_items)
    # return (list(map(sale_schemas.SaleResponse.from_orm, sales)), total_items)

async def search_sales(db:Session, organization_id: str,
    offset: int, search_value:str, size: int = 50):
    search_text = f"%{search_value}%"
    sales = db.query(Sale).join(customer_models.Customer).join(product_models.Product).filter(
        Sale.organization_id ==organization_id).filter(
        customer_models.Customer.first_name.like(search_text)|
        customer_models.Customer.last_name.like(search_text)|
        product_models.Product.name.like(search_text)|
        Sale.unique_id.like(search_value)|
        Sale.sale_id.like(search_value)|
        Sale.amount.like(search_value)).options(
        selectinload(Sale.product)).options(selectinload(
        Sale.customer)).offset(offset=offset).limit(limit=size).all()
    
    total_items = db.query(Sale).join(customer_models.Customer
        ).join(product_models.Product).filter(
        Sale.organization_id ==organization_id).filter(
        customer_models.Customer.first_name.like(search_text)|
        customer_models.Customer.last_name.like(search_text)|
        Sale.sale_id.like(search_value)|
        product_models.Product.name.like(search_text)|
        Sale.unique_id.like(search_value)|
        Sale.amount.like(search_value)).count()
    return (sales, total_items)

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
    return sale_instance

async def update_sale(sale_id:str, sale:sale_schemas.SaleUpdate, db:Session):
    sale_instance = db.query(Sale).filter(Sale.sale_id == sale_id).first()
    if sale.product_id:
        sale_instance.product_id =sale.product_id
    if sale.unique_id:
        sale_instance.unique_id = sale.unique_id
    if sale.customer_id:
        sale_instance.customer_id= sale.customer_id
    if sale.amount:
        sale_instance.amount = sale.amount
    if sale.currency:
        sale_instance.sale_currency = sale.sale_currency
    if sale.mode_of_payment:
        sale_instance.mode_of_payment = sale.mode_of_payment
    if sale.payment_status:
        sale_instance.payment_status = sale.payment_status
    if sale.sale_status:
        sale_instance.sales_status= sale.sales_status
    if sale.description:
        sale_instance.description= sale.description
    if sale.is_deleted:
        sale_instance.is_deleted= sale.is_deleted
    sale_instance.last_updated = sale.last_updated
    db.commit()
    db.refresh(sale_instance)
    return sale_instance

async def fetch_sale_by_id(sale_id:str, db:Session):
    sale = db.query(Sale).filter(Sale.sale_id == sale_id
            ).options(selectinload(Sale.customer) 
            ).options(selectinload(Sale.product)).first()
    return sale

async def delete_sale(sale_id:str, db:Session):
    sale = db.query(Sale).filter(Sale.sale_id == sale_id
            ).first()
    sale.is_deleted = True
    db.commit()
    db.refresh(sale)
    return sale

async def generate_unique_id(db:Session, org_id):
    Sales = db.query(Sale).filter(Sale.organization_id==org_id).count()
    return Sales+1

async def is_sale_valid(db:Session, unique_id:str, sale_id:str, org_id):
    by_unique_id = db.query(Sale).filter(Sale.organization_id==org_id).filter(
        Sale.unique_id==unique_id).first()
    by_sale_id = db.query(Sale).filter(Sale.sale_id==sale_id).first()
    if by_unique_id or by_sale_id:
        return True
    return False