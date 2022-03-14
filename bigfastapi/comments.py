from fastapi import APIRouter, Request
from typing import List, Any
import fastapi as _fastapi
from fastapi.param_functions import Depends
import fastapi.security as _security
import sqlalchemy.orm as _orm
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
from bigfastapi.db import database
from .schemas import comments_schemas
from .models import comments_models
from .auth_api import *



from fastapi.security import HTTPBearer
bearerSchema = HTTPBearer()

JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 60 * 5


app = APIRouter(tags=["Comments"])


@app.get("/comments/{model_name}")
def get_all_comments_related_to_model(
    model_name: str, db_Session: _orm.Session = Depends(get_db)
):
    qs = db_retrieve_all_model_comments(
        model_name=model_name, db=db_Session
    )
    return {"status": True, "data": qs}


@app.get("/comments/{model_name}/{object_id}")
def get_all_comments_for_object(
    model_name: str, object_id: str, db_Session=Depends(get_db)
):
    qs = db_retrieve_all_comments_for_object(
        object_id=object_id, model_name=model_name, db=db_Session
    )
    return {"status": True, "data": qs}


@app.post("/comments/{model_name}/{comment_id}/reply")
def reply_to_comment(
    model_name: str,
    comment_id: int,
    comment: comments_schemas.CommentCreate,
    db_Session=Depends(get_db),
):
    obj = db_reply_to_comment(
        comment_id=comment_id, comment=comment, model_name=model_name, db=db_Session
    )
    return {"status": True, "data": obj}


@app.post("/comments/{model_name}/{object_id}")
def create_new_comment_for_object(
    model_name: str,
    object_id: str,
    comment: comments_schemas.CommentBase,
    db_Session=Depends(get_db),
):
    obj = db_create_comment_for_object(
        object_id=object_id, comment=comment, model_name=model_name, db=db_Session
    )
    return {"status": True, "data": obj}


@app.put("/comments/{model_name}/{comment_id}/update")
def update_comment_by_id(
    model_name: str,
    comment_id: int,
    comment: comments_schemas.CommentUpdate,
    db_Session=Depends(get_db),
):
    obj = db_update_comment(
        object_id=comment_id, model_name=model_name, comment=comment, db=db_Session
    )
    return {"status": True, "data": obj}


@app.delete("/comments/{model_name}/{comment_id}/delete")
def delete_comment_by_id(
    model_name: str, comment_id:int, db_Session=Depends(get_db)
):
    obj = db_delete_comment(
        object_id=comment_id, model_name=model_name, db=db_Session
    )
    return {"status": True, "data": obj}


@app.post("/comments/{model_name}/{comment_id}/vote")
def vote_on_comment(
    model_name: str, comment_id:int, action: str, db_Session=Depends(get_db)
):
    if action not in ["upvote", "downvote"]:
        return {
            "status": False,
            "message": {
                f"{action} not supported. Consider using 'upvote' or 'downvote'."
            },
        }
    response = db_vote_for_comments(
        comment_id=comment_id, model_name=model_name, action=action, db=db_Session
    )
    error_message = "Vote Failed"
    if response:
        return {"status": True, "data": response}
    return {"status": False, "message": error_message}



#=================================== COMMENT SERVICES =================================#

def db_vote_for_comments(comment_id: int, model_name:str, action: str, db: _orm.Session):
    """Perform an upvote or downvote on a comment

    Args:
        comment_id (int): ID of the comment to vote for
        model_name (str): Model Type of the comment
        action (str): "upvote" | "downvote"
        db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI
    
    Returns:
        schema.Comment : A refreshed Comment object reflecting the changed votes
    """ 
    comment_obj = db_retrieve_comment_by_id(comment_id, model_name, db=db)
    if action == "upvote": comment_obj.upvote(),
    elif action == "downvote": comment_obj.downvote()
    db.commit()
    db.refresh(comment_obj)
    return comment_obj

def db_retrieve_comment_by_id(object_id: int, model_name:str, db: _orm.Session):
    """Retrieves a Comment by ID

    Args:
        object_id (int): ID of target Comment
        model_name (str): model type of comment
        db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI

    Returns:
        sqlalchemy Model Object: ORM Comment Object with ID = object_id
    """
    object = db.query(comments_models.Comment).filter(comments_models.Comment.id == object_id).first()
    if object:
        return object # SQLAlchecmy ORM Object 
    else: 
        return "DoesNotExist"

