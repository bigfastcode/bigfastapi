from fastapi import APIRouter, Request
from typing import List, Any
import fastapi as _fastapi
from fastapi.param_functions import Depends
import fastapi.security as _security
import sqlalchemy.orm as _orm
from . import services as _services, schema as _schemas
from bigfastapi.database import get_db

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
async def create_new_comment_for_object(
    model_name: str,
    object_id: int,
    comment: _schemas.CommentCreate,
    db_Session=Depends(get_db),
):
    obj = await _services.db_create_comment_for_object(
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
    obj = await _services.db_update_comment(
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
