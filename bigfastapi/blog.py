
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter
from typing import List
import fastapi as fastapi
import sqlalchemy.orm as orm
from bigfastapi.services.auth_service import is_authenticated
from .schemas import users_schemas as user_schema
from .schemas import blog_schemas as schema
from .models import blog_models as model

from bigfastapi.db.database import get_db

app = APIRouter(tags=["Blog"])

@app.post("/blog", response_model=schema.Blog)
def create_blog(blog: schema.BlogCreate, user: user_schema.User = fastapi.Depends(is_authenticated), db: orm.Session = fastapi.Depends(get_db)):
    
    """intro-->This endpoint allows you to create a create a new blog post on the fly and takes in about two paramenters. To create a blog, you need to make a post request to the /blog endpoint

    paramDesc-->


        reqBody-->title: This is the title of the blog post to be created.
        reqBody-->content: This is the content of the blog post to be created.

    returnDesc-->On sucessful request, it returns

    
        returnBody--> the blog object with details specified below.
    """
    
    # db_blog = model.get_blog_by_title(title=blog.title, db=db)
    if model.get_blog_by_title(title=blog.title, db=db):
        raise fastapi.HTTPException(status_code=400, detail="Blog title already exists")
    
    blog = model.Blog(id=uuid4().hex, title=blog.title, content=blog.content, creator=user.id)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return schema.Blog.from_orm(blog)

@app.get("/blog/{blog_id}")
def get_blog(blog_id: str, db: orm.Session = fastapi.Depends(get_db), ):

    """intro-->This endpoint allows you to retreive a blog post based on it's id which is included in the request url. To get a blog post, you need to make a get request to the /blog/blog_id endpoint in which "id" is the unique identifier of the blog item.

    paramDesc-->On get request the url takes a query parameter "blog_id":
        param-->blog_id: This is the id of the blog item

    returnDesc-->On sucessful request, it returns message,
        returnBody--> "success"
    """

    return db.query(model.Blog).filter(model.Blog.id == blog_id).first()

@app.get("/blogs", response_model=List[schema.Blog])
def get_all_blogs(db: orm.Session = fastapi.Depends(get_db)):

    """intro-->This endpoint allows you to retreive all blog posts in the database. To retreive all blog posts, you need to make a get request to the /blog endpoint.
    
     returnDesc-->On sucessful request, it returns:
        returnBody--> an array of blog objects.
    """

    blogs = db.query(model.Blog).all()
    return list(map(schema.Blog.from_orm, blogs))

@app.get("/blogs/{user_id}", response_model=List[schema.Blog])
def get_user_blogs(user_id: str, db: orm.Session = fastapi.Depends(get_db)):

    """intro-->This endpoint allows you to retreive all blog posts created by a particular user. To retreive all blog posts by a user, you need to make a get request to the /blog/userId endpoint where userId is the unique identifier for the user.

   paramDesc-->On get request the url takes a query parameter "user_id"   
        param-->user_id: This is the id of the user

    returnDesc-->On sucessful request, it returns
         returnBody--> an array of blog post objects created by the queried user.
    """

    user_blogs = db.query(model.Blog).filter(model.Blog.creator == user_id).all()
    return list(map(schema.Blog.from_orm, user_blogs))
    
@app.put("/blog/{blog_id}", response_model=schema.Blog)
def update_blog(blog: schema.BlogUpdate, blog_id: str, user: user_schema.User = fastapi.Depends(is_authenticated), db: orm.Session = fastapi.Depends(get_db)):

    """intro-->This endpoint allows you to update a particular blog post. To update a blog posts, you need to make a put request to the /blog/blog_id endpoint where blog_id is the unique identifier for the blog.
    
    paramDesc-->On query, this request takes the blod id of the blog to be updated:
        reqBody-->title: This is the title of the blog post to be created.
        reqBody-->content: This is the content of the blog post to be created.

    returnDesc-->On sucessful request, it returns
       returnBody--> a refreshed object of the updated blog
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
    
    """intro-->This endpoint allows you to delete a particular blog post. To delete a blog posts, you need to make a delete request to the /blog/blog_id endpoint where blog_id is the unique identifier for the blog.
    
    paramDesc-->On delete request the url takes a query parameter "blog_id":
        param-->blog_id: This is the unique id of the blog item


    returnDesc-->On sucessful request, it returns an Object with message
       returnBody--> "successfully deleted"
    """
    
    blog = model.blog_selector(user=user, id=blog_id, db=db)
    if blog == None:
        raise fastapi.HTTPException(status_code=404, detail="Blog does not exist")
        
    db.delete(blog)
    db.commit()

    return {"message":"successfully deleted"}