def db_retrieve_all_comments_for_object(object_id: int, model_name:str, db: _orm.Session):
    """Retrieve all Comments related to a specific object

    Args:
        object_id (int): ID of the object that maps to rel_id of the Comment
        model_name (str): Model Type of the object
        db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI

    Returns:
        List[schema. Comment]: A list of all comments and their threads, for a specific object
    """
    object_qs = db.query(comments_models.Comment).filter(comments_models.Comment.rel_id == object_id, 
        comments_models.Comment.model_type == model_name, comments_models.Comment.p_id == None).all()
    
    object_qs = list(map(comments_schemas.Comment.from_orm, object_qs))
    return object_qs

def db_retrieve_all_model_comments(model_name:str, db: _orm.Session):
    """Retrieve all comments of model type

    Args:
        model_name (str): Model Type
        db (_orm.Session): [description]

    Returns:
        List[Comment]: QuerySet of all Comments where model_type == model_name
    """
    object_qs = db.query(comments_models.Comment).filter(comments_models.Comment.model_type == model_name, comments_models.Comment.p_id == None).all()
    object_qs = list(map(comments_schemas.Comment.from_orm, object_qs))
    return object_qs

def db_reply_to_comment(model_name:str, comment_id:int, comment: comments_schemas.Comment, db: _orm.Session):
    """Reply to a comment 

    Args:
        model_name (str): Model Type of new Comment
        comment_id (int): ID of Comment to reply to 
        comment (comments_schemas.Comment): new Comment data
        db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI

    Returns:
        comments_schemas.Comment: The newly created Comment
    """
    p_comment = db.query(comments_models.Comment).filter(comments_models.Comment.model_type == model_name, 
        comments_models.Comment.id == comment_id).first()
    if p_comment:
        reply = comments_models.Comment(model_name=model_name, rel_id=p_comment.rel_id, email=comment.email, 
                name=comment.name, text=comment.text, p_id=p_comment.id, commenter_id=comment.commenter_id)
        db.add(reply)
        db.commit()
        db.refresh(reply)
        return reply
    return None

def db_delete_comment(object_id: int, model_name:str, db: _orm.Session):
    """Delete a Comment

    Args:
        object_id (int): ID of Comment to delete
        model_name (str): model type of comment to delete
        db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI

    Returns:
        Comment: Deleted Comment data
    """
    object = db_retrieve_comment_by_id(object_id=object_id, model_name=model_name, db=db)
    db.delete(object)
    db.commit()
    return comments_schemas.Comment.from_orm(object)
    
def db_create_comment_for_object(object_id: str, comment: comments_schemas.CommentBase, db: _orm.Session, model_name:str):
    """Create a top-level Comment for an object

    Args:
        object_id (str): ID of Object to create comment for. Maps to rel_id of comment
        comment (comments_schemas.CommentCreate): new Comment data
        db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI
        model_name (str): Model Type of the Comment to create.

    Returns:
        Comment: Data of the newly Created Comment
    """
    obj = comments_models.Comment(id=uuid4().hex, rel_id=object_id, model_name=model_name, text=comment.text, 
                    name=comment.name, email=comment.email, commenter_id=comment.commenter_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    print(obj)
    return comments_schemas.Comment.from_orm(obj)

def db_update_comment(object_id:int, comment: comments_schemas.CommentUpdate, db: _orm.Session, model_name:str):
    """Edit a Comment Object

    Args:
        object_id (int): ID of Comment to edit
        comment (comments_schemas.CommentUpdate): New Comment data
        db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI
        model_name (str): Model Type of the Comment to edit

    Returns:
        Comment: Refreshed Comment data for Updated Comment
    """
    object_db = db_retrieve_comment_by_id(object_id=object_id, model_name=model_name, db=db)
    object_db.text = comment.text
    object_db.name = comment.name
    object_db.email = comment.email
    db.commit()
    db.refresh(object_db)
    return comments_schemas.Comment.from_orm(object_db)
    
