from enum import unique
from sqlalchemy.types import String, DateTime, Text, Integer, JSON, Boolean
from sqlalchemy import ForeignKey, text
from sqlalchemy.sql import func
from bigfastapi.db.database import Base
from uuid import uuid4
from sqlalchemy.schema import Column
from sqlalchemy.orm import Session
from fastapi import Depends
from datetime import datetime
from bigfastapi.schemas import customer_schemas
from bigfastapi.db.database import get_db
from bigfastapi.utils.utils import generate_short_id
from typing import List


class Customer(Base):
    __tablename__ = "customer"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    customer_id = Column(String(255), index=True,
                         default=generate_short_id(size=12))
    organization_id = Column(String(255), ForeignKey("businesses.id"))
    email = Column(String(255), index=True,  default="")
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    unique_id = Column(String(255), index=True)
    phone_number = Column(String(255), index=True, default="")
    business_name = Column(String(255), index=True,  default="")
    location = Column(String(255), index=True,  default="")
    gender = Column(String(255), index=True, default="")
    age = Column(Integer, index=True, default=0)
    postal_code = Column(String(255), index=True, default="")
    language = Column(String(255), index=True, default="")
    country = Column(String(255), index=True, default="")
    city = Column(String(255), index=True, default="")
    region = Column(String(255), index=True, default="")
    country_code = Column(String(255), index=True, default="")
    other_information = Column(JSON, default=text("'null'"))
    is_deleted = Column(Boolean,  index=True, default=False)
    date_created = Column(DateTime, server_default=func.now())
    last_updated = Column(DateTime, nullable=False,
                          server_default=func.now(), onupdate=func.now())

class OtherInformation(Base):
    __tablename__ = "extra_customer_info"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    customer_id = Column(String(255), ForeignKey("customer.customer_id"))
    key = Column(String(255), index=True, default="")
    value = Column(String(255), index=True, default="")


#==============================Database Services=============================#

async def fetch_customers(organization_id: str,
                          name: str = None,
                          db: Session = Depends(get_db)):
    customers = db.query(Customer).filter(
        Customer.organization_id == organization_id).filter(
        Customer.is_deleted == False
    )
    customer_list = list(map(customer_schemas.Customer.from_orm, customers))
    if not name:
        return customer_list
    found_customers = []
    for customer in customer_list:
        if name.lower() in customer.first_name.lower() or name.lower() in customer.last_name.lower():
            found_customers.append(customer)
    return found_customers


async def add_customer(
    customer: customer_schemas.CustomerBase,
    organization_id: str,
    db: Session = Depends(get_db)
    ):
    customer_instance = Customer(
        id=uuid4().hex,
        customer_id=generate_short_id(size=12),
        first_name=customer.first_name,
        last_name=customer.last_name,
        unique_id=customer.unique_id,
        organization_id=organization_id,
        email=customer.email,
        phone_number=customer.phone_number,
        location=customer.location,
        business_name=customer.business_name,
        gender=customer.gender,
        age=customer.age,
        postal_code=customer.postal_code,
        language=customer.language,
        country=customer.country,
        city=customer.city,
        region=customer.region,
        country_code=customer.country_code,
        date_created=datetime.now(),
        last_updated=datetime.now()
    )
    db.add(customer_instance)
    db.commit()
    db.refresh(customer_instance)
    return customer_schemas.Customer.from_orm(customer_instance)


async def add_other_info(
    list_other_info: List[customer_schemas.OtherInfo],
    customer_id:str,
    db: Session = Depends(get_db)
    ):
    res_obj = []
    for other_info in list_other_info:
        other_info_instance = OtherInformation(
            id = uuid4().hex,
            customer_id = customer_id,
            key = other_info.key,
            value = other_info.value
        )
        db.add(other_info_instance)
        db.commit()
        db.refresh(other_info_instance)
        res_obj.append(other_info_instance)

    return list(map(customer_schemas.OtherInfo.from_orm, res_obj))


async def put_customer(
    customer: customer_schemas.CustomerUpdate,
    customer_instance,
    db: Session = Depends(get_db)
):
    if customer.first_name:
        customer_instance.first_name = customer.first_name
    if customer.last_name:
        customer_instance.last_name = customer.last_name
    if customer.unique_id:
        customer_instance.unique_id = customer.unique_id
    if customer.email:
        customer_instance.email = customer.email
    if customer.phone_number:
        customer_instance.phone_number = customer.phone_number
    if customer.location:
        customer_instance.location = customer.location
    if customer.business_name:
        customer_instance.business_name = customer.business_name
    if customer.gender:
        customer_instance.gender = customer.gender
    if customer.age:
        customer_instance.age = customer.age
    if customer.postal_code:
        customer_instance.postal_code = customer.postal_code
    if customer.language:
        customer_instance.language = customer.language
    if customer.country:
        customer_instance.country = customer.country
    if customer.city:
        customer_instance.city = customer.city
    if customer.region:
        customer_instance.region = customer.region
    if customer.country_code:
        customer_instance.region = customer.country_code
    customer_instance.last_updated = datetime.now()
    db.commit()
    db.refresh(customer_instance)
    return customer_schemas.Customer.from_orm(customer_instance)


async def get_customer_by_id(customer_id: str, organization_id: str, db: Session):
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id and Customer.organization_id == organization_id).first()
    return customer
