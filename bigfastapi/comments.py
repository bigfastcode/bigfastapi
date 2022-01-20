from fastapi import APIRouter, Request
from typing import List, Any
import fastapi as _fastapi
from fastapi.param_functions import Depends
import fastapi.security as _security
import sqlalchemy.orm as _orm
from . import services as _services, schema as _schemas
from bigfastapi.db.database import get_db

from pyexpat import model
import fastapi as _fastapi
from fastapi import Request
from fastapi.openapi.models import HTTPBearer
import fastapi.security as _security
import jwt as _jwt
import datetime as _dt
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from bigfastapi.utils import settings as settings
from bigfastapi.db import database as _database
from . import models as _models, schema as _schemas
from .token import *
from .auth import *
from .mail import *



from fastapi.security import HTTPBearer
bearerSchema = HTTPBearer()
import re

JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 60 * 5


app = APIRouter(tags=["Comments"])


@app.get("/comments/{model_name}")
async def get_all_comments_related_to_model(
    model_name: str, db_Session: _orm.Session = Depends(get_db)
):
    qs = await _services.db_retrieve_all_model_comments(
        model_name=model_name, db=db_Session
    )
    return {"status": True, "data": qs}


@app.get("/comments/{model_name}/{object_id}")
async def get_all_comments_for_object(
    model_name: str, object_id: str, db_Session=Depends(get_db)
):
    qs = await _services.db_retrieve_all_comments_for_object(
        object_id=object_id, model_name=model_name, db=db_Session
    )
    return {"status": True, "data": qs}


@app.post("/comments/{model_name}/{comment_id}/reply")
async def reply_to_comment(
    model_name: str,
    comment_id: int,
    comment: _schemas.CommentCreate,
    db_Session=Depends(get_db),
):
    obj = await _services.db_reply_to_comment(
        comment_id=comment_id, comment=comment, model_name=model_name, db=db_Session
    )
    return {"status": True, "data": obj}


@app.post("/comments/{model_name}/{object_id}")
def create_new_comment_for_object(
    model_name: str,
    object_id: int,
    comment: _schemas.CommentCreate,
    db_Session=Depends(get_db),
):
    obj = _services.db_create_comment_for_object(
        object_id=object_id, comment=comment, model_name=model_name, db=db_Session
    )
    return {"status": True, "data": obj}


@app.put("/comments/{model_name}/{comment_id}/update")
async def update_comment_by_id(
    model_name: str,
    comment_id: int,
    comment: _schemas.CommentUpdate,
    db_Session=Depends(get_db),
):
    obj = _services.db_update_comment(
        object_id=comment_id, model_name=model_name, comment=comment, db=db_Session
    )
    return {"status": True, "data": obj}


@app.delete("/comments/{model_name}/{comment_id}/delete")
async def delete_comment_by_id(
    model_name: str, comment_id:int, db_Session=Depends(get_db)
):
    obj = await _services.db_delete_comment(
        object_id=comment_id, model_name=model_name, db=db_Session
    )
    return {"status": True, "data": obj}


@app.post("/comments/{model_name}/{comment_id}/vote")
async def vote_on_comment(
    model_name: str, comment_id:int, action: str, db_Session=Depends(get_db)
):
    if action not in ["upvote", "downvote"]:
        return {
            "status": False,
            "message": {
                f"{action} not supported. Consider using 'upvote' or 'downvote'."
            },
        }
    response = await _services.db_vote_for_comments(
        comment_id=comment_id, model_name=model_name, action=action, db=db_Session
    )
    error_message = "Vote Failed"
    if response:
        return {"status": True, "data": response}
    return {"status": False, "message": error_message}



#=================================== COMMENT SERVICES =================================#

async def db_vote_for_comments(comment_id: int, model_name:str, action: str, db: _orm.Session):
    """[summary]

    Args:
        comment_id (int): [description]
        model (Base): [description]
        action (str): "upvote" | "downvote"
        db (_orm.Session): [description]
    """ 
    comment_obj = await db_retrieve_comment_by_id(comment_id, model_name, db=db)
    if action == "upvote": comment_obj.upvote(),
    elif action == "downvote": comment_obj.downvote()
    db.commit()
    db.refresh(comment_obj)
    return comment_obj

async def db_retrieve_comment_by_id(object_id: int, model_name:str, db: _orm.Session):
    object = db.query(_models.Comment).filter(_models.Comment.id == object_id).first()
    if object:
        return object # SQLAlchecmy ORM Object 
    else: 
        return "DoesNotExist"

async def db_retrieve_all_comments_for_object(object_id: int, model_name:str, db: _orm.Session):
    object_qs = db.query(_models.Comment).filter(_models.Comment.rel_id == object_id, 
        _models.Comment.model_type == model_name, _models.Comment.p_id == None).all()
    
    object_qs = list(map(_schemas.Comment.from_orm, object_qs))
    return object_qs

async def db_retrieve_all_model_comments(model_name:str, db: _orm.Session):
    object_qs = db.query(_models.Comment).filter(_models.Comment.model_type == model_name, _models.Comment.p_id == None).all()
    object_qs = list(map(_schemas.Comment.from_orm, object_qs))
    return object_qs

async def db_reply_to_comment(model_name:str, comment_id:int, comment: _schemas.Comment, db: _orm.Session):
    p_comment = db.query(_models.Comment).filter(_models.Comment.model_type == model_name, 
        _models.Comment.id == comment_id).first()
    if p_comment:
        reply = _models.Comment(model_name=model_name, rel_id=p_comment.rel_id, email=comment.email, name=comment.name, text=comment.text, p_id=p_comment.id)
        db.add(reply)
        db.commit()
        db.refresh(reply)
        return reply
    return None

async def db_delete_comment(object_id: int, model_name:str, db: _orm.Session):
    object = await db_retrieve_comment_by_id(object_id=object_id, model_name=model_name, db=db)
    db.delete(object)
    db.commit()
    return _schemas.Comment.from_orm(object)
    
async def db_create_comment_for_object(object_id: str, comment: _schemas.CommentCreate, db: _orm.Session, model_name:str = None):
    obj = _models.Comment(rel_id=object_id, model_name=model_name, text=comment.text, name=comment.name, email=comment.email)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _schemas.Comment.from_orm(obj)

async def db_update_comment(object_id:int, comment: _schemas.CommentUpdate, db: _orm.Session, model_name:str = None):
    object_db = await db_retrieve_comment_by_id(object_id=object_id, model_name=model_name, db=db)
    object_db.text = comment.text
    object_db.name = comment.name
    object_db.email = comment.email
    db.commit()
    db.refresh(object_db)
    return _schemas.Comment.from_orm(object_db)
    
