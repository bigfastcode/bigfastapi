from fastapi import APIRouter, Request, BackgroundTasks
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
from bigfastapi.activity_log import createActivityLog
from .schemas import comments_schemas
from .models import comments_models, user_models
from .services.auth_service import *

from bigfastapi.schemas import users_schemas
from bigfastapi.services.auth_service import is_authenticated
from bigfastapi.utils import paginator

from bigfastapi.services.notification_services import (
    get_mentions,
    create_comment_notification_format,
    create_notification
)


from fastapi.security import HTTPBearer
bearerSchema = HTTPBearer()

JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 60 * 5

app = APIRouter(tags=["Comments"])


@app.get("/comments/{model_type}")
def get_all_comments_related_to_model(
    model_type: str, db_Session: _orm.Session = Depends(get_db)
):

    """intro-->This endpoint allows you to retrieve all comments of the same model type. To use this endpoint you need to make a get request to the /comments/{model_type} endpoint 
            paramDesc-->On get request the url takes the parameter, model_type
                param-->model_type: This is the model type of the comment

    returnDesc--> On sucessful request, it returns 
        returnBody--> an array of comments
    """
    qs = db_retrieve_all_model_comments(
        model_type=model_type, db=db_Session
    )
    return {"status": True, "data": qs}


@app.get("/comments/{model_type}/{object_id}")
async def get_all_comments_for_object(
    model_type: str, 
    object_id: str, 
    page: int = 1,
    size: int = 10,
    db_Session=Depends(get_db)
):
    """intro-->This endpoint allows you to retrieve all comments related to a specific object. To use this endpoint you need to make a get request to the /comments/{model_type}/{object_id} endpoint 
            paramDesc-->On get request the url takes two parameters, model_type & object_id
                param-->model_type: This is the model type of the comment
                param-->object_id: This is the id of the object that contains the comment

    returnDesc--> On sucessful request, it returns 
        returnBody--> an array of comments and their threads for a specified object
    """

    # set pagination parameter
    page_size = 10 if size < 1 or size > 10 else size
    page_number = 1 if page <= 0 else page
    offset = await paginator.off_set(page=page_number, size=page_size)

    qs = db_retrieve_all_comments_for_object(
        object_id=object_id, model_type=model_type, db=db_Session
    )
    
    comments = qs.offset(offset=offset).limit(limit=page_size).all()
    
    total_items = qs.count()

    pointers = await paginator.page_urls(
            page=page_number, size=page_size, count=total_items, endpoint=f"/comments/{model_type}/{object_id}"
    )

    response = {
            "page": page,
            "size": page_size,
            "total": total_items,
            "previous_page": pointers["previous"],
            "next_page": pointers["next"],
            "items": comments,
    }    
    # return {"status": True, "data": qs}
    return response


@app.get("/comments/{model_type}/comment/{comment_id}")
def get_specific_comment(
    model_type: str, comment_id: str, db_Session=Depends(get_db)):    

    """intro-->This endpoint allows you to retrieve a specific comment of model type. To use this endpoint you need to make a get request to the /comments/{model_type}/{comment_id} endpoint 
            paramDesc-->On get request the url takes two parameters, model_type & comment_id
                param-->model_type: This is the model type of the comment
                param-->comment_id: This is the id of the comment

        returnDesc--> On sucessful request, it returns 
            returnBody--> the comment
    """
    comment_obj = db_retrieve_specific_comment_based_on_model_type(comment_id, model_type, db=db_Session)

    return comment_obj


@app.post("/comments/{model_type}/{comment_id}/reply")
def reply_to_comment(
    model_type: str,
    comment_id: int,
    comment: comments_schemas.CommentCreate,
    db_Session=Depends(get_db),
):
    """intro-->This endpoint is used to add a reply to a comment. To use this endpoint you need to make a post request to the /comments/{model_type}/{comment_id}/reply endpoint 
            paramDesc-->On post request the url takes two parameters, model_type & object_id
                param-->model_type: This is the model type of the comment
                param-->comment_id: This is the unique id of the comment

    returnDesc--> On sucessful request, it returns 
        returnBody--> The newly created comment
    """
    obj = db_reply_to_comment(
        comment_id=comment_id, comment=comment, model_type=model_type, db=db_Session
    )
    return {"status": True, "data": obj}


