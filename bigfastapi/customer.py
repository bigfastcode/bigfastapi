"""Customers

This file contains a group of API routes related to customers. 
You can create, retrieve, update and delete a customer object.

Importing the routes: import customers from bigfastapi and FastAPI
Then include with app.include_router(customers, tags=["Customers"])
After that, the following endpoints will become available:

 * /customers
 * /customers/import/{organization_id}
 * /customers/{customer_id}
 * /customers/organization/{organization_id}

"""

from typing import List
from xmlrpc.client import boolean
from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, BackgroundTasks
from bigfastapi.models.organisation_models import Organization
from bigfastapi.models.user_models import User
from bigfastapi.models.customer_models import Customer
from bigfastapi.schemas import customer_schemas, users_schemas
from bigfastapi.models import customer_models
from sqlalchemy.orm import Session
from bigfastapi.db.database import get_db
from uuid import uuid4
from fastapi.responses import JSONResponse
from .auth_api import is_authenticated
from fastapi_pagination import Page, add_pagination, paginate
import csv
import io
import pandas as pd
from bigfastapi.utils import paginator

app = APIRouter(tags=["Customers 💁"],)


@app.post("/customers",
          response_model=customer_schemas.CustomerResponse,
          status_code=status.HTTP_201_CREATED
          )
async def create_customer(
    background_tasks: BackgroundTasks,
    customer: customer_schemas.CustomerBase,

    db: Session = Depends(get_db),
    # user: users_schemas.User = Depends(is_authenticated)
):
    """Creates a new customer object.
    Args:
        customer: A pydantic schema that defines the customer request parameters. e.g
                        { "first_name" (required): "string", 
                        "last_name" (required): "string",
                        "unique_id" (required): "string",
                        "organization_id" (required): "09512826638748bd9bd06d22812cc06b",
                        "email": "string@gmail.com",
                        "phone_number": "string",
                        "business_name": "string",
                        "location": "string",
                        "gender": "string",
                        "age": 0,
                        "postal_code": "string",
                        "language": "string",
                        "country": "string",
                        "city": "string",
                        "region": "string",
                        "country_code": "string",
                        "other_info": [{"value": "string",
                            "key": "string"}]
                        }
        db (Session): Session database connection for storing the customer object.
        background_tasks: A parameter that allows tasks to be performed at the background
        user: user authentication validator
        
    Returns:
        status_code: HTTP_201_CREATED (new customer created)
        response_model: CustomerResponse e.g
                {message: str, customer: customer_instance}
    Raises
        HTTP_404_NOT_FOUND: object does not exist in db
        HTTP_401_FORBIDDEN: Not Authenticated
        HTTP_422_UNPROCESSABLE_ENTITY: request Validation error
    """
    organization = db.query(Organization).filter(
        Organization.id == customer.organization_id).first()
    if not organization:
        return JSONResponse({"message": "Organization does not exist", "customer": []},
                            status_code=status.HTTP_404_NOT_FOUND)

    customer_instance = await customer_models.add_customer(customer=customer, organization_id=customer.organization_id, db=db)

    if customer.other_info:
        background_tasks.add_task(customer_models.add_other_info, customer.other_info, customer_instance.customer_id, db)

    return {"message": "Customer created succesfully", "customer": customer_instance}


@app.post("/customers/import/{organization_id}",
          response_model=List[customer_schemas.CustomerResponse],
          status_code=status.HTTP_201_CREATED
          )
async def create_bulk_customer(
    organization_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    # user: users_schemas.User = Depends(is_authenticated)
):
    """Creates a multiple customer objects from a valid csv file.
    Args:
        organization_id: A unique identifier of an organisation
        background_tasks: A parameter that allows tasks to be performed at the background
        file: A standard csv file containing specific customer information to be created. e.g
                        { "first_name" (required): "string", 
                        "last_name" (required): "string",
                        "unique_id" (required): "string",
                        "organization_id" (required): "09512826638748bd9bd06d22812cc06b",
                        "email": "string@gmail.com",
                        "phone_number": "string",
                        "business_name": "string",
                        "location": "string",
                        "gender": "string",
                        "age": 0,
                        "postal_code": "string",
                        "language": "string",
                        "country": "string",
                        "city": "string",
                        "region": "string",
                        "country_code": "string",
                        "other_info": [{"value": "string",
                            "key": "string"}]
                        }
        db (Session): Session database connection for storing the customer object.
        user: user authentication validator
        
    Returns:
        status_code: HTTP_201_CREATED (new customer created)
        response_model: CustomerResponse e.g
                {message: str, customer: customer_instance}
    Raises
        HTTP_404_NOT_FOUND: object does not exist in db
        HTTP_401_FORBIDDEN: Not Authenticated
        HTTP_406_NOT_ACCEPTABLE: missing required fields or invalid file
    """

    if file.content_type != "text/csv":
        return JSONResponse({"message": "file must be a valid csv", "customer": []},
                            status_code=status.HTTP_406_NOT_ACCEPTABLE)

    organization = db.query(Organization).filter(
        Organization.id == organization_id).first()
    if not organization:
        return JSONResponse({"message": "Organization does not exist", "customer": []},
                            status_code=status.HTTP_404_NOT_FOUND)

    list_customers = await file_to_list_converter(file)
    required_cols = ["first_name", "last_name", "unique_id"]

    df_customers = pd.DataFrame(list_customers)
    sent_columns = df_customers.columns

    for col in required_cols:
        if col not in sent_columns:
            return JSONResponse({"message": f"A required field {col} is missing", "customer": []},
                                status_code=status.HTTP_406_NOT_ACCEPTABLE)

    background_tasks.add_task(unpack_create_customers,
                              df_customers, organization_id, db)

    return JSONResponse({"message": "Creating Customers...", "customer": list_customers},
                        status_code=status.HTTP_201_CREATED)


