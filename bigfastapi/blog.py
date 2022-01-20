from fastapi import APIRouter, Request
from typing import List
import fastapi as _fastapi
from fastapi.param_functions import Depends
import fastapi.security as _security
import sqlalchemy.orm as _orm
from . import services as _services, schema as _schemas
from bigfastapi.db.database import get_db

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



#=================================== BLOG SERVICES =================================#

async def _blog_selector(user: _schemas.User, id: str, db: _orm.Session):
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
    return list(map(_schemas.Blog.from_orm, user_blogs))

async def get_all_blogs(db: _orm.Session):
    blogs = db.query(_models.Blog).all()
    return list(map(_schemas.Blog.from_orm, blogs))

async def create_blog(blog: _schemas.BlogCreate, user: _schemas.User, db:_orm.Session):
    blog = _models.Blog(id=uuid4().hex, title=blog.title, content=blog.content, creator=user.id)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return _schemas.Blog.from_orm(blog)

async def update_blog(blog: _schemas.BlogUpdate, id: str, db: _orm.Session, user: _schemas.User):
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

    return _schemas.Blog.from_orm(blog_db)

async def delete_blog(id: str, db: _orm.Session, user: _schemas.User):
    blog = await _blog_selector(user=user, id=id, db=db)

    db.delete(blog)
    db.commit()

    return {"message":"successfully deleted"}