@app.post("/comments/{model_type}/{object_id}")
async def create_new_comment_for_object(
    model_type: str,
    object_id: str,
    background_tasks: BackgroundTasks,
    comment: comments_schemas.CommentBase,
    db_Session=Depends(get_db),
    user: users_schemas.User = Depends(is_authenticated)
):  
    """intro-->This endpoint is used to create a top level comment for an object. To use this endpoint you need to make a post request to the /comments/{model_type}/{object_id} endpoint 
            paramDesc-->On post request the url takes two parameters, model_type & object_id
                param-->model_type: This is the model type of the comment
                param-->object_id: This is the id of the comment to edit

    returnDesc--> On sucessful request, it returns 
        returnBody--> details of the refreshed comment
    """
    obj = db_create_comment_for_object(
        object_id=object_id, comment=comment, model_type=model_type, db=db_Session
    )

    commenter = db_Session.query(user_models.User).filter(user_models.User.id == comment.commenter_id).first()
    mentions = await get_mentions(comment.text)
    print(mentions)

    log = create_log_comment( 
        organization_id=comment.org_id,
        model_id=obj.id,
        comment=comment.text,
        model_name="Comment", 
        activity="added",
        created_for_id=object_id,
        created_for_model="biz_partner",
        db=db_Session, 
        user=user
    )

    notification = await create_comment_notification_format(
        organization_id=comment.org_id, 
        module="comments", 
        mentions=mentions,
        db=db_Session,
        user=user
    )    

    background_tasks.add_task(
        create_notification, 
        notification=notification, 
        user=user, 
        db=db_Session
    )

    background_tasks.add_task(
        createActivityLog, 
        model_name="Comment", model_id=obj.id, user=user, 
        log=log, db=db_Session, created_for_id=object_id, 
        created_for_model="biz_partner"
    )


    return {"status": True, "data": obj}


@app.put("/comments/{model_type}/{comment_id}/update")
def update_comment_by_id(
    model_type: str,
    comment_id: str,
    comment: comments_schemas.CommentUpdate,
    db_Session=Depends(get_db),
):
    """intro-->This endpoint is used to edit a comment object. To use this endpoint you need to make a put request to the /comments/{model_type}/{comment_id}/update endpoint 
            paramDesc-->On put request the url takes two parameters, model_type & comment_id
                param-->model_type: This is the model type of the comment
                param-->comment_id: This is the unique id of the comment

    returnDesc--> On sucessful request, it returns 
        returnBody--> details of the updated comment
    """
    obj = db_update_comment(
        object_id=comment_id, model_type=model_type, comment=comment, db=db_Session
    )
    return {"status": True, "data": obj}


@app.delete("/comments/{model_type}/{comment_id}/delete")
def delete_comment_by_id(
    model_type: str, comment_id:int, db_Session=Depends(get_db)
):
    """intro-->This endpoint is used to delete a comment. To use this endpoint you need to make a delete request to the /comments/{model_type}/{comment_id}/delete endpoint 
            paramDesc-->On delete request the url takes two parameters, model_type & comment_id
                param-->model_type: This is the model type of the comment
                param-->comment_id: This is the id of the comment to edit

    returnDesc--> On sucessful request, it returns 
        returnBody--> details of the deleted comment
    """
    obj = db_delete_comment(
        object_id=comment_id, model_type=model_type, db=db_Session
    )
    return {"status": True, "data": obj}


@app.post("/comments/{model_type}/{comment_id}/vote")
def vote_on_comment(
    model_type: str, comment_id:int, action: str, db_Session=Depends(get_db)
):  
    """intro-->This endpoint allows you to downvote or upvote a comment. To use this endpoint you need to make a post request to the /comments/{model_type}/{comment_id}/vote endpoint 
            paramDesc-->On post request the url takes in three parameters 
                param-->model_type: This is the model type of the comment
                param-->comment_id: This is the comment id of the comment to vote for
                param-->action: This is a query parameter, this determines the voting action you want to perform. Must be either "upvote" | "downvote"

                db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI

    returnDesc--> On sucessful request, it returns 
        returnBody--> a refreshed Comment object reflecting the changed votes
    """
   
    if action not in ["upvote", "downvote"]:
        return {
            "status": False,
            "message": {
                f"{action} not supported. Consider using 'upvote' or 'downvote'."
            },
        }
    response = db_vote_for_comments(
        comment_id=comment_id, model_type=model_type, action=action, db=db_Session
    )
    error_message = "Vote Failed"
    if response:
        return {"status": True, "data": response}
    return {"status": False, "message": error_message}



#=================================== COMMENT SERVICES =================================#

def create_log_comment(
    organization_id:str,
    model_id: str,
    model_name: str,
    comment: str, 
    created_for_id: str,
    created_for_model:str,
    db: _orm.Session,
    user: users_schemas.User = Depends(is_authenticated),
    activity: str = "added",
):      

    action = f'{user.first_name} {activity} a Comment "{comment}"'
    log = {
        'action': action,
        'organization_id': organization_id,
        'object_url': "comment"            
    }
    return log


def db_vote_for_comments(comment_id: int, model_type:str, action: str, db: _orm.Session):
    
    comment_obj = db_retrieve_comment_by_id(comment_id, model_type, db=db)
    if action == "upvote": comment_obj.upvote(),
    elif action == "downvote": comment_obj.downvote()
    db.commit()
    db.refresh(comment_obj)
    return comment_obj

def db_retrieve_comment_by_id(object_id: str, model_type:str, db: _orm.Session):
    """Retrieves a Comment by ID

    Args:
        object_id (int): ID of target Comment
        model_type (str): model type of comment
        db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI

    Returns:
        sqlalchemy Model Object: ORM Comment Object with ID = object_id
    """
    object = db.query(comments_models.Comment).filter(comments_models.Comment.id == object_id).first()
    if object:
        return object # SQLAlchecmy ORM Object 
    else: 
        return "DoesNotExist"

