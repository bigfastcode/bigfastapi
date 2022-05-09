
import datetime as datetime
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File
from typing import List, Optional
import fastapi as fastapi
from fastapi import HTTPException, status
import sqlalchemy.orm as orm
from .auth_api import is_authenticated
from .schemas import users_schemas as user_schema
from .schemas import product_schemas as schema
from .models import product_models as model
from .models import organisation_models as org_model
from .files import upload_image
from .utils import paginator

from bigfastapi.db.database import get_db

app = APIRouter(
    tags=["Product"]
    )

@app.get("/product", response_model=schema.ProductOut)
async def get_products(business_id: str, 
                search_value: str = None,
                sorting_key: str = None,
                datetime_constraint: datetime.datetime = None,
                page: int = 1,
                size: int = 50,
                reverse_sort: bool = True,
                db: orm.Session = fastapi.Depends(get_db)):

    """
    Intro-This endpoint allows you to retreive all non-deleted products in the database for a particular business. 
    To retreive all products, you need to make a get request to the /products/{business_id} endpoint. 
    
    returnDesc-On sucessful request, it returns:
    returnBody- a list of an array of product objects.
    """

    sort_dir = "desc" if reverse_sort == True else "asc"
    page_size = 50 if size < 1 or size > 100 else size
    page_number = 1 if page <= 0 else page
    offset = await paginator.off_set(page=page_number, size=page_size)

    if search_value:
        product_list, num_results = await model.search_products(business_id=business_id, 
                search_value=search_value, offset=offset, size=page_size, db=db)
    elif sorting_key:
        product_list = await model.sort_products(business_id=business_id, 
                sort_key=sorting_key, offset=offset, size=page_size, sort_dir=sort_dir, db=db)
    else:
        product_list = await model.fetch_products(business_id=business_id,
                offset=offset, size=page_size, timestamp=datetime_constraint, db=db)
    
    total_number = len(product_list)

    # products = db.query(model.Product).filter(model.Product.business_id == business_id, model.Product.is_deleted==False).all()

    if not product_list:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products present")

    pointers = await paginator.page_urls(page=page_number, size=page_size, count=total_number, endpoint=f"/product")
    response = {"page": page_number, "size": page_size, "total": total_number,"previous_page":pointers['previous'], "next_page": pointers["next"], 
                "items": product_list}
    
    return response

@app.get('/product/{product_id}', response_model=schema.ShowProduct)
def get_product(business_id: str, product_id: str, db: orm.Session = fastapi.Depends(get_db)):
    """
    Intro-This endpoint allows you to retreive details of a product in the database belonging to a business. 
    To retreive a product, you need to make a get request to the /products/{business_id}/{product_id} endpoint. 
    
    returnDesc-On sucessful request, it returns:
    returnBody- an array of product objects.
    """

    product = db.query(model.Product).filter(model.Product.business_id == business_id, model.Product.id == product_id, model.Product.is_deleted==False).first()

    if not product:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product does not exist")

    return product



@app.post("/product", response_model=schema.Product, status_code=status.HTTP_201_CREATED)
async def create_product(product: schema.ProductCreate, 
                   user: user_schema.User = fastapi.Depends(is_authenticated), 
                   db: orm.Session = fastapi.Depends(get_db)):
                   
    
    """
    Intro - This endpoint allows you to create a create a new product item.
    It takes in about four parameters. To create a product, you 
    need to make a post request to the /product endpoint

    paramDesc-
        reqBody-name: This is the name of the product to be created. 
        reqBody-description: This is the description of the product to be created. 
        reqBody-price: This is the set price for the product
        reqBody-discount: If a discount applies to the product, this is the field to put it in. 
    returnDesc-On sucessful request, it returns
        returnBody- the blog object.
    """
    #check if unique id is unique in the business
    id_status = db.query(model.Product).filter(model.Product.unique_id == product.unique_id, model.Product.business_id==product.business_id).first()
    if id_status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unique ID already exists')

    #check if user is allowed to create a product in the business
    if  org_model.is_organization_member(user_id=user.id, organization_id=product.business_id, db=db) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to create a product for this business")
    
    #set status
    if product.quantity > 0:
        product_status = True
    else:
        product_status = False

    
    #read and upload images
    if product.files != None:
        for file in product.files:
            image = await upload_image(file, db, bucket_name=product.unique_id)


    #Add product to database
    product = model.Product(id=uuid4().hex, created_by=user.id, business_id=product.business_id, name=product.name, description=product.description,
                            price=product.price, discount=product.discount, unique_id=product.unique_id, quantity=product.quantity
                            ,status = product_status)
    
    db.add(product)
    db.commit()
    db.refresh(product)


    #Add price record to PriceHistory table
    price_record = model.PriceHistory(id=uuid4().hex, product_id=product.id, price=product.price, created_by=user.id)
    db.add(price_record)
    db.commit()
    db.refresh(price_record)

    return product


@app.put('/product/{product_id}')
def update_product(product_update: schema.ProductUpdate,business_id: str, 
                    product_id: str,
                    user: user_schema.User = fastapi.Depends(is_authenticated), 
                    db: orm.Session = fastapi.Depends(get_db)):
    
    #check if user is allowed to update products

    #check if business exists


    product = db.query(model.Product).filter(model.Product.business_id==business_id, model.Product.id==product_id, model.Product.is_deleted==False).first()

    #check if product exits
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product does not exist')

    
    #check for change in price and update price history table
    if product.price != product_update.price:
        priceUpdate = model.PriceHistory(id=uuid4().hex, price=product_update.price, created_by=user.id, product_id=product.id)
        db.add(priceUpdate)
        db.commit()
        db.refresh(priceUpdate)
    
    product.name = product_update.name
    product.description = product_update.description
    product.discount = product_update.discount
    product.price = product_update.price
    product.updated_at = datetime.datetime.utcnow()

    db.commit()

    return {'message':'Product updated successfully'}


@app.delete("/product/{product_id}")
def delete_product(business_id: str, product_id: str, 
                    user: user_schema.User = fastapi.Depends(is_authenticated), 
                    db: orm.Session = fastapi.Depends(get_db)):
    
    """
    intro-This endpoint allows you to delete a particular product post. To delete a product, 
    you need to make a delete request to the /product/{business_id}/{product_id} endpoint.

    paramDesc-On delete request the url takes a query parameter business_id and product_id
    param-business_id: This is the unique id of the business
    param-product_id: This is the unique id of the product item

    returnDesc-On sucessful request, it returns an Object with message
       returnBody- "successfully deleted"
    """
    
    #check if user is in business and can delete product
    if org_model.is_organization_member(user_id=user.id, organization_id=business_id, db=db) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to delete a product for this business")


    #check if product exists in db
    product = model.select_product(product_id=product_id, business_id=business_id, db=db)
    if product is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product does not exist")
        
    product.is_deleted = True
    db.commit()

    return {"message":"successfully deleted"}




    

    








    

