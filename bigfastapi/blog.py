
from uuid import uuid4
from fastapi import APIRouter, Request
from typing import List
import fastapi as _fastapi
from fastapi.param_functions import Depends
import fastapi.security as _security
import sqlalchemy.orm as _orm
from .auth import is_authenticated
from .schemas import users_schemas
from .schemas import blog_schemas
from .models import blog_models as _models

from bigfastapi.db.database import get_db

app = APIRouter(tags=["Blog"])

@app.post("/blog", response_model=blog_schemas.Blog)
async def create_blog(
    blog: blog_schemas.BlogCreate, 
    user: users_schemas.User = _fastapi.Depends(is_authenticated), 
    db: _orm.Session = _fastapi.Depends(get_db)
):
    db_blog = await get_blog_by_title(title=blog.title, db=db)
    if db_blog:
        raise _fastapi.HTTPException(status_code=400, detail="Blog title already exists")
    return await create_blog(blog=blog, user=user, db=db)

@app.get("/blog/{blog_id}")
async def get_blog(
    blog_id: str, 
    db: _orm.Session = _fastapi.Depends(get_db), 
):
    return await get_blog_by_id(id=blog_id, db=db)

@app.get("/blogs", response_model=List[blog_schemas.Blog])
async def get_all_blogs(db: _orm.Session = _fastapi.Depends(get_db)):
    return await get_all_blogs(db=db)

@app.get("/blogs/{user_id}", response_model=List[blog_schemas.Blog])
async def get_user_blogs(
    user_id: str,
    db: _orm.Session = _fastapi.Depends(get_db) 
):
    return await get_user_blogs(user_id=user_id, db=db)
    
@app.put("/blog/{blog_id}", response_model=blog_schemas.Blog)
async def update_blog(
    blog: blog_schemas.BlogUpdate, 
    blog_id: str, 
    user: users_schemas.User = _fastapi.Depends(is_authenticated),
    db: _orm.Session = _fastapi.Depends(get_db)
):
    return await update_blog(blog=blog, id=blog_id, db=db, user=user)

@app.delete("/blog/{blog_id}")
async def delete_blog(
    blog_id: str, 
    user: users_schemas.User = _fastapi.Depends(is_authenticated),
    db: _orm.Session = _fastapi.Depends(get_db)
):
    return await delete_blog(id=blog_id, db=db, user=user)



#=================================== BLOG SERVICES =================================#

async def _blog_selector(user: users_schemas.User, id: str, db: _orm.Session):
    blog = db.query(_models.Blog).filter_by(creator=user.id).filter(_models.Blog.id == id).first()

    if blog is None:
        raise _fastapi.HTTPException(status_code=404, detail="Blog does not exist")

    return blog

async def get_blog_by_id(id: str, db: _orm.Session):
    return db.query(_models.Blog).filter(_models.Blog.id == id).first()

async def get_blog_by_title(title: str, db: _orm.Session):
    return db.query(_models.Blog).filter(_models.Blog.title == title).first()


async def get_user_blogs(user_id: str, db: _orm.Session):
    user_blogs = db.query(_models.Blog).filter(_models.Blog.creator == user_id).all()
    return list(map(blog_schemas.Blog.from_orm, user_blogs))

async def get_all_blogs(db: _orm.Session):
    blogs = db.query(_models.Blog).all()
    return list(map(blog_schemas.Blog.from_orm, blogs))

async def create_blog(blog: blog_schemas.BlogCreate, user: users_schemas.User, db:_orm.Session):
    blog = _models.Blog(id=uuid4().hex, title=blog.title, content=blog.content, creator=user.id)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog_schemas.Blog.from_orm(blog)

async def update_blog(blog: blog_schemas.BlogUpdate, id: str, db: _orm.Session, user: users_schemas.User):
    blog_db = await _blog_selector(user=user, id=id, db=db)

    if blog.content != "":
        blog_db.content = blog.content

    if blog.title != "":
        blog_db_title = await get_blog_by_title(title=blog.title, db=db)

        if blog_db_title:
            raise _fastapi.HTTPException(status_code=400, detail="Blog title already in use")
        else:
            blog_db.title = blog.title

    blog_db.last_updated = _dt.datetime.utcnow()

    db.commit()
    db.refresh(blog_db)

    return blog_schemas.Blog.from_orm(blog_db)

async def delete_blog(id: str, db: _orm.Session, user: users_schemas.User):
    blog = await _blog_selector(user=user, id=id, db=db)

    db.delete(blog)
    db.commit()

    return {"message":"successfully deleted"}