def db_retrieve_all_comments_for_object(object_id: int, model_type:str, db: _orm.Session):
    """Retrieve all Comments related to a specific object

    Args:
        object_id (int): ID of the object that maps to rel_id of the Comment
        model_type (str): Model Type of the object
        db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI

    Returns:
        List[schema. Comment]: A list of all comments and their threads, for a specific object
    """
    object_qs = (db.query(comments_models.Comment).filter(comments_models.Comment.rel_id == object_id, 
        comments_models.Comment.model_type == model_type, comments_models.Comment.p_id == None)
        .order_by(comments_models.Comment.last_updated.desc()))
    
    # object_qs = list(map(comments_schemas.Comment.from_orm, object_qs))
    # return object_qs[::-1]

    return object_qs

def db_retrieve_all_model_comments(model_type:str, db: _orm.Session):
    """Retrieve all comments of model type

    Args:
        model_type (str): Model Type
        db (_orm.Session): [description]

    Returns:
        List[Comment]: QuerySet of all Comments where model_type == model_type
    """
    object_qs = db.query(comments_models.Comment).filter(comments_models.Comment.model_type == model_type, comments_models.Comment.p_id == None).all()
    object_qs = list(map(comments_schemas.Comment.from_orm, object_qs))
    return object_qs

def db_reply_to_comment(model_type:str, comment_id:int, comment: comments_schemas.Comment, db: _orm.Session):
    """Reply to a comment 

    Args:
        model_type (str): Model Type of new Comment
        comment_id (int): ID of Comment to reply to 
        comment (comments_schemas.Comment): new Comment data
        db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI

    Returns:
        comments_schemas.Comment: The newly created Comment
    """
    p_comment = db.query(comments_models.Comment).filter(comments_models.Comment.model_type == model_type, 
        comments_models.Comment.id == comment_id).first()
    if p_comment:
        reply = comments_models.Comment(model_type=model_type, rel_id=p_comment.rel_id, email=comment.email, 
                name=comment.name, text=comment.text, p_id=p_comment.id, commenter_id=comment.commenter_id)
        db.add(reply)
        db.commit()
        db.refresh(reply)
        return reply
    return None

def db_delete_comment(object_id: int, model_type:str, db: _orm.Session):
    """Delete a Comment

    Args:
        object_id (int): ID of Comment to delete
        model_type (str): model type of comment to delete
        db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI

    Returns:
        Comment: Deleted Comment data
    """
    object = db_retrieve_comment_by_id(object_id=object_id, model_type=model_type, db=db)
    db.delete(object)
    db.commit()
    return comments_schemas.Comment.from_orm(object)
    
def db_create_comment_for_object(object_id: str, comment: comments_schemas.CommentBase, db: _orm.Session, model_type:str):
    """Create a top-level Comment for an object

    Args:
        object_id (str): ID of Object to create comment for. Maps to rel_id of comment
        comment (comments_schemas.CommentCreate): new Comment data
        db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI
        model_type (str): Model Type of the Comment to create.

    Returns:
        Comment: Data of the newly Created Comment
    """

    id = comment.id if comment.id else uuid4().hex
    obj = comments_models.Comment(id=id, rel_id=object_id, model_type=model_type, text=comment.text, 
                    name=comment.name, email=comment.email, commenter_id=comment.commenter_id, 
                    date_created=comment.date_created, last_updated=comment.last_updated)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    
    return obj

def db_update_comment(object_id:str, comment: comments_schemas.CommentUpdate, db: _orm.Session, model_type:str):
    """Edit a Comment Object

    Args:
        object_id (int): ID of Comment to edit
        comment (comments_schemas.CommentUpdate): New Comment data
        db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI
        model_type (str): Model Type of the Comment to edit

    Returns:
        Comment: Refreshed Comment data for Updated Comment
    """
    object_db = db_retrieve_comment_by_id(object_id=object_id, model_type=model_type, db=db)
    object_db.text = comment.text
    object_db.name = comment.name
    object_db.email = comment.email
    db.commit()
    db.refresh(object_db)
    return comments_schemas.Comment.from_orm(object_db)
    

def db_retrieve_specific_comment_based_on_model_type(object_id:str, model_type:str, db: _orm.Session):
    """Retrieves a comment of a model type by ID

    Args:
        object_id (int): ID of target Comment
        model_type (str): model type of comment
        db (_orm.Session): DB Session to commit to. Automatically determined by FastAPI

    Returns:
        sqlalchemy Model Object: ORM Comment Object with ID = object_id on Success, else 404 error
    """
    comment_obj = db.query(comments_models.Comment).filter(comments_models.Comment.model_type == model_type, 
                    comments_models.Comment.id == object_id).first()

    if comment_obj is None:
        raise _fastapi.HTTPException(
            status_code=404, detail="Comment does not exist"
        )

    return comment_obj                         
