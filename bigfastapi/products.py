
import os
import fastapi as fastapi
import datetime as datetime
import sqlalchemy.orm as orm
import secrets
from uuid import uuid4
from fastapi import APIRouter, Depends, UploadFile, File
from typing import List, Optional
from fastapi import HTTPException, status
from .auth_api import is_authenticated
from .schemas import users_schemas as user_schema
from .schemas import product_schemas as schema
from .models import product_models as model
from .models.organisation_models import Organization
from .models import file_models as file_model
from .files import upload_image
from .utils import paginator
from .core import helpers
from bigfastapi.utils.schema_form import as_form
from starlette.requests import Request
from fastapi.responses import FileResponse
from bigfastapi.utils import settings as settings
from bigfastapi.db.database import get_db

app = APIRouter(
    tags=["Product"]
    )


@app.post("/product", response_model=schema.Product, status_code=status.HTTP_201_CREATED)
async def create_product(product: schema.ProductCreate=Depends(schema.ProductCreate.as_form), 
                   user: user_schema.User = fastapi.Depends(is_authenticated), 
                   product_image: Optional[List[UploadFile]] = File(None) ,
                   db: orm.Session = fastapi.Depends(get_db)):
       
    
    """
    Intro - This endpoint allows you to create a create a new product item.
    It takes in four parameters. To create a product, you 
    need to make a post request to the /product endpoint

    paramDesc-
        reqBody-name: This is the name of the product to be created. 
        reqBody-description: This is the description of the product to be created. 
        reqBody-unique_id: This is a user given unique id for the product. Optional
        reqBody-image: Optional product image
    returnDesc-On sucessful request, it returns

        returnBody- the product object.
    """
    #check if unique id is unique in the business
    id_status = db.query(model.Product).filter(model.Product.unique_id == product.unique_id, model.Product.business_id==product.business_id).first()
    if id_status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unique ID already exists')

    #check if user is allowed to create a product in the business
    if  helpers.Helpers.is_organization_member(user_id=user.id, organization_id=product.business_id, db=db) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to create a product for this business")

    #check and generate unique ID
    if product.unique_id is None:
        product.unique_id = uuid4().hex

    #Add product to database
    product = model.Product(id=uuid4().hex, created_by=user.id, business_id=product.business_id, name=product.name, description=product.description,
                             unique_id=product.unique_id) 
    
    db.add(product)
    db.commit()
    db.refresh(product)

     #process and upload image
    if product_image:
        for file in product_image:
            filename = file.filename
            extension = filename.split(".")[1]

            if extension not in ["png", "jpg", "jpeg"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="File format not allowed")
            
            file.filename = secrets.token_hex(10) +'.'+extension
            result = await upload_image(file, db=db, bucket_name = product.id)


    return product


