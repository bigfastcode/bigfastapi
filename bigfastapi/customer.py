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

from random import randrange
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, BackgroundTasks
from bigfastapi.models.organisation_models import Organization, is_organization_member, fetchOrganization
from bigfastapi.models.customer_models import Customer
from bigfastapi.schemas import customer_schemas, users_schemas
from bigfastapi.models import customer_models
from sqlalchemy.orm import Session
from bigfastapi.db.database import get_db
from fastapi.responses import JSONResponse
from .auth_api import is_authenticated
from bigfastapi.utils.utils import generate_short_id
from uuid import uuid4
import csv
from datetime import datetime
import io
from bigfastapi.utils import paginator

app = APIRouter(tags=["Customers 💁"],)


@app.post("/customers",
    response_model=customer_schemas.CustomerResponse,
    status_code=status.HTTP_201_CREATED
    )
async def create_customer(
    customer: customer_schemas.CustomerBase,
    db: Session = Depends(get_db),
    user: users_schemas.User = Depends(is_authenticated)
    ):
    """intro-->This endpoint allows you to create a new customer. To use this endpoint you need to make a post request to the /customers endpoint with a specified body of request

    returnDesc--> On sucessful request, it returns a 
        returnBody--> 
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
                            "key": "string"}]}
        db (Session): Session database connection for storing the customer object.
        background_tasks: A parameter that allows tasks to be performed at the background
        user: user authentication validator
        
    Returns:
        status_code: HTTP_201_CREATED (new customer created)
        response_model: CustomerResponse e.g
                {message: str, customer: customer_instance}
    Raises
        HTTP_404_NOT_FOUND: object does not exist in db
        HTTP_401_UNAURIZED: Not Authenticated
        HTTP_403_FORBIDDEN: User is not a member of organization
        HTTP_422_UNPROCESSABLE_ENTITY: request Validation error
    """
    try:
        organization = await fetchOrganization(orgId=customer.organization_id, db=db)
        if not organization:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                detail=INVALID_ORGANIZATION)

        is_valid_member =await is_organization_member(user_id=user.id, organization_id=organization.id, db=db)
        if is_valid_member == False:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=NOT_ORGANIZATION_MEMBER)
        
        existing_customers = await customer_models.get_customer_by_unique_id(db=db, 
            org_id=organization.id, unique_id=customer.unique_id)
        if existing_customers:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=NON_UNIQUE_ID)

        customer_instance = await customer_models.add_customer(customer=customer,
            organization_id=customer.organization_id, db=db)
        if customer.other_info:
            other_info = await customer_models.add_other_info(customer.other_info, customer_instance.customer_id, db)
            setattr(customer_instance, 'other_info', other_info)
        return {"message": "Customer created succesfully", "customer": customer_instance}
    except Exception as ex:
        if type(ex) == HTTPException:
            raise ex
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))


@app.post("/customers/import/{organization_id}",
    status_code=status.HTTP_200_OK
    )
async def create_bulk_customer(
    organization_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: users_schemas.User = Depends(is_authenticated)
    ):

    """intro-->This endpoint creates customer objects from a valid csv file. To use this endpoint you need to make a post request to the /customers/import/{organization_id} endpoint

    
    returnDesc--> On sucessful request, it returns 
        returnBody--> details of the newly created customers

    Creates a multiple customer objects from a valid csv file.
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
        HTTP_500_INTERNAL_SERVER_ERROR: unexpected error types

    """
    try:
        if file.content_type != "text/csv":
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, 
                detail= "file must be a valid csv file type")
        
        organization = await fetchOrganization(orgId=organization_id, db=db)
        if not organization:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=INVALID_ORGANIZATION)

        is_valid_member = await is_organization_member(user_id=user.id, organization_id=organization.id, db=db)
        if is_valid_member == False:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=NOT_ORGANIZATION_MEMBER)

        list_customers = await file_to_schema_converter(file=file, organization_id=organization_id, db=db)
        db.add_all(list_customers)
        db.commit()
        return JSONResponse({"message": f"{len(list_customers)} Customers Created Successfully"},
                            status_code=status.HTTP_200_OK)
    except Exception as ex:
        print(ex)
        if type(ex) == HTTPException:
            raise ex
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))


