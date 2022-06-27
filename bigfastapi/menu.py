import datetime as _dt
import json
from uuid import uuid4

import fastapi
import sqlalchemy.orm as _orm
from fastapi import APIRouter, HTTPException
from bigfastapi.db.database import get_db
from bigfastapi.models import menu_models
from bigfastapi.services.menu_service import get_default_menu_object
from .auth_api import is_authenticated
from .core.helpers import Helpers
from .schemas import users_schemas

import pkg_resources


app = APIRouter(tags=["Menu"])

DATA_PATH = pkg_resources.resource_filename('bigfastapi', 'data/menu.json')


@app.put('/menu/add-item')
def addMenuItem(newFeature: str = '', db: _orm.Session = fastapi.Depends(get_db),
                user: users_schemas.User = fastapi.Depends(is_authenticated)):

    menuObject = get_default_menu_object()

    # fie = open(DATA_PATH, 'r')
    # t = fie.read()
    # me = json.loads(t)
    # fie.close()
    return menuObject

    if user.is_superuser:
        updateResult = menu_models.addFeature(db)
        return updateResult
    else:
        raise HTTPException(
            status_code=401, detail="You lack the necessary permission")
