from pyexpat import model
import fastapi as _fastapi
from fastapi import Request
from fastapi.openapi.models import HTTPBearer
import fastapi.security as _security
import jwt as _jwt
import datetime as _dt
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from bigfastapi import database as _database, settings as settings
from . import models as _models, schema as _schemas
from .token import *
from .code import *
from .send_mail import *



from fastapi.security import HTTPBearer
bearerSchema = HTTPBearer()
import re

JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 60 * 5


async def get_user_by_email(email: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.email == email).first()

async def get_user_by_id(id: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.id == id).first()

async def get_orgnanization_by_name(name: str, db: _orm.Session):
    return db.query(_models.Organization).filter(_models.Organization.name == name).first()


async def is_authenticated(request: Request, token:str = _fastapi.Depends(bearerSchema), db: _orm.Session = _fastapi.Depends(_database.get_db)):
    token = token.credentials
    validate_resp = await validate_token(token)
    if not validate_resp["status"]:
        raise _fastapi.HTTPException(
            status_code=401, detail=validate_resp["data"]
        )

    user = await get_user_by_id(db=db, id=validate_resp["data"]["user_id"])
    db_token = await get_token_from_db(token, db)
    if db_token:
        return _schemas.User.from_orm(user)
    else:
        raise _fastapi.HTTPException(
            status_code=401, detail="invalid token"
        )


    


async def create_user(verification_method: str, user: _schemas.UserCreate, db: _orm.Session):
    verification_info = ""
    user_obj = _models.User(
        id = uuid4().hex,email=user.email, password=_hash.bcrypt.hash(user.password),
        first_name=user.first_name, last_name=user.last_name,
        is_active=True, is_verified = False
    )
    db.add(user_obj)
    db.commit()
    if verification_method == "code":
        code = await resend_code_verification_mail(user_obj.email, db, user.verification_code_length)
        verification_info = code["code"]
    elif verification_method == "token":
        token = await resend_token_verification_mail(user_obj.email,user.verification_redirect_url, db)
        verification_info = token["token"]
    db.refresh(user_obj)
    return {"user":user_obj, "verification_info": verification_info}


async def authenticate_user(email: str, password: str, db: _orm.Session):
    user = await get_user_by_email(db=db, email=email)

    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user

async def logout(user: _schemas.User):
    db = _database.SessionLocal()
    db_token = await get_token_by_userid(user_id= user.id, db=db)
    print(db_token)
    db.delete(db_token)
    db.commit()
    return True

async def user_update(user_update: _schemas.UserUpdate, user:_schemas.User, db: _orm.Session):
    user = await get_user_by_id(id = user.id, db=db)

    if user_update.first_name != "":
        user.first_name = user_update.first_name

    if user_update.last_name != "":
        user.last_name = user_update.last_name

    if user_update.phone_number != "":
        user.phone_number = user_update.phone_number
        
    if user_update.organization != "":
        user.organization = user_update.organization

    db.commit()
    db.refresh(user)

    return _schemas.User.from_orm(user)


async def verify_user_code(code:str):
    db = _database.SessionLocal()
    code_db = await get_code_from_db(code, db)
    if code_db:
        user = await get_user_by_id(db=db, id=code_db.user_id)
        user.is_verified = True

        db.commit()
        db.refresh(user)
        db.delete(code_db)
        db.commit()
        return _schemas.User.from_orm(user)
    else:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Code")

async def password_change_code(password: _schemas.UserPasswordUpdate, code: str, db: _orm.Session):

    code_db = await get_password_reset_code_from_db(code, db)
    if code_db:
        user = await get_user_by_id(db=db, id=code_db.user_id)
        user.password = _hash.bcrypt.hash(password.password)
        db.commit()
        db.refresh(user)

        db.delete(code_db)
        db.commit()
        return {"message": "password change successful"}
    else:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Token")

