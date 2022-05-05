from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Boolean
from sqlalchemy import ForeignKey, desc
from uuid import  uuid4
from sqlalchemy.sql import func
from bigfastapi.schemas import sale_schemas
from bigfastapi.utils.utils import generate_short_id
from bigfastapi.db import database


class Sale(database.Base):
    __tablename__ = "sales"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    sale_id = Column(String(255), index=True, unique=True, default=generate_short_id(size=12))
    creator_id = Column(String(255), ForeignKey("users.id"))
    product_id = Column(String(255), ForeignKey("products.id"))
    customer_id = Column(String(255), ForeignKey("customer.customer_id"))
    organization_id = Column(String(255), ForeignKey("businesses.id"))
    amount = Column(String(255), index=True)
    sale_currency = Column(String(255), index=True)
    mode_of_payment = Column(String(255), index=True)
    payment_status = Column(String(255), index=True)
    sales_status = Column(String(255), index=True)
    description = Column(String(500), index=True)
    is_deleted = Column(Boolean,  index=True, default=False)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)


async def fetch_sales(
    organization_id: str,
    offset: int, size: int = 50,
    sort_dir: str = "asc",
    sort_key: str = "date_created",
    db: Session = Depends(database.get_db)
    ):
    if sort_dir == "desc":
        sales = db.query(Sale).filter(
            Sale.organization_id == organization_id).filter(Sale.is_deleted == False
            ).order_by(desc(getattr(Sale, sort_key, "date_created"))
            ).offset(offset=offset).limit(limit=size).all()
    else:
        sales = db.query(Sale).filter(
            Sale.organization_id == organization_id).filter(Sale.is_deleted == False
            ).order_by(getattr(Sale, sort_key, "date_created")
            ).offset(offset=offset).limit(limit=size).all()
    return list(map(sale_schemas.Sale.from_orm, sales))

