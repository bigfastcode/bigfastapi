from .auth_api import is_authenticated
from random import randrange
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, BackgroundTasks
from bigfastapi.models import customer_models, sale_models, organisation_models, product_models
from bigfastapi.schemas import sale_schemas, users_schemas, customer_schemas
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
from bigfastapi.core import messages

app = APIRouter(tags=["Sales"],)


@app.post("/sales",
    response_model=sale_schemas.SaleResponse,
    status_code=status.HTTP_201_CREATED
    )
async def create_sale(
    sale: sale_schemas.SaleBase,
    db: Session = Depends(get_db),
    user: users_schemas.User = Depends(is_authenticated)
    ):
    try:
        organization = await organisation_models.fetchOrganization(orgId=sale.organization_id, db=db)
        if not organization:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                detail=messages.INVALID_ORGANIZATION)

        is_valid_member =await organisation_models.is_organization_member(user_id=user.id, organization_id=organization.id, db=db)
        if is_valid_member == False:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.NOT_ORGANIZATION_MEMBER)
        
        if not sale.unique_id:
            sale.unique_id = await sale_models.generate_unique_id(db=db, 
                org_id=organization.id)

        existing_customers = await sale_models.is_sale_valid(db=db, unique_id=sale.unique_id, 
            org_id=organization.id, customer_id=sale.customer_id)
        if existing_customers == True:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=messages.NON_UNIQUE_ID)

        created_sale = await sale_models.create_sale(sale=sale, db=db, user_id=user.id)
        return created_sale
    except Exception as ex:
        if type(ex) == HTTPException:
            raise ex
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))


@app.get("/sales",
    # response_model=customer_schemas.PaginatedCustomerResponse,
    status_code=status.HTTP_200_OK
    )
async def get_all_sale(
    organization_id:str,
    page: int = 1,
    size: int = 50,
    datetime_constraint:datetime = None,
    sorting_key: str = "date_created",
    search_value:str = None,
    reverse_sort: bool = True,
    db: Session = Depends(get_db),
    user: users_schemas.User = Depends(is_authenticated)
    ):

    organization = await organisation_models.fetchOrganization(orgId=organization_id, db=db)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
            detail=messages.INVALID_ORGANIZATION)

    is_valid_member =await organisation_models.is_organization_member(user_id=user.id, organization_id=organization_id, db=db)
    if is_valid_member == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.NOT_ORGANIZATION_MEMBER)

    sort_dir = "asc" if reverse_sort == True else "desc"
    page_size = 50 if size < 1 or size > 100 else size
    page_number = 1 if page <= 0 else page
    offset = await paginator.off_set(page=page_number, size=page_size)
    sales, total_items = await sale_models.fetch_sales(organization_id=organization_id, offset=offset, size=page_size, 
            sort_dir=sort_dir, sorting_key=sorting_key, db=db)
    pointers = await paginator.page_urls(page=page_number, size=page_size, count=total_items, endpoint="/customers")
    response = {"previous_page":pointers['previous'], "next_page": pointers["next"],
            "page": page_number, "size": page_size, "total": total_items, "items": sales}
    return response


@app.get("/sales/{sale_id}",
    # response_model=sale_schemas.SaleResponse,
    status_code=status.HTTP_200_OK
    )
async def get_single_sale(
    organization_id:str,
    sale_id: str,
    db: Session = Depends(get_db),
    user: users_schemas.User = Depends(is_authenticated)
):
    organization = await organisation_models.fetchOrganization(orgId=organization_id, db=db)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
            detail=messages.INVALID_ORGANIZATION)

    is_valid_member =await organisation_models.is_organization_member(user_id=user.id, organization_id=organization_id, db=db)
    if is_valid_member == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.NOT_ORGANIZATION_MEMBER)

    sale =  await sale_models.fetch_sale_by_id(sale_id=sale_id, db=db)
    return sale

#-------Upcoming endpoints ----#
#send_sale_receipt
#update_sale
#delete_single_sale
#delete_selected_sales