async def verify_user_token(token:str):
    db = _database.SessionLocal()
    validate_resp = await validate_token(token)
    if not validate_resp["status"]:
        raise _fastapi.HTTPException(
            status_code=401, detail=validate_resp["data"]
        )

    user = await get_user_by_id(db=db, id=validate_resp["data"]["user_id"])
    user.is_verified = True

    db.commit()
    db.refresh(user)

    return _schemas.User.from_orm(user)
async def password_change_token(password: _schemas.UserPasswordUpdate, token: str, db: _orm.Session):
    validate_resp = await validate_token(token)
    if not validate_resp["status"]:
        raise _fastapi.HTTPException(
            status_code=401, detail=validate_resp["data"]
        )

    token_db = db.query(_models.PasswordResetToken).filter(_models.PasswordResetToken.token == token).first()
    if token_db:
        user = await get_user_by_id(db=db, id=validate_resp["data"]["user_id"])
        user.password = _hash.bcrypt.hash(password.password)
        db.commit()
        db.refresh(user)

        db.delete(token_db)
        db.commit()
        return {"message": "password change successful"}
    else:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Token")





def validate_email(email):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if(re.search(regex, email)):
        return {"status": True, "message": "Valid"} 
    else:
        return {"status": False, "message": "Enter Valid E-mail"}


async def create_organization(user: _schemas.User, db: _orm.Session, organization: _schemas.OrganizationCreate):
    organization = _models.Organization(id=uuid4().hex, creator=user.id, mission= organization.mission, 
    vision= organization.vision, values= organization.values, name= organization.name)
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return _schemas.Organization.from_orm(organization)


async def get_organizations(user: _schemas.User, db: _orm.Session):
    organizations = db.query(_models.Organization).filter_by(owner_id=user.id)

    return list(map(_schemas.Organization.from_orm, organizations))


async def _organization_selector(organization_id: int, user: _schemas.User, db: _orm.Session):
    organization = (
        db.query(_models.Organization)
        .filter_by(creator=user.id)
        .filter(_models.Organization.id == organization_id)
        .first()
    )

    if organization is None:
        raise _fastapi.HTTPException(status_code=404, detail="Organization does not exist")

    return organization


async def get_organization(organization_id: int, user: _schemas.User, db: _orm.Session):
    organization = await _organization_selector(organization_id=organization_id, user=user, db=db)

    return _schemas.Organization.from_orm(organization)


async def delete_organization(organization_id: int, user: _schemas.User, db: _orm.Session):
    organization = await _organization_selector(organization_id, user, db)

    db.delete(organization)
    db.commit()

async def update_organization(organization_id: int, organization: _schemas.OrganizationUpdate, user: _schemas.User, db: _orm.Session):
    organization_db = await _organization_selector(organization_id, user, db)

    if organization.mission != "":
        organization_db.mission = organization.mission

    if organization.vision != "":
        organization_db.vision = organization.vision

    if organization.values != "":
        organization_db.values = organization.values

    if organization.name != "":
        db_org = await get_orgnanization_by_name(name = organization.name, db=db)
        if db_org:
            raise _fastapi.HTTPException(status_code=400, detail="Organization name already in use")
        else:
            organization_db.name = organization.name       

    organization_db.last_updated = _dt.datetime.utcnow()

    db.commit()
    db.refresh(organization_db)

    return _schemas.Organization.from_orm(organization_db)



async def _blog_selector(user: _schemas.User, blog_id: str, db: _orm.Session):
    blog = db.query(_models.Blog).filter_by(creator=user.id).filter(_models.Blog.id == blog_id).first()

    if blog is None:
        raise _fastapi.HTTPException(status_code=404, detail="Blog does not exist")

    return blog

async def get_blog_by_title(title: str, db: _orm.Session):
    return db.query(_models.Blog).filter(_models.Blog.title == title).first()


async def get_user_blogs(user: _schemas.User, db: _orm.Session):
    user_blogs = db.query(_models.Blog).filter_by(_models.Blog.creator == user.id)
    return list(map(_schemas.Blog.from_orm, user_blogs))

