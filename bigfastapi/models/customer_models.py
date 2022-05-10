from random import randrange
from sqlalchemy.types import String, DateTime, Integer, Boolean
from sqlalchemy import ForeignKey, desc
from sqlalchemy.sql import func
from bigfastapi.db.database import Base
from uuid import uuid4
from sqlalchemy.schema import Column
from sqlalchemy.orm import Session
from fastapi import Depends
from datetime import datetime
# from bigfastapi.models.organisation_models import Organization
from bigfastapi.schemas import customer_schemas
from bigfastapi.db.database import get_db
from bigfastapi.utils.utils import generate_short_id
from typing import List
from operator import and_, or_


class Customer(Base):
    __tablename__ = "customer"
    # id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    customer_id = Column(String(255), index=True, primary_key=True, 
                         default=generate_short_id(size=12))
    organization_id = Column(String(255), ForeignKey("businesses.id"))
    email = Column(String(255), index=True,  default="")
    first_name = Column(String(255), default="", index=True)
    last_name = Column(String(255), default="", index=True)
    unique_id = Column(String(255), nullable=False, index=True)
    phone_number = Column(String(255), index=True, default="")
    # business_name = Column(String(255), index=True,  default="")
    location = Column(String(255), index=True,  default="")
    gender = Column(String(255), index=True, default="")
    age = Column(Integer, index=True, default=0)
    postal_code = Column(String(255), index=True, default="")
    language = Column(String(255), index=True, default="")
    country = Column(String(255), index=True, default="")
    city = Column(String(255), index=True, default="")
    region = Column(String(255), index=True, default="")
    auto_reminder = Column(Boolean, index=True, default=False)
    country_code = Column(String(255), index=True, default="")
    is_deleted = Column(Boolean,  index=True, default=False)
    date_created = Column(DateTime, server_default=func.now())
    last_updated = Column(DateTime, nullable=False,
                          server_default=func.now(), onupdate=func.now())
    is_inactive = Column(Boolean, index=True, default=False)
    default_currency = Column(String(255), index=True)
    # customer_group_id = Column(String(255), ForeignKey("customer_group.group_id"))


class OtherInformation(Base):
    __tablename__ = "extra_customer_info"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    customer_id = Column(String(255), ForeignKey("businesses.id"))
    key = Column(String(255), index=True, default="")
    value = Column(String(255), index=True, default="")


class CustomerGroup(Base):
    __tablename__ = "customer_group"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    group_id = Column(String(255), index=True, default=generate_short_id(size=12))
    group_name = Column(String(255), index=True, default="")
    group_description =Column(String(255), index=True, default="")
    date_created = Column(DateTime, server_default=func.now())
    last_updated = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


#==============================Database Services=============================#

async def fetch_customers(
    organization_id: str,
    offset: int,
    timestamp: datetime = None,
    size: int = 50,
    db: Session = Depends(get_db)
    ):
    if timestamp:
        customers = db.query(Customer).filter(
            Customer.organization_id == organization_id).filter(
            Customer.is_deleted == False).filter(or_(
            Customer.is_inactive == False, Customer.is_inactive == None
            )).filter(Customer.last_updated > timestamp).order_by(Customer.date_created.desc()
            ).offset(offset=offset).limit(limit=size).all()
        total_items = db.query(Customer).filter(Customer.organization_id == organization_id).filter(
            Customer.is_deleted == False).filter(or_(
            Customer.is_inactive == False, Customer.is_inactive == None)).filter(
            Customer.last_updated > timestamp).count()
    else:
        customers = db.query(Customer).filter(
            Customer.organization_id == organization_id).filter(
            Customer.is_deleted == False).filter(or_(
            Customer.is_inactive == False, Customer.is_inactive == None
            )).order_by(Customer.date_created.desc()
            ).offset(offset=offset).limit(limit=size).all()
        total_items = db.query(Customer).filter(Customer.organization_id == organization_id).filter(
            Customer.is_deleted == False).filter(or_(
            Customer.is_inactive == False, Customer.is_inactive == None)).count()  
    return (list(map(customer_schemas.Customer.from_orm, customers)), total_items) 


