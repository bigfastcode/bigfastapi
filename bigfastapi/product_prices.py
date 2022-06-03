import fastapi as fastapi
import datetime as datetime
import sqlalchemy.orm as orm
from uuid import uuid4
from fastapi import APIRouter, Depends
from typing import List, Optional
from fastapi import HTTPException, status
from .auth_api import is_authenticated
from .schemas import users_schemas as user_schema
from .schemas import product_price_schemas as schema
from .models import product_price_models as model
from .models import product_models as product_model
from .models.organisation_models import Organization
from .utils import paginator
from .core import helpers
from bigfastapi.db.database import get_db

app = APIRouter(
    tags=["Product Prices"]
    )

@app.post("/prices", response_model=schema.ProductPrice, status_code=status.HTTP_201_CREATED)
async def create_product_price(price: schema.CreateProductPrice, 
                   user: user_schema.User = fastapi.Depends(is_authenticated), 
                   db: orm.Session = fastapi.Depends(get_db)):
    
    #check if user is allowed to create a price for product in the business
    user_status = await helpers.Helpers.is_organization_member(user_id=user.id, organization_id=price.organization_id, db=db)
    if user_status == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to create pricing for a product in this business")

    #check if product exists      
    product = product_model.fetch_product_by_id(db=db, id=price.product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product does not exist")
    
    #apply
    if price.apply_on == 'weekend':
        monday = False
        tuesday = False
        wednesday = False
        thursday = False
        friday =  False
        saturday = True
        sunday = True
    elif price.apply_on == 'all':
        monday = True
        tuesday = True
        wednesday = True
        thursday = True
        friday =  True
        saturday = True
        sunday = True

    #Add product price to db
    created_price = model.ProductPrice(id=uuid4().hex,product_id=price.product_id,stock_id=price.stock_id,
                               price=price.price,start=price.start,end=price.end,
                               monday=monday, tuesday=tuesday, wednesday=wednesday, thursday=thursday,
                               friday=friday, saturday=saturday, sunday=sunday,
                               customer_group=price.customer_group,
                               currency=price.currency,created_by=user.id)

    db.add(created_price)
    db.commit()
    db.refresh(created_price)


    return created_price


@app.get('/prices/product/{product_id}', response_model=List[schema.ProductPrice])
async def get_product_prices(organization_id: str, product_id: str, db: orm.Session = fastapi.Depends(get_db),
                            user: user_schema.User = fastapi.Depends(is_authenticated)):

    #check if user is allowed to view prices for product in the business
    user_status = await helpers.Helpers.is_organization_member(user_id=user.id, organization_id=organization_id, db=db)
    if user_status == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to view pricing for a product in this business")
    
    #fetch product prices
    productprices = model.fetch_product_prices(db=db, product_id=product_id)

    if not productprices:
        return []
    
    for price in productprices:
        if price.monday == False:
            price.apply_on = 'weekend'
        else:
            price.apply_on = 'all'

    return productprices


@app.get('/prices/{price_id}', response_model=schema.ProductPrice)
async def get_product_price(organization_id: str, product_id: str, db: orm.Session = fastapi.Depends(get_db),
                            user: user_schema.User = fastapi.Depends(is_authenticated)):

    #check if user is allowed to view prices for product in the business
    user_status = await helpers.Helpers.is_organization_member(user_id=user.id, organization_id=organization_id, db=db)
    if user_status == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to view pricing for a product in this business")

    #fetch product price
    productprice = model.fetch_product_price_by_id(db=db, product_id=product_id)

    if not productprice:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product Price does not exist")
    
    if productprice.monday == False:
        productprice.apply_on = 'weekend'
    else:
        productprice.apply_on = 'all'

    return productprice 


@app.put('/prices/{price_id}')
async def update_product_price(price_update: schema.ProductPriceUpdate,
                    price_id: str,
                    user: user_schema.User = fastapi.Depends(is_authenticated), 
                    db: orm.Session = fastapi.Depends(get_db)):
    
    #check if user is allowed to update price in business
    user_status = await helpers.Helpers.is_organization_member(user_id=user.id, organization_id=price_update.organization_id, db=db)
    if user_status ==False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to update prices for a product for this business")

    #fetch price
    price = model.fetch_product_price_by_id(db=db, price_id=price_id)

    #check if product price exits
    if not price:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product Price does not exist')
    
    if price_update.price != None:
        price.price = price_update.price
    if price_update.currency != None:
        price.currency = price_update.currency
    if price_update.start != None:
        price.start = price_update.start
    if price_update.end != None:
        price.end = price_update.end
    if price_update.apply_on != None:
        if price_update.apply_on == 'weekend':
            price.monday = False
            price.tuesday = False
            price.wednesday = False
            price.thursday = False
            price.friday =  False
            price.saturday = True
            price.sunday = True
        elif price_update.apply_on == 'all':
            price.monday = True
            price.tuesday = True
            price.wednesday = True
            price.thursday = True
            price.friday =  True
            price.saturday = True
            price.sunday = True

    price.last_updated = datetime.datetime.utcnow()

    db.commit()

    return {'message':'Product Price updated successfully'}



@app.delete("/prices/{price_id}")
async def delete_product_price(id: schema.DeleteProductPrice,price_id: str,
                    user: user_schema.User = fastapi.Depends(is_authenticated), 
                    db: orm.Session = fastapi.Depends(get_db)):
    
    #check if user is in business and can delete product price
    user_status = await helpers.Helpers.is_organization_member(user_id=user.id, organization_id=id.organization_id, db=db) 
    if user_status == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to delete a product price for this business")

    #check if product price exists in db
    product_price = model.fetch_product_price_by_id(price_id=price_id, db=db)
    if product_price is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product Price does not exist")
        
    product_price.is_deleted = True
    db.commit()

    return {"message":"successfully deleted"}