@app.get('/customers',
    response_model=customer_schemas.PaginatedCustomerResponse,
    status_code=status.HTTP_200_OK
    )
async def get_customers(
    organization_id: str,
    search_value: str = None,
    sorting_key: str = None,
    datetime_constraint: datetime =None,
    page: int = 1,
    size: int = 50,
    reverse_sort: bool = True,
    db: Session = Depends(get_db),
    user: users_schemas.User = Depends(is_authenticated)
    ):
    """intro-->This endpoint allows you to fetch all customers registered in an organisation sorted by most recently added. To use this endpoint you need to make a get request to the /customers endpoint

        paramDesc-->On get request, the request url takes in the query parameter organization_id and a number of other optional query parameters
            param-->organization_id: This is the unique id of the organization of interest
            param-->search_value: A search string for filtering customers to be fetch
            param-->sorting_key: A string by which to sort the list of customers
            param-->reverse_sort: A boolean to determine if objects should be sorted in ascending or descending order. defaults to True (ascending order)
            param-->size: This is the size per page, this is 10 by default
            param-->page: This is the page of interest, this is 1 by default
        returnDesc--> On sucessful request, it returns 
        returnBody--> details of the customers

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
    try:
        organization = await fetchOrganization(orgId=organization_id, db=db)
        if not organization:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=INVALID_ORGANIZATION)

        is_valid_member = await is_organization_member(user_id=user.id, organization_id=organization.id, db=db)
        if is_valid_member == False:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=NOT_ORGANIZATION_MEMBER)

        sort_dir = "asc" if reverse_sort == True else "desc"
        page_size = 50 if size < 1 or size > 100 else size
        page_number = 1 if page <= 0 else page
        offset = await paginator.off_set(page=page_number, size=page_size)
        organization = db.query(Organization).filter(
            Organization.id == organization_id).first()
        if not organization:
            return JSONResponse({"message": "Organization does not exist"}, status_code=status.HTTP_404_NOT_FOUND)
        if search_value:
            customers, total_items = await customer_models.search_customers(organization_id=organization_id, 
                search_value=search_value, offset=offset, size=page_size, db=db)
        elif sorting_key:
            customers, total_items = await customer_models.sort_customers(organization_id=organization_id, sort_key=sorting_key, 
                offset=offset, size=page_size, sort_dir=sort_dir, db=db)
        else:
            customers, total_items = await customer_models.fetch_customers(organization_id=organization_id,
                offset=offset, size=page_size, timestamp=datetime_constraint, db=db)
        pointers = await paginator.page_urls(page=page_number, size=page_size, count=total_items, endpoint="/customers")
        response = {"previous_page":pointers['previous'], "next_page": pointers["next"],
            "page": page_number, "size": page_size, "total": total_items, "items": customers}
        return response
    except Exception as ex:
        print(ex)
        if type(ex) == HTTPException:
            raise ex
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))



@app.get('/customers/{customer_id}',
         response_model=customer_schemas.CustomerResponse,
         status_code=status.HTTP_200_OK
         )
async def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    user: users_schemas.User = Depends(is_authenticated)
):  
    """intro-->This endpoint allows you to fetch a single customer object from the database using a unique customer id. To use this endpoint you need to make a get request to the /customers endpoint

        paramDesc-->On get request, the request url takes in the query parameter customer_id
            param-->customer_id: This is a unique identifier of the customer of interest
            
        returnDesc--> On sucessful request, it returns 
        returnBody--> details of the customer

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
    try:
        customer = await customer_models.get_customer_by_id(customer_id=customer_id, db=db)
        if not customer:
            return JSONResponse({"message": "Customer does not exist"},
                status_code=status.HTTP_404_NOT_FOUND)
        is_valid_member = await is_organization_member(user_id=user.id, organization_id=customer.organization.id, db=db)
        if is_valid_member == False:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=NOT_ORGANIZATION_MEMBER)
            
        other_info = await customer_models.get_other_customer_info(customer_id=customer_id, db=db)
        setattr(customer, 'other_info', other_info)

        return {"message": "successfully fetched details", 
            "customer": customer_schemas.Customer.from_orm(customer)}
    except Exception as ex:
        print(ex)
        if type(ex) == HTTPException:
            raise ex
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))



