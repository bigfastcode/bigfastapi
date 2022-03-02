from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile
from bigfastapi.models.organisation_models import Organization
from bigfastapi.models.user_models import User
from bigfastapi.models.customer_models import Customer, add_customer, put_customer
from bigfastapi.schemas import customer_schemas, users_schemas
from sqlalchemy.orm import Session
from bigfastapi.db.database import get_db
from uuid import uuid4
from fastapi.responses import JSONResponse
from .auth_api import is_authenticated
from fastapi_pagination import Page, add_pagination, paginate
import csv, io
from collections import namedtuple



app = APIRouter(tags=["Customers 💁"],)



@app.post("/customers", response_model=customer_schemas.CustomerCreateResponse,
                         status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: customer_schemas.CustomerCreate, 
    db: Session = Depends(get_db),
    #user: users_schemas.User = Depends(is_authenticated)
    ):
    organization = db.query(Organization).filter(
                    Organization.id == customer.organization_id).first()
    if not organization: 
        return JSONResponse({"message": "Organization does not exist", "customer": []}, 
                    status_code=status.HTTP_404_NOT_FOUND)

    customer_instance = await add_customer(customer=customer, organization=organization, db=db)
    return {"message": "Customer created succesfully", "customer": customer_instance}


@app.post("/customers/bulk",
                         status_code=status.HTTP_201_CREATED, )# response_model=customer_schemas.CustomerCreateResponse,
async def create_bulk_customer(organization_id: str, file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    #user: users_schemas.User = Depends(is_authenticated) 
    ):

    if file.content_type != "text/csv":
        return JSONResponse({"message":"file must be a valid csv", "customer": []},
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    organization = db.query(Organization).filter(
                    Organization.id == organization_id).first()
    if not organization: 
        return JSONResponse({"message": "Organization does not exist", "customer": []}, 
                    status_code=status.HTTP_404_NOT_FOUND)

    posted_customers = []
    list_customers= await file_to_list_converter(file)
    for customer in list_customers:
        if "first_name" not in customer: 
            return JSONResponse ({"message": "first_name is a required field", "customer": []}, 
                    status_code=status.HTTP_406_NOT_ACCEPTABLE)
        if "last_name" not in customer:
            return JSONResponse ({"message": "last_name is a required field", "customer": []}, 
                    status_code=status.HTTP_406_NOT_ACCEPTABLE)
        if "email" not in customer:
            customer["email"] = ""
        if "phone_number" not in customer:
            customer["phone_number"] = ""
        if "address" not in customer:
            customer["address"] = ""
        if "gender" not in customer:
            customer["gender"] = ""
        if "age" not in customer:
            customer["age"] = 0
        if "postal_code" not in customer:
            customer["postal_code"] = ""
        if "language" not in customer:
            customer["language"] = ""
        if "country" not in customer:
            customer["country"] = ""
        if "city" not in customer:
            customer["city"] = ""
        if "region" not in customer:
            customer["region"] = ""
        if "other_information" not in customer:
            customer["other_information"] = {}
        if "country_code" not in customer:
            customer["country_code"] = ""
        d_customer = namedtuple("Customer", customer.keys())(*customer.values())
        added_customer = await add_customer(customer=d_customer, organization=organization, db=db)
        posted_customers.append(added_customer)
    return {"message": "Customer created succesfully", "customer": posted_customers}


@app.get('/customers', response_model=Page[customer_schemas.Customer],
            status_code=status.HTTP_200_OK)
def get_customers(
    organization_id: str,
    db: Session = Depends(get_db), 
    #user: users_schemas.User = Depends(is_authenticated)
    ):
    customers = []
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        return JSONResponse({"message": "Organization does not exist"}, status_code=status.HTTP_404_NOT_FOUND)
    customers = db.query(Customer).filter_by(organization_id=organization_id, is_deleted = False)
    if customers:
        customer_list = list(map(customer_schemas.Customer.from_orm, customers))
        return paginate(customer_list)
    return paginate(customers)
    


@app.get('/customers/{customer_id}', response_model=customer_schemas.Customer)
def get_customer(
    customer_id: str, 
    db: Session = Depends(get_db),
    #user: users_schemas.User = Depends(is_authenticated)
   ):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if customer is not None:
        return customer_schemas.Customer.from_orm(customer)
    else:
        return JSONResponse({"message": "Customer does not exist"},
                    status_code=status.HTTP_404_NOT_FOUND)
        

@app.put('/customers/{customer_id}', response_model=customer_schemas.Customer, 
        status_code=status.HTTP_202_ACCEPTED)
def update_customer(
    customer: customer_schemas.CustomerUpdate, 
    customer_id: str, db: Session = Depends(get_db),
    #user: users_schemas.User = Depends(is_authenticated)
    ):
    customer_instance = db.query(Customer).filter(
                    Customer.customer_id == customer_id).first()
    if not customer_instance :
        raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, 
                            detail={"message": "Customer does not exist"})
    if customer.organization_id:
        organization = db.query(Organization).filter(
                                Organization.id == customer.organization_id).first()
        if not organization:
            return JSONResponse({"message": "Organization does not exist"}, status_code=status.HTTP_404_NOT_FOUND)
        customer_instance.organization_id = organization.id

    updated_customer = put_customer(customer=customer, 
                customer_instance=customer_instance, db=db)
    return {"message": "Customer created succesfully",
             "customer": customer_schemas.Customer.from_orm(updated_customer)}

 


@app.delete('/customers/{customer_id}', 
            response_model=customer_schemas.ResponseModel, status_code=status.HTTP_200_OK)
def soft_delete_customer(
    customer_id: str, 
    db: Session = Depends(get_db),
    #user: users_schemas.User = Depends(is_authenticated)
    ):
    

    customer = db.query(Customer).filter(
                        Customer.customer_id == customer_id).first()
    if not customer:
        return JSONResponse({"message": "Customer does not exist"}, status_code=status.HTTP_404_NOT_FOUND)
    customer.is_deleted = True
    db.commit()
    db.refresh(customer)
    return JSONResponse({"message": "Customer deleted succesfully"}, status_code=status.HTTP_200_OK)


@app.delete('/customers/organization/{org_id}', 
            response_model=customer_schemas.ResponseModel, status_code=status.HTTP_200_OK)
def soft_delete_all_customers(
    org_id: str, 
    user_id: str,
    db: Session = Depends(get_db),
    #user: users_schemas.User = Depends(is_authenticated)
    ):
    user = db.query(User).filter(User.id == user_id).first()
    if user.is_superuser != True:
        return JSONResponse({"message": "User has no authority to delete all customers"},
                                 status_code=status.HTTP_406_NOT_ACCEPTABLE)

    organization = db.query(Organization).filter(Organization.id == org_id).first()
    if not organization:
        return JSONResponse({"message": "Organization does not exist"}, 
                                    status_code=status.HTTP_404_NOT_FOUND)
    
    customers = db.query(Customer).filter_by(organization_id=org_id, is_deleted = False)
    for customer in customers:
        customer.is_deleted = True
        db.commit()
        db.refresh(customer)
        print(customer)

    return JSONResponse({"message": "Customers deleted succesfully"}, status_code=status.HTTP_200_OK)


add_pagination(app)


#=================================Customer Services==============================#

async def file_to_list_converter(file: UploadFile = File(...)):
    file_bytes = await file.read()
    customer_str = file_bytes.decode()
    reader = csv.DictReader(io.StringIO(customer_str))
    list_customers = []
    for records in reader:
        list_customers.append(records)
    return list_customers