@app.get('/customers',
        #  response_model=customer_schemas.Customer,
         status_code=status.HTTP_200_OK
         )
async def get_customers(
    organization_id: str,
    search_value: str = None,
    sorting_key: str = None,
    page: int = 1,
    size: int = 50,
    reverse_sort: bool = True,
    db: Session = Depends(get_db),
    # user: users_schemas.User = Depends(is_authenticated)
):
    """fetches all customers registered in an organisation sorted by most recently added.
    Args:
        organization_id: A unique identifier of an organisation
        search_value (optional): A search string for filtering customers to be fetched
        sorting_key (optional): A string by which to sort the list of customers
             (most be a field in the customer object). defaults to "date_created" 
        reverse_sort (optional): A boolean to determine if objects 
            should be sorted in ascending or descending order. defaults to True (ascending order)
        db (Session): Session database connection for storing the customer object.
        user: user authentication validator
        
    Returns:
        status_code: HTTP_200_OK (request successful)
        response_model: paginated list of customers
    Raises
        HTTP_404_NOT_FOUND: orgainization not found
        HTTP_401_FORBIDDEN: Not Authenticated
        HTTP_422_UNPROCESSABLE_ENTITY: request Validation error
    """ 
    sort_dir = "asc" if reverse_sort == True else "desc"
    page_size = 50 if size < 1 or size > 100 else size
    offset = await paginator.off_set(page=page, size=page_size)
    total_items = await paginator.total_row_count(model=Customer, organization_id=organization_id, db=db)
    pointers = await paginator.page_urls(page=page, size=page_size, count=total_items, endpoint="/customers")

    organization = db.query(Organization).filter(
        Organization.id == organization_id).first()
    if not organization:
        return JSONResponse({"message": "Organization does not exist"}, status_code=status.HTTP_404_NOT_FOUND)

    if search_value:
        customers = await customer_models.search_customers(organization_id=organization_id, search_value=search_value,
            offset=offset, size=page_size, db=db)
    elif sorting_key:
        customers = await customer_models.sort_customers(organization_id=organization_id, sort_key=sorting_key, 
            offset=offset, size=page_size, sort_dir=sort_dir, db=db)
    else:
        customers = await customer_models.fetch_customers(organization_id=organization_id, offset=offset, 
                size=page_size, db=db)
    
    response = {"page": page, "size": page_size, "total": total_items,
        "previous_page":pointers['previous'], "next_page": pointers["next"], "items": customers,  }
    # customers.sort(key=lambda x: getattr(x, sorting_key, "firt_name"), reverse=reverse_sort)
    return response



@app.get('/customers/{customer_id}',
         response_model=customer_schemas.CustomerResponse,
         status_code=status.HTTP_200_OK
         )
async def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    # user: users_schemas.User = Depends(is_authenticated)
):
    """Fetches a single customer object from the database using a unique customer id.
    Args:
        customer_id: A unique identifier of a customer
        db (Session): Session database connection for storing the customer object.
        user: user authentication validator
        
    Returns:
        status_code: HTTP_200_OK (request successful)
        response_model: CustomerResponse (schema)
    Raises
        HTTP_404_NOT_FOUND: object does not exist in db
        HTTP_401_FORBIDDEN: Not Authenticated
    """
    customer = await customer_models.get_customer_by_id(customer_id=customer_id, db=db)
    if not customer:
        return JSONResponse({"message": "Customer does not exist"},
            status_code=status.HTTP_404_NOT_FOUND)
    other_info = await customer_models.get_other_customer_info(customer_id=customer_id, db=db)
    setattr(customer, 'other_info', other_info)

    return {"message": "successfully fetched details", 
        "customer": customer_schemas.Customer.from_orm(customer)}



@app.put('/customers/{customer_id}',
         response_model=customer_schemas.CustomerResponse,
         status_code=status.HTTP_202_ACCEPTED
         )
