from typing import Optional, List, Any
from bigfastapi.comments.internal.exceptions import UnsupportedActionForComment
from fastapi import FastAPI, Depends
from bigfastapi.comments import services as _comment_services
from bigfastapi.comments import schemas as _schemas
import bigfastapi.database as _db

async def create_new_comment_for_model(model_name:Any, object_id:int, comment: _schemas.CommentCreate, db_Session=Depends(_db.get_db)):
    obj = await _comment_services.db_create_comment_for_object(object_id=object_id, comment=comment, model=model_name, db=db_Session)
    return {"status":True, "data":obj}

async def vote_on_comment(model_name:str, comment_id:str | int, action:str, db_Session=Depends(_db.get_db)):
    """Upvote or Downvote on a Comment

    Args:
        model_name (str): [for url_name]
        comment_id (str): [description]
        action (str): [upvote | downvote]
        db_Session ([type], optional): [description]. Defaults to Depends(_db.get_db).
    """
    
    if action not in ["upvote","downvote"]:
        raise UnsupportedActionForComment(action)
    response = await _comment_services.db_vote_for_comments(comment_id, model_name, action=action,db=db_Session)
    
    success_message = "Vote Successful"
    error_message = "Vote Failed"
    if response:
        return {"status":True, "data":response}
    return {"status":False, "message":error_message}

async def get_object_comments(model_name:str, object_id:Any, db_Session=Depends(_db.get_db)):
    qs = await _comment_services.db_retrieve_all_comments_for_object(object_id=object_id, model=model_name, db=db_Session)
    return {"status":True, "data":qs}

async def update_comment_by_id(model_name:str, comment_id:str | int, comment: _schemas.CommentUpdate, db_Session=Depends(_db.get_db)):
    obj = await _comment_services.db_update_comment(object_id=comment_id, model=model_name, comment=comment, db=db_Session)    
    return {"status":True, "data":obj}

async def delete_comment_by_id(model_name:str, comment_id:str | int, db_Session=Depends(_db.get_db)):
    obj = await _comment_services.db_delete_comment(object_id=comment_id, model=model_name, db=db_Session)    
    return {"status":True, "data":obj}



async def get_all_comments_related_to_model(model_name:str, db_Session=Depends(_db.get_db)):
    qs = await _comment_services.db_retrieve_all_model_comments(model=model_name, db=db_Session)
    return {"status":True, "data":qs}

