
import fastapi
import sqlalchemy.orm as _orm
from fastapi import APIRouter, HTTPException
from bigfastapi.db.database import get_db
from bigfastapi.services import menu_service
from bigfastapi.schemas.menu_schemas import MenuRequest
from .auth_api import is_authenticated
from .schemas import users_schemas


app = APIRouter(tags=["Menu"])


# ENDPOINT to add menu item to sidebar items
@app.put('/menu/add-item')
def add_menu_tem(payload: MenuRequest, db: _orm.Session = fastapi.Depends(get_db),
                 user: users_schemas.User = fastapi.Depends(is_authenticated)):

    # Check user super-user status
    if not user.is_superuser:
        raise HTTPException(
            status_code=401, detail="You lack the necessary permission")
    #  Run Menu-more modifications
    modify_result = menu_service.modify_menu_more_list(
        payload.menu_item, True, db)

    return {"status": True, "data": modify_result}


# ENDPOINT to remove menu item from sidebar items
@app.put('/menu/remove-item')
def remove_menu_item(payload: MenuRequest, db: _orm.Session = fastapi.Depends(get_db),
                     user: users_schemas.User = fastapi.Depends(is_authenticated)):
    # Check user super-user status
    if not user.is_superuser:
        raise HTTPException(
            status_code=401, detail="You lack the necessary permission")
    #  Run Menu-more modifications
    modify_result = menu_service.modify_menu_more_list(
        payload.menu_item, False, db)

    return {"status": True, "data": modify_result}


# @app.put('/menu/populate')
# def runpopuate(key_word: str = '', db: _orm.Session = fastapi.Depends(get_db)):
#     if key_word != "1802":
#         raise HTTPException(status_code=401, detail="Permission Denied")
#     result = menu_service.popo(db)
#     return result