async def update_customer(
    background_tasks: BackgroundTasks,
    customer: customer_schemas.CustomerUpdate,
    customer_id: str, 
    db: Session = Depends(get_db),
    # user: users_schemas.User = Depends(is_authenticated)
):
    """Updates a customer's detail.
    Args:
        customer_id: A unique identifier of a customer
        background_tasks: A parameter that allows tasks to be performed at the background
        db (Session): Session database connection for storing the customer object.
        user: user authentication validator
        customer: A pydantic schema that defines the customer request parameters to be updated.
                All fields are optional e.g
                        { unique_id: Optional[str] =None
                        first_name: Optional[str] = None
                        last_name: Optional[str] = None
                        email: Optional[str] = None
                        phone_number: Optional[str] = None
                        organization_id: Optional[str] = None
                        business_name: str =None
                        location: str =None
                        gender: Optional[str] = None
                        age: Optional[int] = None
                        postal_code: Optional[str] = None
                        language: Optional[str] = None
                        country: Optional[str] = None
                        city: Optional[str] = None
                        region: Optional[str] = None
                        country_code: Optional[str] = None
                        other_info: [{"value": "string",
                            "key": "string"}]
                        }
    Returns:
        status_code: HTTP_200_OK (request successful)
        response_model: CustomerResponse (schema)
    Raises
        HTTP_404_NOT_FOUND: object does not exist in db
        HTTP_401_FORBIDDEN: Not Authenticated
    """ 
    customer_instance = db.query(Customer).filter(
        Customer.customer_id == customer_id).first()
    if not customer_instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": "Customer does not exist"})
    if customer.organization_id:
        organization = db.query(Organization).filter(
            Organization.id == customer.organization_id).first()
        if not organization:
            return JSONResponse({"message": "Organization does not exist"}, status_code=status.HTTP_404_NOT_FOUND)
        customer_instance.organization_id = organization.id

    updated_customer = await customer_models.put_customer(customer=customer,
                                          customer_instance=customer_instance, db=db)
    
    if customer.other_info:
        background_tasks.add_task(customer_models.add_other_info, customer.other_info, customer_id, db)

    return {"message": "Customer updated succesfully", "customer": updated_customer}


@app.delete('/customers/{customer_id}',
            response_model=customer_schemas.CustomerResponse,
            status_code=status.HTTP_200_OK
            )
async def soft_delete_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    # user: users_schemas.User = Depends(is_authenticated)
):
    """Deletes a single customer object from the database using a unique customer id.
    Args:
        customer_id: A unique identifier of a customer
        db (Session): Session database connection for storing the customer object.
        user: user authentication validator
        
    Returns:
        status_code: HTTP_200_OK (request successful)
        response_model: {"message": "Customer deleted succesfully"}
    Raises
        HTTP_404_NOT_FOUND: object does not exist in db
        HTTP_401_FORBIDDEN: Not Authenticated
    """ 
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id).first()
    if not customer:
        return JSONResponse({"message": "Customer does not exist"},
                            status_code=status.HTTP_404_NOT_FOUND)
    customer.is_deleted = True
    db.commit()
    db.refresh(customer)
    return JSONResponse({"message": "Customer deleted succesfully"},
                        status_code=status.HTTP_200_OK)


@app.delete('/customers/organization/{organization_id}',
            response_model=customer_schemas.CustomerResponse,
            status_code=status.HTTP_200_OK
            )
async def soft_delete_all_customers(
    organization_id: str,
    db: Session = Depends(get_db),
    # user: users_schemas.User = Depends(is_authenticated)
):  
    """Deletes all customers in an organization.
    Args:
        organization_id: A unique identifier of an organisation
        db (Session): Session database connection for storing the customer object.
        user: user authentication validator
        
    Returns:
        status_code: HTTP_200_OK (request successful)
        response_model: {"message": "Customers deleted succesfully"}
    Raises
        HTTP_404_NOT_FOUND: object does not exist in db
        HTTP_401_FORBIDDEN: Not Authenticated
    """    
    organization = db.query(Organization).filter(
        Organization.id == organization_id).first()
    if not organization:
        return JSONResponse({"message": "Organization does not exist"},
                            status_code=status.HTTP_404_NOT_FOUND)

    customers = db.query(Customer).filter_by(
        organization_id=organization_id, is_deleted=False)
    for customer in customers:
        customer.is_deleted = True
        db.commit()
        db.refresh(customer)
        print(customer)

    return JSONResponse({"message": "Customers deleted succesfully"},
                        status_code=status.HTTP_200_OK)

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


async def unpack_create_customers(df_customers, organization_id: str, db: Session = Depends(get_db)):
    posted_customers = []
    for kwargs in df_customers.to_dict(orient='records'):
        customer = Customer(**kwargs)
        added_customer = await customer_models.add_customer(customer=customer, organization_id=organization_id, db=db)
        posted_customers.append(added_customer)
    return posted_customers


