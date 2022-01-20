
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Request
from typing import List
import fastapi as fastapi
from fastapi.param_functions import Depends
import fastapi.security as security
import sqlalchemy.orm as orm
from .auth import is_authenticated
from .schemas import users_schemas
from .schemas import blog_schemas
from .models import blog_models

from bigfastapi.db.database import get_db

app = APIRouter(tags=["Blog"])

@app.post("/blog", response_model=blog_schemas.Blog)
def create_blog(
    blog: blog_schemas.BlogCreate, 
    user: users_schemas.User = fastapi.Depends(is_authenticated), 
    db: orm.Session = fastapi.Depends(get_db)
):
    db_blog = get_blog_by_title(title=blog.title, db=db)
    if db_blog:
        raise fastapi.HTTPException(status_code=400, detail="Blog title already exists")
    return create_blog(blog=blog, user=user, db=db)

@app.get("/blog/{blog_id}")
def get_blog(
    blog_id: str, 
    db: orm.Session = fastapi.Depends(get_db), 
):
    return get_blog_by_id(id=blog_id, db=db)

@app.get("/blogs", response_model=List[blog_schemas.Blog])
def get_all_blogs(db: orm.Session = fastapi.Depends(get_db)):
    return get_all_blogs(db=db)

@app.get("/blogs/{user_id}", response_model=List[blog_schemas.Blog])
def get_user_blogs(
    user_id: str,
    db: orm.Session = fastapi.Depends(get_db) 
):
    return get_user_blogs(user_id=user_id, db=db)
    
@app.put("/blog/{blog_id}", response_model=blog_schemas.Blog)
def update_blog(
    blog: blog_schemas.BlogUpdate, 
    blog_id: str, 
    user: users_schemas.User = fastapi.Depends(is_authenticated),
    db: orm.Session = fastapi.Depends(get_db)
):
    return update_blog(blog=blog, id=blog_id, db=db, user=user)

@app.delete("/blog/{blog_id}")
def delete_blog(
    blog_id: str, 
    user: users_schemas.User = fastapi.Depends(is_authenticated),
    db: orm.Session = fastapi.Depends(get_db)
):
    return delete_blog(id=blog_id, db=db, user=user)



#=================================== BLOG SERVICES =================================#

def blog_selector(user: users_schemas.User, id: str, db: orm.Session):
    blog = db.query(blog_models.Blog).filter_by(creator=user.id).filter(blog_models.Blog.id == id).first()

    if blog is None:
        raise fastapi.HTTPException(status_code=404, detail="Blog does not exist")

    return blog

def get_blog_by_id(id: str, db: orm.Session):
    return db.query(blog_models.Blog).filter(blog_models.Blog.id == id).first()

def get_blog_by_title(title: str, db: orm.Session):
    return db.query(blog_models.Blog).filter(blog_models.Blog.title == title).first()


def get_user_blogs(user_id: str, db: orm.Session):
    user_blogs = db.query(blog_models.Blog).filter(blog_models.Blog.creator == user_id).all()
    return list(map(blog_schemas.Blog.from_orm, user_blogs))

def get_all_blogs(db: orm.Session):
    blogs = db.query(blog_models.Blog).all()
    return list(map(blog_schemas.Blog.from_orm, blogs))

def create_blog(blog: blog_schemas.BlogCreate, user: users_schemas.User, db: orm.Session):
    blog = blog_models.Blog(id=uuid4().hex, title=blog.title, content=blog.content, creator=user.id)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog_schemas.Blog.from_orm(blog)

def update_blog(blog: blog_schemas.BlogUpdate, id: str, db: orm.Session, user: users_schemas.User):
    blog_db = blog_selector(user=user, id=id, db=db)

    if blog.content != "":
        blog_db.content = blog.content

    if blog.title != "":
        blog_db_title = get_blog_by_title(title=blog.title, db=db)

        if blog_db_title:
            raise fastapi.HTTPException(status_code=400, detail="Blog title already in use")
        else:
            blog_db.title = blog.title

    blog_db.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(blog_db)

    return blog_schemas.Blog.from_orm(blog_db)

def delete_blog(id: str, db: orm.Session, user: users_schemas.User):
    blog = blog_selector(user=user, id=id, db=db)

    db.delete(blog)
    db.commit()

    return {"message":"successfully deleted"}