async def get_all_blogs(db: _orm.Session):
    blogs = db.query(_models.Blog).all()
    return list(map(_schemas.Blog.from_orm, blogs))

async def create_blog(blog: _schemas.BlogCreate, user: _schemas.User, db:_orm.Session):
    blog = _models.Blog(id=uuid4.hex(), title=blog.title, content=blog.content, creator=user.id)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return _schemas.Blog.from_orm(blog)

async def update_blog(blog: _schemas.BlogUpdate, blog_id: str, db: _orm.Session, user: _schemas.User):
    blog_db = await _blog_selector(user=user, blog_id=blog_id, db=db)

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

async def delete_blog(blog_id: int, db: _orm.Session, user: _schemas.User):
    blog = await _blog_selector(user=user, blog_id=blog_id, db=db)

    db.delete(blog)
    db.commit()
#=================================== COMMENTS =================================#

async def db_vote_for_comments(comment_id: int, model_name:str, action: str, db: _orm.Session):
    """[summary]

    Args:
        comment_id (int): [description]
        model (Base): [description]
        action (str): "upvote" | "downvote"
        db (_orm.Session): [description]
    """ 
    comment_obj = await db_retrieve_comment_by_id(comment_id, model_name, db=db)
    if action == "upvote": comment_obj.upvote(),
    elif action == "downvote": comment_obj.downvote()
    db.commit()
    db.refresh(comment_obj)
    return comment_obj

async def db_retrieve_comment_by_id(object_id: int, model_name:str, db: _orm.Session):
    object = db.query(_models.Comment).filter(_models.Comment.id == object_id).first()
    if object:
        return object # SQLAlchecmy ORM Object 
    else: 
        return "DoesNotExist"

async def db_retrieve_all_comments_for_object(object_id: int, model_name:str, db: _orm.Session):
    object_qs = db.query(_models.Comment).filter(_models.Comment.rel_id == object_id, 
        _models.Comment.model_type == model_name, _models.Comment.p_id == None).all()
    
    object_qs = list(map(_schemas.Comment.from_orm, object_qs))
    return object_qs

async def db_retrieve_all_model_comments(model_name:str, db: _orm.Session):
    object_qs = db.query(_models.Comment).filter(_models.Comment.model_type == model_name, _models.Comment.p_id == None).all()
    object_qs = list(map(_schemas.Comment.from_orm, object_qs))
    return object_qs

async def db_reply_to_comment(model_name:str, comment_id:int, comment: _schemas.Comment, db: _orm.Session):
    p_comment = db.query(_models.Comment).filter(_models.Comment.model_type == model_name, 
        _models.Comment.id == comment_id).first()
    if p_comment:
        reply = _models.Comment(model_name=model_name, rel_id=p_comment.rel_id, email=comment.email, name=comment.name, text=comment.text, p_id=p_comment.id)
        db.add(reply)
        db.commit()
        db.refresh(reply)
        return reply
    return None

async def db_delete_comment(object_id: int, model_name:str, db: _orm.Session):
    object = await db_retrieve_comment_by_id(object_id=object_id, model_name=model_name, db=db)
    db.delete(object)
    db.commit()
    return _schemas.Comment.from_orm(object)
    
def db_create_comment_for_object(object_id: int, comment: _schemas.CommentCreate, db: _orm.Session, model_name:str = None):
    obj = _models.Comment(rel_id=object_id, model_name=model_name, text=comment.text, name=comment.name, email=comment.email)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _schemas.Comment.from_orm(obj)

async def db_update_comment(object_id:int, comment: _schemas.CommentUpdate, db: _orm.Session, model_name:str = None):
    object_db = await db_retrieve_comment_by_id(object_id=object_id, model_name=model_name, db=db)
    object_db.text = comment.text
    object_db.name = comment.name
    object_db.email = comment.email
    db.commit()
    db.refresh(object_db)
    return _schemas.Comment.from_orm(object_db)
    
