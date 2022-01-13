import sys 
from functools import wraps
import asyncio
from bigfastapi.comments import adapters as adp
from bigfastapi.comments.internal.exceptions import UnsupportedActionForComment
from bigfastapi.comments.internal import fixtures as _fixtures
from bigfastapi import database as _database, settings as settings

def comment_view_wrapper(action:str ="GET", model_name: _database.Base = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            response_obj = None 
            object_id = kwargs.get("object_id")
            comment = kwargs.get("comment")
            comment_id = kwargs.get("comment_id")
            db_Session = kwargs.get("db_Session")
            vote_action =kwargs.get("vote_action")
            
            if action == "CREATE":
                # Create new comment for a particular model object [object_id, comment]
                response_obj = await adp.create_new_comment_for_model(model_name=model_name, object_id=object_id, comment=comment, db_Session=db_Session)
                return response_obj
                
            elif action == "READ":
                # Get all comments for a particular model object [object_id]
                response_obj = await adp.get_object_comments(model_name=model_name, object_id=object_id, db_Session=db_Session)
                return response_obj

            elif action == "UPDATE":
                # Update a particular comment from a particular model object [comment_id]
                response_obj = await adp.update_comment_by_id(model_name=model_name, comment_id=comment_id, comment=comment, db_Session=db_Session)
                return response_obj

            elif action == "DELETE":
                # Delete a comment from a particular model object [comment_id]
                response_obj = await adp.delete_comment_by_id(model_name=model_name, comment_id=comment_id, db_Session=db_Session)
                return response_obj
            elif action == "GET":
                # Get all comments associated with a particular type
                response_obj = await adp.get_all_comments_related_to_model(model_name=model_name, db_Session=db_Session)
                return response_obj
            elif action == "VOTE":
                # Vote on a comment [comment_id, action = ["upvote"|"downvote"]]
                response_obj = await adp.vote_on_comment(model_name=model_name, comment_id=comment_id, action=vote_action, db_Session=db_Session)
                return response_obj
            else:
                raise UnsupportedActionForComment

        return wrapper
    return decorator