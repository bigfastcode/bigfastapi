from fastapi import APIRouter, Request
from typing import List
import fastapi as _fastapi
from fastapi.param_functions import Depends
import fastapi.security as _security
import sqlalchemy.orm as _orm
from . import services as _services, schema as _schemas
from bigfastapi.database import get_db

app = APIRouter(tags=["Blog"])

@app.post("/blog", response_model=_schemas.Blog)
async def create_blog(
    blog: _schemas.BlogCreate, 
    user: _schemas.User = _fastapi.Depends(_services.is_authenticated), 
    db: _orm.Session = _fastapi.Depends(get_db)
):
    db_blog = await _services.get_blog_by_title(title=blog.title, db=db)
    if db_blog:
        raise _fastapi.HTTPException(status_code=400, detail="Blog title already exists")
    return await _services.create_blog(blog=blog, user=user, db=db)

@app.get("/blog/{blog_id}")
async def get_blog(
    blog_id: str, 
    db: _orm.Session = _fastapi.Depends(get_db), 
):
    return await _services.get_blog_by_id(id=blog_id, db=db)

@app.get("/blogs", response_model=List[_schemas.Blog])
async def get_all_blogs(db: _orm.Session = _fastapi.Depends(get_db)):
    return await _services.get_all_blogs(db=db)

@app.get("/blogs/{user_id}", response_model=List[_schemas.Blog])
async def get_user_blogs(
    user_id: str,
    db: _orm.Session = _fastapi.Depends(get_db) 
):
    return await _services.get_user_blogs(user_id=user_id, db=db)
    
@app.put("/blog/{blog_id}", response_model=_schemas.Blog)
async def update_blog(
    blog: _schemas.BlogUpdate, 
    blog_id: str, 
    user: _schemas.User = _fastapi.Depends(_services.is_authenticated),
    db: _orm.Session = _fastapi.Depends(get_db)
):
    return await _services.update_blog(blog=blog, id=blog_id, db=db, user=user)

@app.delete("/blog/{blog_id}")
async def delete_blog(
    blog_id: str, 
    user: _schemas.User = _fastapi.Depends(_services.is_authenticated),
    db: _orm.Session = _fastapi.Depends(get_db)
):
    return await _services.delete_blog(id=blog_id, db=db, user=user)