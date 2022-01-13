from typing import Optional, List, Any
from fastapi import FastAPI, Depends
from bigfastapi.comments.internal import fixtures as _fixtures
from bigfastapi.comments.internal import schemas as _schemas
from bigfastapi.comments.decorators import comment_view_wrapper
from bigfastapi import database as _db


app = FastAPI()

@app.get("/app")
@comment_view_wrapper(action="GET", model_name=_fixtures.Actor)
def all_comment_actor(db_Session = Depends(_db.get_db)):
    pass 

@app.post("/app/{object_id}")
@comment_view_wrapper(action="CREATE", model_name=_fixtures.Actor)
def create_comment_for_actor_object(object_id:Any, comment: _schemas.CommentCreate, db_Session = Depends(_db.get_db)):
    pass 

@app.get("/app/{object_id}")
@comment_view_wrapper(action="READ", model_name=_fixtures.Actor)
def read_comment_for_actor_object(object_id:Any, db_Session = Depends(_db.get_db)):
    pass 

@app.put("/app/comments/{comment_id}")
@comment_view_wrapper(action="UPDATE", model_name=_fixtures.Actor)
def update_comment_for_actor_object(comment_id:Any, comment: _schemas.CommentCreate, db_Session = Depends(_db.get_db)):
    pass 

@app.delete("/app/comments/{comment_id}")
@comment_view_wrapper(action="DELETE", model_name=_fixtures.Actor)
def delete_comment_for_actor_object(comment_id:Any, db_Session = Depends(_db.get_db)):
    pass 

@app.get("/app/comments/vote/{comment_id}")
@comment_view_wrapper(action="VOTE", model_name=_fixtures.Actor)
def vote_for_comment(comment_id:Any, vote_action:str, db_Session = Depends(_db.get_db)):
    pass 
