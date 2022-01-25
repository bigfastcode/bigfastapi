
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter
from typing import List
import fastapi as fastapi
import sqlalchemy.orm as orm
from .auth import is_authenticated
from .schemas import users_schemas as user_schema
from .schemas import blog_schemas as schema
from .models import blog_models as model

from bigfastapi.db.database import get_db

app = APIRouter(tags=["Blog"])

@app.post("/blog", response_model=schema.Blog)
def create_blog(blog: schema.BlogCreate, user: user_schema.User = fastapi.Depends(is_authenticated), db: orm.Session = fastapi.Depends(get_db)):
    
    """Create a new blog
    
    Returns:
        schema.Blog: Details of the newly created blog
    """
    
    db_blog = model.get_blog_by_title(title=blog.title, db=db)
    if db_blog:
        raise fastapi.HTTPException(status_code=400, detail="Blog title already exists")
    
    blog = model.Blog(id=uuid4().hex, title=blog.title, content=blog.content, creator=user.id)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return schema.Blog.from_orm(blog)

@app.get("/blog/{blog_id}")
def get_blog(blog_id: str, db: orm.Session = fastapi.Depends(get_db), ):

    """Get the details of a blog
    
    Args:
        blog_id (str): the id of the blog

    Returns:
        schema.Blog: Details of the requested blog
    """

    return db.query(model.Blog).filter(model.Blog.id == blog_id).first()

@app.get("/blogs", response_model=List[schema.Blog])
def get_all_blogs(db: orm.Session = fastapi.Depends(get_db)):

    """Get all the blogs in the database
    
    Returns:
        List of schema.Blog: A list of all the blogs
    """

    blogs = db.query(model.Blog).all()
    return list(map(schema.Blog.from_orm, blogs))

@app.get("/blogs/{user_id}", response_model=List[schema.Blog])
def get_user_blogs(user_id: str, db: orm.Session = fastapi.Depends(get_db)):

    """Get all the blogs created by a user
    
    Args:
        user_id (str): the id of the user

    Returns:
        List of schema.Blog: A list of all the blogs created by the user
    """

    user_blogs = db.query(model.Blog).filter(model.Blog.creator == user_id).all()
    return list(map(schema.Blog.from_orm, user_blogs))
    
@app.put("/blog/{blog_id}", response_model=schema.Blog)
def update_blog(blog: schema.BlogUpdate, blog_id: str, user: user_schema.User = fastapi.Depends(is_authenticated), db: orm.Session = fastapi.Depends(get_db)):

    """Update the details of a blog
    
    Args:
        blog_id (str): the id of the blog to be updated

    Returns:
        schema.Blog: Refreshed data of the updated blog
    """

    blog_db = model.blog_selector(user=user, id=blog_id, db=db)

    if blog_db == None:
        raise fastapi.HTTPException(status_code=404, detail="Blog does not exist")

    if blog.content != "":
        blog_db.content = blog.content

    if blog.title != "":
        blog_db_title = model.get_blog_by_title(title=blog.title, db=db)

        if blog_db_title:
            raise fastapi.HTTPException(status_code=400, detail="Blog title already in use")
        else:
            blog_db.title = blog.title

    blog_db.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(blog_db)

    return schema.Blog.from_orm(blog_db)

@app.delete("/blog/{blog_id}")
def delete_blog(blog_id: str, user: user_schema.User = fastapi.Depends(is_authenticated), db: orm.Session = fastapi.Depends(get_db)):
    
    """Delete a blog from the database
    
    Args:
        blog_id (str): the id of the blog to be deleted

    Returns:
        object (dict): successfully deleted
    """
    
    blog = model.blog_selector(user=user, id=blog_id, db=db)
    if blog == None:
        raise fastapi.HTTPException(status_code=404, detail="Blog does not exist")
        
    db.delete(blog)
    db.commit()

    return {"message":"successfully deleted"}
