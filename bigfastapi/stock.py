import fastapi as fastapi
import sqlalchemy.orm as orm
import datetime as datetime
from uuid import uuid4
from fastapi import APIRouter, Depends, Query
from typing import List
from fastapi import HTTPException, status
from .auth_api import is_authenticated
from .schemas import users_schemas as user_schema
from .schemas import stock_schemas as stock_schema
from .models import product_models as model
from .models import stock_models as stock_model
from .core import helpers
from bigfastapi.db.database import get_db


app = APIRouter(
    tags=["Stock"]
    )

@app.post('/stock', response_model=stock_schema.ShowStock, status_code=status.HTTP_201_CREATED)
async def create_stock(stock: stock_schema.CreateStock, 
                       user: user_schema.User = fastapi.Depends(is_authenticated),
                       db: orm.Session = fastapi.Depends(get_db)):
    """
    Intro - This endpoint allows you to create a create a new stock item.
    It takes in four parameters. To create a stock, you 
    need to make a post request to the /stock endpoint

    paramDesc-
        reqBody-name: This is the name of the stock to be created. 
        reqBody-product_id: This is the id for which the stock is being created. 
        reqBody-price: This is the buying price of the stock. 
        reqBody-quantity: Quantity of product available on that stock.

    returnDesc-On sucessful request, it returns

        returnBody- the stock object.
    """

    #check if product to create stock for exists
    product = model.fetch_product_by_id(id=stock.product_id, db=db)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product does not exist")
    
    #check if user is allowed to create a stock for product in the business
    user_status = await helpers.Helpers.is_organization_member(user_id=user.id, organization_id=stock.organization_id, db=db)
    if user_status==False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to create a stock for a product in this business")

    created_stock = stock_model.create_stock(db=db, name=stock.name, product_id=stock.product_id, quantity=stock.quantity, 
                        price= stock.price, user_id=user.id)

    if created_stock:
        return created_stock


@app.get('/stock/{stock_id}', response_model=stock_schema.ShowStock)
async def get_stock(stock_id: str, organization_id: str,  db: orm.Session = fastapi.Depends(get_db),
              user: user_schema.User = fastapi.Depends(is_authenticated)):
    
    """
    Intro-This endpoint allows you to retreive details of a stock in the database for a particular product. 
    To retreive the stock details, you need to make a get request to the /stock/{stock_id} endpoint. 
    
    paramDesc-On get request the url takes a path parameter stock_id
    returnDesc- On sucessful request, it returns:
    returnBody- the stock object.
    """

    #check if user is allowed to view stock for a product in the business
    user_status = await helpers.Helpers.is_organization_member(user_id=user.id, organization_id=organization_id, db=db)
    if user_status == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to view stock for a product in this business")
 
    #fetch stock
    stock = stock_model.fetch_stock_by_id(db=db, stock_id=stock_id)

    if not stock:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock does not exist")

    return stock


@app.get('/stock/product/{product_id}', response_model=List[stock_schema.ShowStock])
async def get_stocks(product_id: str, organization_id:  str, db: orm.Session = fastapi.Depends(get_db), 
                user: user_schema.User = fastapi.Depends(is_authenticated)):

    """
    Intro-This endpoint allows you to retreive all non-deleted stock in the database for a particular product in a business. 
    To retreive all stock for a product, you need to make a get request to the /stock/product/{product_id} endpoint. 
    
    paramDesc-On get request the url takes a path parameter product_id
    returnDesc- On sucessful request, it returns:
    returnBody- a list of an array of stock objects.
    """


    #check if user is allowed to view stock for a product in the business
    user_status = await helpers.Helpers.is_organization_member(user_id=user.id, organization_id=organization_id, db=db)
    if user_status == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to view stock for a product in this business")
 
    #fetch stocks
    stocks = db.query(stock_model.Stock).filter(stock_model.Stock.product_id == product_id, 
                                               stock_model.Stock.is_deleted==False).all()

    if not stocks:
        return []

    return stocks