@app.put('/customers/{customer_id}',
         response_model=customer_schemas.CustomerResponse,
         status_code=status.HTTP_202_ACCEPTED
         )
async def update_customer(
    background_tasks: BackgroundTasks,
    customer: customer_schemas.CustomerUpdate,
    customer_id: str, 
    db: Session = Depends(get_db),
    user: users_schemas.User = Depends(is_authenticated)
):
    """intro-->This endpoint allows you to update a customer's details. To use this endpoint you need to make a put request to the /customers/{customer_id} endpoint

        paramDesc-->On get request, the request url takes the parameter, customer_id
            param-->customer_id: This is a unique identifier of the customer of interest
            
        returnDesc--> On sucessful request, it returns 
        returnBody--> updated details of the customer

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
    try:
        customer_instance = db.query(Customer).filter(
            Customer.customer_id == customer_id).first()
        if not customer_instance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail={"message": "Customer does not exist"})

        if customer.organization_id:
            organization = await fetchOrganization(orgId=customer.organization_id, db=db)
            if not organization:
                return JSONResponse({"message": INVALID_ORGANIZATION}, status_code=status.HTTP_404_NOT_FOUND)
            customer_instance.organization_id = organization.id

        is_valid_member = await is_organization_member(user_id=user.id, organization_id=customer_instance.organization_id, db=db)
        if is_valid_member == False:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=NOT_ORGANIZATION_MEMBER)

        updated_customer = await customer_models.put_customer(customer=customer,
                                            customer_instance=customer_instance, db=db)      
        if customer.other_info:
            update_other_info = await customer_models.add_other_info(customer.other_info, customer_id, db)

        other_info = await customer_models.get_other_customer_info(customer_id=customer_id, db=db)
        setattr(updated_customer, 'other_info', other_info)
        print(updated_customer)
        return {"message": "Customer updated succesfully", "customer": updated_customer}
    except Exception as ex:
        print(ex)
        if type(ex) == HTTPException:
            raise ex
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))


@app.delete('/customers/{customer_id}',
            response_model=customer_schemas.CustomerResponse,
            status_code=status.HTTP_200_OK
            )
async def soft_delete_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    user: users_schemas.User = Depends(is_authenticated)
):  
    """intro-->This endpoint allows you to delete a particular customer from the database. To use this endpoint you need to make a delete request to the /customers/{customer_id} endpoint

        paramDesc-->On delete request, the request url takes the parameter, customer_id
            param-->customer_id: This is a unique identifier of the customer of interest
            
        returnDesc--> On sucessful request, it returns message,
        returnBody-->  Customer deleted succesfully

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
    try:
        customer = db.query(Customer).filter(
            Customer.customer_id == customer_id).first()
        if not customer:
            return JSONResponse({"message": "Customer does not exist"},
                                status_code=status.HTTP_404_NOT_FOUND)

        is_valid_member =await is_organization_member(user_id=user.id, organization_id=customer.organization_id,db=db)
        if is_valid_member == False:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=NOT_ORGANIZATION_MEMBER)

        customer.is_deleted = True
        db.commit()
        db.refresh(customer)
        return JSONResponse({"message": "Customer deleted succesfully"},
                            status_code=status.HTTP_200_OK)
    except Exception as ex:
        print(ex)
        if type(ex) == HTTPException:
            raise ex
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))


