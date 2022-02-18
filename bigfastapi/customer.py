from datetime import datetime
from http.client import HTTPException
from typing import Optional
from fastapi import APIRouter
from bigfastapi.models import organisation_models
from bigfastapi.utils.utils import generate_short_id
from bigfastapi.schemas import customer_schemas, users_schemas
from bigfastapi.models import customer_models
import sqlalchemy.orm as orm
import fastapi
from bigfastapi.db.database import get_db
from uuid import uuid4
from fastapi.responses import JSONResponse
from fastapi import status
from .auth_api import is_authenticated
from fastapi_pagination import Page, add_pagination, paginate

app = APIRouter(tags=["Customers 💁"],)




@app.post("/customers", response_model=customer_schemas.CustomerCreateResponse,
                         status_code=status.HTTP_201_CREATED)
def create_customer(
    customer: customer_schemas.CustomerCreate, 
    db: orm.Session = fastapi.Depends(get_db),
    #user: users_schemas.User = fastapi.Depends(is_authenticated)
    ):
    organization = db.query(organisation_models.Organization).filter(organisation_models.Organization.id == customer.organization_id).first()
    if not organization: 
        return JSONResponse({"message": "Organization does not exist"}, status_code=status.HTTP_404_NOT_FOUND)
    customer_instance = customer_models.Customer(
        id = uuid4().hex,
        customer_id = generate_short_id(size=12),
        first_name = customer.first_name,
        last_name= customer.last_name,
        organization_id= organization.id,
        email= customer.email,
        phone_number= customer.phone_number,
        address= customer.address,
        gender= customer.gender,
        age= customer.age,
        postal_code= customer.postal_code,
        language= customer.language,
        country= customer.country,
        city= customer.city,
        region= customer.region,
        other_information = customer.other_information,
        country_code = customer.country_code,
        date_created = datetime.now(),
        last_updated = datetime.now()

    )
    db.add(customer_instance)
    db.commit()
    db.refresh(customer_instance)
    print(customer_instance)
    return {"message": "Customer created succesfully", "customer": customer_schemas.Customer.from_orm(customer_instance)}
    


@app.get('/customers', response_model=Page[customer_schemas.Customer],
            status_code=status.HTTP_200_OK)
def get_customers(
    organization_id: str,
    db: orm.Session = fastapi.Depends(get_db), 
    #user: users_schemas.User = fastapi.Depends(is_authenticated)
    ):
    customers = []
    organization = db.query(organisation_models.Organization).filter(organisation_models.Organization.id == organization_id).first()
    if not organization:
        return JSONResponse({"message": "Organization does not exist"}, status_code=status.HTTP_404_NOT_FOUND)
    customers = db.query(customer_models.Customer).filter_by(organization_id=organization_id)
    if customers:
        customer_list = list(map(customer_schemas.Customer.from_orm, customers))
        return paginate(customer_list)
    return paginate(customers)
    


@app.get('/customers/{customer_id}', response_model=customer_schemas.Customer)
def get_customer(
    customer_id: str, 
    db: orm.Session = fastapi.Depends(get_db),
    #user: users_schemas.User = fastapi.Depends(is_authenticated)
   ):
    customer = db.query(customer_models.Customer).filter(customer_models.Customer.customer_id == customer_id).first()
    if customer is not None:
        return customer_schemas.Customer.from_orm(customer)
    else:
        return JSONResponse({"message": "Customer does not exist"}, status_code=status.HTTP_404_NOT_FOUND)
        

@app.put('/customers/{customer_id}', 
        response_model=customer_schemas.Customer, 
        status_code=status.HTTP_202_ACCEPTED)
def update_customer(
    customer: customer_schemas.CustomerUpdate, 
    customer_id: str, 
    db: orm.Session = fastapi.Depends(get_db),
    #user: users_schemas.User = fastapi.Depends(is_authenticated)
    ):

    customer_instance = db.query(customer_models.Customer).filter(
                                customer_models.Customer.customer_id == customer_id).first()
    if not customer_instance :
        raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, 
                            detail={"message": "Customer does not exist"})

    if customer.organization_id:
        organization = db.query(organisation_models.Organization).filter(
                                organisation_models.Organization.id == customer.organization_id).first()
        if not organization:
            return JSONResponse({"message": "Organization does not exist"}, status_code=status.HTTP_404_NOT_FOUND)
        customer_instance.organization_id = organization.id
        
    if customer.first_name:
        customer_instance.first_name = customer.first_name
    if customer.last_name:
        customer_instance.last_name = customer.last_name
    if customer.email:
        customer_instance.email = customer.email
    if customer.phone_number:
        customer_instance.phone_number= customer.phone_number
    if customer.address:
        customer_instance.address= customer.address
    if customer.gender:
        customer_instance.gender= customer.gender
    if customer.age:
        customer_instance.age= customer.age
    if customer.postal_code:
        customer_instance.postal_code= customer.postal_code
    if customer.language:
        customer_instance.language= customer.language
    if customer.country:
        customer_instance.country= customer.country
    if customer.city:
        customer_instance.city= customer.city
    if customer.region:
        customer_instance.region= customer.region
    customer_instance.last_updated = datetime.now()
    db.commit()
    db.refresh(customer_instance)
    return customer_schemas.Customer.from_orm(customer_instance)


@app.delete('/customers/{customer_id}', 
            response_model=customer_schemas.ResponseModel, status_code=status.HTTP_200_OK)
def delete_customer(
    customer_id: str, 
    db: orm.Session = fastapi.Depends(get_db),
    #user: users_schemas.User = fastapi.Depends(is_authenticated)
    ):

    customer = db.query(customer_models.Customer).filter(
                        customer_models.Customer.customer_id == customer_id).first()
    if not customer:
        return JSONResponse({"message": "Customer does not exist"}, status_code=status.HTTP_404_NOT_FOUND)
    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted succesfully"}

        



add_pagination(app)