async def search_customers(
    organization_id:str,
    search_value: str,
    offset: int, size:int=50,
    db:Session = Depends(get_db)
    ):  
    search_text = f"%{search_value}%"
    no_of_search_results1 =db.query(Customer).filter(and_(
        Customer.organization_id == organization_id,
        Customer.is_deleted == False)).filter(or_(
        Customer.is_inactive == False, Customer.is_inactive == None
        )).filter(or_(Customer.first_name.like(search_text),
        Customer.last_name.like(search_text))).count()

    no_of_search_results2 = db.query(Customer).filter(and_(
        Customer.organization_id == organization_id,
        Customer.is_deleted == False)).filter(or_(
        Customer.is_inactive == False, Customer.is_inactive == None
        )).filter(or_(Customer.unique_id.like(search_value),
        Customer.customer_id.like(search_value))).count()
    total_items = no_of_search_results1 +  no_of_search_results2

    customers_by_name = db.query(Customer).filter(and_(
        Customer.organization_id == organization_id,
        Customer.is_deleted == False)).filter(or_(
        Customer.is_inactive == False, Customer.is_inactive == None
        )).filter(or_(Customer.first_name.like(search_text),
        Customer.last_name.like(search_text))).order_by(
        Customer.date_created.desc()).offset(
        offset=offset).limit(limit=size).all()
    map_names = list(map(customer_schemas.Customer.from_orm, customers_by_name))

    customers_by_id =db.query(Customer).filter(and_(
        Customer.organization_id == organization_id,
        Customer.is_deleted == False)).filter(or_(
        Customer.is_inactive == False, Customer.is_inactive == None
        )).filter(or_(Customer.unique_id.like(search_value),
        Customer.customer_id.like(search_value))).order_by(
        Customer.date_created.desc()).offset(
        offset=offset).limit(limit=size).all()
    map_ids = list(map(customer_schemas.Customer.from_orm, customers_by_id))

    customer_list = [*map_names, *map_ids]
    return (customer_list, total_items)


async def sort_customers(
    organization_id:str,
    sort_key: str,
    offset: int, size:int=50,
    sort_dir: str = "asc",
    db:Session = Depends(get_db)
    ):  
    if sort_dir == "desc":
        customers = db.query(Customer).filter(
            Customer.organization_id == organization_id).filter(
            Customer.is_deleted == False).filter(or_(
            Customer.is_inactive == False, Customer.is_inactive == None
            )).order_by(desc(getattr(Customer, sort_key, "first_name"))
            ).offset(offset=offset).limit(limit=size).all()
    else:
        customers = db.query(Customer).filter(
            Customer.organization_id == organization_id).filter(
            Customer.is_deleted == False).filter(or_(
            Customer.is_inactive == False, Customer.is_inactive == None
            )).order_by(getattr(Customer, sort_key, "first_name")
            ).offset(offset=offset).limit(limit=size).all()
    total_items = db.query(Customer).filter(Customer.organization_id == organization_id).filter(
        Customer.is_deleted == False).filter(or_(
        Customer.is_inactive == False, Customer.is_inactive == None)).count()  
    return (list(map(customer_schemas.Customer.from_orm, customers)), total_items)


async def add_customer(
    customer: customer_schemas.CustomerBase,
    organization_id: str,
    db: Session = Depends(get_db)
):
    customer_instance = Customer(
        id = uuid4().hex,
        customer_id=customer.customer_id,
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
        date_created=customer.date_created,
        is_deleted = customer.is_deleted,
        last_updated=customer.last_updated
    )
    db.add(customer_instance)
    db.commit()
    db.refresh(customer_instance)
    return customer_schemas.Customer.from_orm(customer_instance)


async def bulk_add_customers(customers, organization_id: str, db:Session = Depends(get_db)):
    objects = [Customer(id=uuid4().hex,
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
        date_created=customer.date_created,
        is_deleted = customer.is_deleted,
        last_updated=customer.last_updated) for customer in customers]
    db.add_all(objects)
    db.commit()
    # db.refresh()
    return(objects)


async def add_other_info(
    list_other_info: List[customer_schemas.OtherInfo],
    customer_id: str,
    db: Session = Depends(get_db)
):
    res_obj = []
    for other_info in list_other_info:
        other_info_instance = OtherInformation(
            id=uuid4().hex,
            customer_id=customer_id,
            key=other_info.key,
            value=other_info.value
        )
        db.add(other_info_instance)
        db.commit()
        db.refresh(other_info_instance)
        res_obj.append(other_info_instance)
    return list(map(customer_schemas.OtherInfo.from_orm, res_obj))


async def put_customer(
    customer: customer_schemas.CustomerBase,
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
    customer_instance.last_updated = customer.last_updated
    db.commit()
    db.refresh(customer_instance)
    return customer_schemas.Customer.from_orm(customer_instance)


async def get_customer_by_id(customer_id: str, db: Session):
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id).first()
    if customer:
        return customer_schemas.Customer.from_orm(customer)
    return {}


async def get_other_customer_info(customer_id:str, db:Session):
    other_info = db.query(OtherInformation).filter(
        OtherInformation.customer_id == customer_id).all()
    return list(map( customer_schemas.OtherInfo.from_orm, other_info))


async def get_inactive_customers(organization_id:str, db:Session, offset:int, size:int):
    total_items = db.query(Customer).filter(
        Customer.organization_id==organization_id).filter(
        Customer.is_deleted == False).filter(
        Customer.is_inactive==True).count()

    customers= db.query(Customer).filter(
        Customer.organization_id==organization_id).filter(
        Customer.is_deleted == False).filter(
        Customer.is_inactive==True).order_by(
        Customer.last_updated.desc()).offset(
            offset=offset).limit(limit=size).all()
    return (list(map(customer_schemas.Customer.from_orm, customers)), total_items)

async def get_customer_by_unique_id(db:Session, unique_id, org_id):
    customers = db.query(Customer).filter(Customer.organization_id==org_id).filter(
        Customer.unique_id==unique_id).all()
    return list(map(customer_schemas.Customer.from_orm, customers))