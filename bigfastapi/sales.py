from .auth_api import is_authenticated
from random import randrange
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, BackgroundTasks
from bigfastapi.models import organisation_models, customer_models, sale_models
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

    created_sale = await sale_models.create_sale(sale=sale, db=db, user_id=user.id)
    return created_sale


@app.get("/sales",
    # response_model=customer_schemas.PaginatedCustomerResponse,
    status_code=status.HTTP_200_OK
    )
async def get_all_sale(
    organization_id:str,
    page: int = 1,
    size: int = 50,
    sorting_key: str = "date_created",
    search_value:str = None,
    reverse_sort: bool = True,
    db: Session = Depends(get_db),
    user: users_schemas.User = Depends(is_authenticated)
    ):

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
    sale =  await sale_models.fetch_sale_by_id(sale_id=sale_id, db=db)
    return sale

#-------Upcoming endpoints ----#
#send_sale_receipt
#update_sale
#delete_single_sale
#delete_selected_sales