@app.get('/stock/{organization_id}', response_model=List[stock_schema.ShowStock])
async def get_all_stocks(organization_id: str, db: orm.Session = fastapi.Depends(get_db), 
                    user: user_schema.User = fastapi.Depends(is_authenticated)):

    """
    Intro-This endpoint allows you to retreive all non-deleted stock in the database for a particular business. 
    To retreive all stock for a business, you need to make a get request to the /stock/{organization_id} endpoint. 
    
    paramDesc-On get request the url takes a path parameter organization_id
    returnDesc- On sucessful request, it returns:
    returnBody- a list of an array of stock objects.
    """

    #check if user is allowed to view stock for a product in the business
    user_status = await helpers.Helpers.is_organization_member(user_id=user.id, organization_id=organization_id, db=db)
    if user_status == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to view stock for a product in this business")
 
    #fetch stocks
    stocks = stock_model.fetch_all_stocks_in_business(db=db, organization_id=organization_id)

    if not stocks:
        return []

    return stocks



@app.put('/stock/{stock_id}')
async def update_stock(stock_update: stock_schema.StockUpdate, 
                    stock_id: str,
                    user: user_schema.User = fastapi.Depends(is_authenticated), 
                    db: orm.Session = fastapi.Depends(get_db)):
    """
    Intro-This endpoint allows you to update the details of a stock in the database for a particular product. 
    To retreive the stock details, you need to make a put request to the /stock/{stock_id} endpoint. 
    
    paramDesc-
        reqBody-name: This is the name of the stock to be updated. Optional
        reqBody-price: This is the price of the stock to be updated. Optional
        reqBody-quantity: This is the quantity of stock to be updated. Optional

    returnDesc- On sucessful request, it returns:
    returnBody- the stock object.
    """

    #check if user is allowed to update stock
    user_status =  await helpers.Helpers.is_organization_member(user_id=user.id, organization_id=stock_update.organization_id, db=db)
    if user_status == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to update a stock for this business")

    #fetch stock
    stock = stock_model.fetch_stock_by_id(db=db, stock_id=stock_id)
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Stock does not exist')

    if stock_update.quantity != None:
        stock.quantity = stock_update.quantity
    if stock_update.status != None:
        stock.status = stock_update.status
    if stock_update.price != None:
        stock.price = stock_update.price
    if stock_update.name != None:
        stock.name = stock_update.name

    stock.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(stock)

    return {'message':'Stock updated successfully', 'data': stock }



@app.delete("/stock/{stock_id}")
async def delete_stock(
    stock_id: str,  
    id: stock_schema.DeleteStock,
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
    #check if user is in business and can delete stock
    user_status = await helpers.Helpers.is_organization_member(user_id=user.id, organization_id=id.organization_id, db=db)
    if user_status == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to delete a stock for this business")

    #fetch stock
    stock = stock_model.fetch_stock_by_id(db=db, stock_id=stock_id)
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Stock does not exist')

    stock.is_deleted = True
    db.commit()

    return {"message":"Successfully deleted"}


@app.delete("/stock/selected/delete", status_code=status.HTTP_200_OK)
async def delete_selected_stock(req: stock_schema.DeleteSelectedStock,
                             db: orm.Session = Depends(get_db),
                            user: user_schema.User = fastapi.Depends(is_authenticated)):
    """
    intro-This endpoint allows you to delete selected products. To delete selected products, 
    you need to make a delete request to the /product/selected/delete endpoint.

    paramDesc-On delete request the url takes no parameter

    returnDesc-On sucessful request, it returns a message
    returnBody- "successfully deleted products"
    """

    #check if user is in business and can delete stock
    user_status =  await helpers.Helpers.is_organization_member(user_id=user.id, organization_id=req.organization_id, db=db)
    if user_status == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to delete a stock for this business")

    for stock_id in req.stock_id_list:
        stock = stock_model.fetch_stock_by_id(stock_id=stock_id, db=db)

        if stock != None:
            stock.is_deleted = True
            db.commit()

    return {"message":"Successfully Deleted Products"}


@app.delete("/stock/{product_id}/all/delete", status_code=status.HTTP_200_OK)
def delete_selected_products(req: stock_schema.DeleteStock, product_id: str,
                             db: orm.Session = Depends(get_db),
                            user: user_schema.User = fastapi.Depends(is_authenticated)):

    #check if user is in business and can delete stock
    user_status = helpers.Helpers.is_organization_member(user_id=user.id, organization_id=req.organization_id, db=db)
    if user_status == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to delete a stock for a product in this business")

    stocks = db.query(stock_model.Stock).filter(stock_model.Stock.product_id==product_id, 
                                              stock_model.Stock.is_deleted == False).all()

    if stocks is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No stocks exist for this product")

    for stock in stocks:
        stock.is_deleted = True
        db.commit()

    return {"message":"Successfully Deleted All Stocks for this Product"}