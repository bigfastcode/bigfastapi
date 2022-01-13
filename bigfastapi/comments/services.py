from fastapi import Depends
import sqlalchemy.orm as _orm
from bigfastapi.comments import schemas as _schemas
from bigfastapi.database import get_db, Base
from typing import List, Any, Optional

from bigfastapi.comments.internal.exceptions import DoesNotExist

async def db_vote_for_comments(comment_id: int, model: Base, action: str, db: _orm.Session):
    """[summary]

    Args:
        comment_id (int): [description]
        model (Base): [description]
        action (str): "upvote" | "downvote"
        db (_orm.Session): [description]
    """ 
    comment_obj = await db_retrieve_comment_by_id(comment_id, model, db=db)
    if action == "upvote": comment_obj.upvote(),
    elif action == "downvote": comment_obj.downvote()
    db.commit()
    db.refresh(comment_obj)
    return comment_obj

async def db_retrieve_comment_by_id(object_id: int, model: Base, db: _orm.Session):
    object = db.query(model.Comment).filter(model.Comment.id == object_id).first()
    if object:
        return object # SQLAlchecmy ORM Object 
    else: 
        raise DoesNotExist(f"{model.Comment} {object_id}")

async def db_retrieve_all_comments_for_object(object_id: int, model: Base, db: _orm.Session):
    object_qs = db.query(model.Comment).filter(model.Comment.rel_id == object_id).all()
    object_qs = list(map(_schemas.Comment.from_orm, object_qs))
    return object_qs

async def db_retrieve_all_model_comments(model: Base, db: _orm.Session):
    object_qs = db.query(model.Comment).all()
    object_qs = list(map(_schemas.Comment.from_orm, object_qs))
    return object_qs

async def db_delete_comment(object_id: str|int, model: Base, db: _orm.Session):
    object = await db_retrieve_comment_by_id(object_id=object_id, model=model, db=db)
    db.delete(object)
    db.commit()
    return _schemas.Comment.from_orm(object)
    
async def db_create_comment_for_object(object_id: int, comment: _schemas.CommentCreate, model: Base, db: _orm.Session):
    obj = model.Comment(rel_id=object_id, text=comment.text, name=comment.name, email=comment.email)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _schemas.Comment.from_orm(obj)

async def db_update_comment(object_id:int, model: Base, comment: _schemas.CommentUpdate,db: _orm.Session):
    object_db = await db_retrieve_comment_by_id(object_id=object_id, model=model, db=db)
    object_db.text = comment.text
    object_db.name = comment.name
    object_db.email = comment.email
    db.commit()
    db.refresh(object_db)
    return _schemas.Comment.from_orm(object_db)
    