@app.delete('/customers/organization/{organization_id}',
            response_model=customer_schemas.CustomerResponse,
            status_code=status.HTTP_200_OK
            )
async def soft_delete_all_customers(
    organization_id: str,
    db: Session = Depends(get_db),
    user: users_schemas.User = Depends(is_authenticated)
):  
    """intro-->This endpoint allows you to delete all customers in a particular organization. To use this endpoint you need to make a delete request to the /customers/organization/{organization_id} endpoint

        paramDesc-->On delete request, the request url takes the parameter, customer_id
            param-->customer_id: This is a unique identifier of the customer of interest
            
        returnDesc--> On sucessful request, it returns message,
        returnBody-->  Customers deleted succesfully

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
    try:
        organization = await fetchOrganization(orgId=organization_id, db=db)
        if not organization:
            return JSONResponse({"message": INVALID_ORGANIZATION},
                                status_code=status.HTTP_404_NOT_FOUND)
        is_valid_member =await is_organization_member(user_id=user.id, organization_id=organization.id, db=db)
        if is_valid_member == False:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=NOT_ORGANIZATION_MEMBER)
        customers = db.query(Customer).filter_by(
            organization_id=organization_id, is_deleted=False)
        for customer in customers:
            customer.is_deleted = True
            db.commit()
            db.refresh(customer)
            print(customer)

        return JSONResponse({"message": "Customers deleted succesfully"},
                            status_code=status.HTTP_200_OK)
    except Exception as ex:
        print(ex)
        if type(ex) == HTTPException:
            raise ex
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))


@app.put('/customers/inactive/selected{organization_id}',
    response_model=customer_schemas.CustomerResponse,
    status_code=status.HTTP_200_OK
    )
async def make_customers_inactive(
    organization_id:str,
    list_customer_id: List[str], 
    db: Session = Depends(get_db),
    user: users_schemas.User = Depends(is_authenticated)
    ):
    """intro-->This endpoint allows you to render customers inactive. To use this endpoint you need to make a put request to the /customers/inactive/selected endpoint

    returnDesc--> On sucessful request, it returns a 
        returnBody--> list of the customers rendered inactive
    """
    try:
        
        is_valid_member =await is_organization_member(user_id=user.id, organization_id=organization_id, db=db)
        if is_valid_member == False:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=NOT_ORGANIZATION_MEMBER)
        for customer_id in list_customer_id:
            customer = db.query(Customer).filter(
                Customer.customer_id == customer_id).first()
            customer.is_inactive = True
            db.commit()
            db.refresh(customer)
        return JSONResponse({"message": f"{len(list_customer_id)} Customers deactivated"},
                            status_code=status.HTTP_200_OK)
    except Exception as ex:
        print(ex)
        if type(ex) == HTTPException:
            raise ex
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))


#=================================Customer Services==============================#

async def file_to_schema_converter(organization_id, db, file: UploadFile = File(...), ):
    file_bytes = await file.read()
    customer_str = file_bytes.decode()
    reader = csv.DictReader(io.StringIO(customer_str))
    list_customers = []
    provided_ids = []
    for item in reader:
        customer = customer_schemas.CustomerBase(**item)
        existing_customers = await customer_models.get_customer_by_unique_id(
            db=db, org_id=organization_id, unique_id=customer.unique_id)
        if existing_customers or customer.unique_id in provided_ids:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, 
                detail=NON_UNIQUE_ID)
        provided_ids.append(customer.unique_id)
        model_customer= await schema_mapper(customer=customer, organization_id=organization_id)
        list_customers.append(model_customer)
    return list_customers

async def schema_mapper(customer:customer_schemas.CustomerBase, organization_id: str):
    mapped_object = customer_models.Customer(
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
        last_updated=customer.last_updated) 
    return mapped_object

NOT_ORGANIZATION_MEMBER = "User not authorized to carry out this action"
INVALID_ORGANIZATION = "Organization does not exist"
NON_UNIQUE_ID = "unique_id must be unique for all customers in this organization"