@app.get("/product", response_model=schema.ProductOut)
async def get_products(request: Request, business_id: str, 
                search_value: str = None,
                sorting_key: str = None,
                datetime_constraint: datetime.datetime = None,
                page: int = 1,
                size: int = 50,
                reverse_sort: bool = True,
                db: orm.Session = fastapi.Depends(get_db)):

    """
    Intro-This endpoint allows you to retreive all non-deleted products in the database for a particular business. 
    To retreive all products, you need to make a get request to the /product endpoint. 
    
    returnDesc- On sucessful request, it returns:
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

    if not product_list:
        product_list = []

    hostname = request.headers.get('host')

    for product in product_list:
        #fetch images
        images = db.query(file_model.File).filter(file_model.File.bucketname == product.id).all()
        image_path_list = []
        for image in images:
            path = request.url.scheme +"://" + hostname + '/product/'+ product.id + '/'+image.id
            image_path_list.append(path)
        
        product.product_image = image_path_list


    pointers = await paginator.page_urls(page=page_number, size=page_size, count=total_number, endpoint=f"/product")
    response = {"page": page_number, "size": page_size, "total": total_number,"previous_page":pointers['previous'], "next_page": pointers["next"], 
                "items": product_list}
    
    return response


@app.get('/product/{product_id}', response_model=schema.ShowProduct)
def get_product(request: Request, business_id: str, product_id: str, db: orm.Session = fastapi.Depends(get_db)):
    """
    Intro-This endpoint allows you to retreive details of a product in the database belonging to a business. 
    To retreive a product, you need to make a get request to the /products/{product_id} endpoint. 
    
    returnDesc-On sucessful request, it returns:
    returnBody- a product object.
    """
    #fetch product
    product = db.query(model.Product).filter(model.Product.business_id == business_id, model.Product.id == product_id, model.Product.is_deleted==False).first()

    if not product:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product does not exist")

    #fetch images
    hostname = request.headers.get('host')
    images = db.query(file_model.File).filter(file_model.File.bucketname == product.id).all()
    image_path_list = []
    for image in images:
        path = request.url.scheme +"://" + hostname + '/product/'+ product.id + '/'+image.id
        image_path_list.append(path)
    
    product.product_image = image_path_list

    return product


@app.get("/product/{product_id}/{file_id}")
async def get_product_image(product_id: str, file_id: str, 
                                        db: orm.Session = fastapi.Depends(get_db)):
    
    product = model.get_product_by_id(product_id, db=db)
    image = db.query(file_model.File).filter(file_model.File.bucketname == product.id, 
                                              file_model.File.id == file_id).first()

    filename = f"/{image.bucketname}/{image.filename}"

    root_location = os.path.abspath("filestorage")
    full_image_path = root_location + filename

    return FileResponse(full_image_path)


@app.put('/product/{product_id}')
def update_product(product_update: schema.ProductUpdate,
                    product_id: str,
                    user: user_schema.User = fastapi.Depends(is_authenticated), 
                    db: orm.Session = fastapi.Depends(get_db)):
    """
    Intro-This endpoint allows you to update the details of a product. 
    To update a product, you need to make a PUT request to the /products/{product_id} endpoint. 
    You can only update name and description of a product.
    
    returnDesc-On sucessful request, it returns:
    returnBody- a product object.
    """
    
    #check if user is allowed to update products
    if helpers.Helpers.is_organization_member(user_id=user.id, organization_id=product_update.business_id, db=db) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to update a product for this business")

    #fetch products
    product = db.query(model.Product).filter(model.Product.business_id==product_update.business_id, model.Product.id==product_id, model.Product.is_deleted==False).first()

    #check if product exits
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product does not exist')
    
    if product_update.name != None:
        product.name = product_update.name
    if product_update.description != None:
        product.description = product_update.description

    product.updated_at = datetime.datetime.utcnow()

    db.commit()

    return {'message':'Product updated successfully'}


@app.delete("/product/{product_id}")
def delete_product(id: schema.DeleteProduct, product_id: str,
                    user: user_schema.User = fastapi.Depends(is_authenticated), 
                    db: orm.Session = fastapi.Depends(get_db)):
    
    """
    intro-This endpoint allows you to delete a particular product. To delete a product, 
    you need to make a delete request to the /product/{product_id} endpoint.

    paramDesc-On delete request the url takes a query parameter product_id
    param-product_id: This is the id of the product item

    returnDesc-On sucessful request, it returns a message
    returnBody- "successfully deleted"
    """
    
    #check if user is in business and can delete product
    if helpers.Helpers.is_organization_member(user_id=user.id, organization_id=id.business_id, db=db) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to delete a product for this business")

    #check if product exists in db
    product = model.select_product(product_id=product_id, business_id=id.business_id, db=db)
    if product is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product does not exist")
        
    product.is_deleted = True
    db.commit()

    return {"message":"successfully deleted"}


@app.delete("/product/selected/delete", status_code=status.HTTP_200_OK)
def delete_selected_products(req: schema.DeleteSelectedProduct,
                             db: orm.Session = Depends(get_db),
                            user: user_schema.User = fastapi.Depends(is_authenticated)):
    """
    intro-This endpoint allows you to delete selected products. To delete selected products, 
    you need to make a delete request to the /product/selected/delete endpoint.

    paramDesc-On delete request the url takes no parameter

    returnDesc-On sucessful request, it returns a message
    returnBody- "successfully deleted products"
    """

    #check if user is in business and can delete product
    if helpers.Helpers.is_organization_member(user_id=user.id, organization_id=req.business_id, db=db) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to delete a product for this business")

    for product_id in req.product_id_list:
        product = model.get_product_by_id(id=product_id, db=db)

        if product != None and product.business_id == req.business_id:
            product.is_deleted = True
            db.commit()

    return {"message":"Successfully Deleted Products"}


@app.delete("/product/business/all/delete", status_code=status.HTTP_200_OK)
def delete_selected_products(req: schema.DeleteProduct,
                             db: orm.Session = Depends(get_db),
                            user: user_schema.User = fastapi.Depends(is_authenticated)):
    """
    intro-This endpoint allows you to delete all products in a business. To delete all products, 
    you need to make a delete request to the /product/business/all/delete endpoint.

    paramDesc-On delete request the url takes no parameter

    returnDesc-On sucessful request, it returns a message
    returnBody- "successfully deleted all products"
    """

    #check if user is in business and can delete product
    if helpers.Helpers.is_organization_member(user_id=user.id, organization_id=req.business_id, db=db) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to delete a product for this business")

    products = db.query(model.Product).filter(model.Product.business_id==req.business_id, 
                                              model.Product.is_deleted == False).all()

    if products is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products exist in this business")

    for product in products:
        product.is_deleted = True
        db.commit()

    return {"message":"Successfully Deleted All Products"}
       





    

    








    

