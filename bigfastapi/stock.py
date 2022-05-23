import fastapi as fastapi
import sqlalchemy.orm as orm
import datetime as datetime
from uuid import uuid4
from fastapi import APIRouter, Depends
from typing import List, Optional
from fastapi import HTTPException, status
from .auth_api import is_authenticated
from .schemas import users_schemas as user_schema
from .schemas import product_schemas as schema
from .schemas import stock_schemas as stock_schema
from .models import product_models as model
from .models import stock_models as stock_model
from .utils import paginator
from .core import helpers
from bigfastapi.db.database import get_db


app = APIRouter(
    tags=["Stock"]
    )

@app.post('/stock', response_model=stock_schema.ShowStock, status_code=status.HTTP_201_CREATED)
async def create_stock(stock: stock_schema.CreateStock, 
                       user: user_schema.User = fastapi.Depends(is_authenticated),
                       db: orm.Session = fastapi.Depends(get_db)):

    #check if product to create stock for exists
    product = model.get_product_by_id(id=stock.product_id, db=db)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product does not exist")
    
    #check if user is allowed to create a stock for product in the business
    if  helpers.Helpers.is_organization_member(user_id=user.id, organization_id=stock.business_id, db=db) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to create a stock for a product in this business")

    #set status
    if stock.quantity > 0:
        stock_status = True
    else:
        stock_status = False

    #Add stock to database
    stock = stock_model.Stock(id=uuid4().hex, product_id = stock.product_id, 
                                quantity=stock.quantity, price=stock.price, status=stock_status,
                                created_by=user.id, name=stock.name)
    
    db.add(stock)
    db.commit()
    db.refresh(stock)

    return stock


@app.get('/stock/{stock_id}', response_model=stock_schema.ShowStock)
def get_stock(stock_id: str, business_id: str,  db: orm.Session = fastapi.Depends(get_db),
              user: user_schema.User = fastapi.Depends(is_authenticated)):
    
    #check if user is allowed to view stock for a product in the business
    if  helpers.Helpers.is_organization_member(user_id=user.id, organization_id=business_id, db=db) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to view stock for a product in this business")
 
    #fetch stock
    stock = stock_model.fetch_stock_by_id(db=db, stock_id=stock_id)

    if not stock:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock does not exist")

    return stock


@app.get('/stock/product/{product_id}', response_model=List[stock_schema.ShowStock])
def get_stocks(product_id: str, business_id:  str, db: orm.Session = fastapi.Depends(get_db), 
                user: user_schema.User = fastapi.Depends(is_authenticated)):

    #check if user is allowed to view stock for a product in the business
    if  helpers.Helpers.is_organization_member(user_id=user.id, organization_id=business_id, db=db) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to view stock for a product in this business")
 
    #fetch stocks
    stocks = db.query(stock_model.Stock).filter(stock_model.Stock.product_id == product_id, 
                                               stock_model.Stock.is_deleted==False).all()

    if not stocks:
        return []

    return stocks


@app.get('/stock/{business_id}', response_model=List[stock_schema.ShowStock])
def get_all_stocks(business_id: str, db: orm.Session = fastapi.Depends(get_db), 
                    user: user_schema.User = fastapi.Depends(is_authenticated)):

    #check if user is allowed to view stock for a product in the business
    if  helpers.Helpers.is_organization_member(user_id=user.id, organization_id=business_id, db=db) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to view stock for a product in this business")
 
    #fetch stocks
    stocks = stock_model.fetch_all_stocks_in_business(db=db, business_id=business_id)

    if not stocks:
        return []

    return stocks



@app.put('/stock/{stock_id}')
def update_stock(stock_update: stock_schema.StockUpdate, 
                    stock_id: str,
                    user: user_schema.User = fastapi.Depends(is_authenticated), 
                    db: orm.Session = fastapi.Depends(get_db)):

    #check if user is allowed to update stock
    if helpers.Helpers.is_organization_member(user_id=user.id, organization_id=stock_update.business_id, db=db) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to update a stock for this business")

    #fetch stock
    stock = stock_model.fetch_stock_by_id(db=db, stock_id=stock_id)
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Stock does not exist')

    if stock_update.name != None:
        stock.name = stock_update.name
    if stock_update.quantity != None:
        stock.quantity = stock_update.quantity
    if stock_update.status != None:
        stock.status = stock_update.status
    if stock_update.price != None:
        if stock.price != stock_update.price:
            price_update = stock_model.StockPriceHistory(id=uuid4().hex, 
                                                         price=stock.price, created_by=user.id, 
                                                         stock_id=stock.id)
            db.add(price_update)
            db.commit()
            stock.price = stock_update.price

    stock.updated_at = datetime.datetime.utcnow()
    db.commit()

    return {'message':'Stock updated successfully'}



@app.delete("/stock/{stock_id}")
def delete_product(stock_id: str,  
                    stock: stock_schema.DeleteStock,
                    user: user_schema.User = fastapi.Depends(is_authenticated), 
                    db: orm.Session = fastapi.Depends(get_db)):
    
    """
    intro-This endpoint allows you to delete a particular stock. To delete a stock, 
    you need to make a delete request to the /stock/{stock_id} endpoint.

    paramDesc-On delete request the url takes a path parameter stock_id
    param-stock_id: This is the unique id of the stock

    returnDesc-On sucessful request, it returns an Object with message
       returnBody- "Successfully deleted"
    """
    #check if user is in business and can delete product
    if helpers.Helpers.is_organization_member(user_id=user.id, organization_id=stock.business_id, db=db) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to delete a stock for this business")

    #fetch stock
    stock = stock_model.fetch_stock_by_id(db=db, stock_id=stock_id)
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Stock does not exist')

    stock.is_deleted = True
    db.commit()

    return {"message":"Successfully deleted"}