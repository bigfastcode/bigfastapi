import datetime as _dt
from uuid import uuid4

import fastapi
import sqlalchemy.orm as _orm
from fastapi import APIRouter, HTTPException

from fastapi_pagination import Page, paginate, add_pagination
from sqlalchemy import desc

from bigfastapi.db.database import get_db
from bigfastapi.models import menu_model
from bigfastapi.models.menu_model import addFeature
from .auth_api import is_authenticated
from .core.helpers import Helpers
from .schemas import users_schemas


app = APIRouter(tags=["Menu"])


@app.put('/menu/add-item')
def addMenuItem(newFeature: str = '',
                db: _orm.Session = fastapi.Depends(get_db),
                user: users_schemas.User = fastapi.Depends(is_authenticated)):

    updateResult = menu_model.addFeature(db)
    return updateResult


add_pagination(app)
