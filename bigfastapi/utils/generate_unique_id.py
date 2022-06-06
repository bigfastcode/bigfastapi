import math
from fastapi import Depends
from bigfastapi.db.database import get_db
import sqlalchemy.orm as orm
import random
from sqlalchemy import desc

def generate_unique_id(model, organization_id, db: orm.Session = Depends(get_db), sort_key="created_at"):
   
    last_model=(db.query(model)
        .filter(model.organization_id == organization_id)
        .order_by(getattr(model, sort_key, "created_at")).first()) #model.created_at.desc()).first())
    #make unique id to be one when the model is just being created
    if last_model== None:
        unique_id= "1"
    else:
        checker = True
        #get last unique id and set to 1 if it is None
        unique_id = last_model.unique_id if \
            last_model.unique_id != None else "1"
        while checker:
            #increment the unique id by 1
            new_unique_id = increment_unique_id(str(unique_id))
            _model= db.query(model).\
            filter(model.unique_id == new_unique_id).\
            filter(model.organization_id == organization_id).\
                first()
            if _model== None:
                checker = False
            unique_id = new_unique_id
            
    return unique_id

def increment_unique_id(unique_id):
    if unique_id.isalpha():
        last_character = unique_id[-1]
        new_last_character = chr(ord(last_character)+1)
        new_unique_id = append_new_character_to_unique_id(unique_id, 
            new_last_character)
    elif unique_id.isnumeric():
        new_last_character = int(unique_id)+1
        new_unique_id = new_last_character
    elif unique_id.isalnum():
        last_character = unique_id[-1]
        if last_character.isnumeric():
            new_last_character = (last_character)+1 if type(last_character) is int else int(last_character)+1
            new_unique_id = append_new_character_to_unique_id(unique_id, 
            new_last_character)
        else:
            new_last_character = chr(ord(last_character)+1)
            new_unique_id = append_new_character_to_unique_id(unique_id, 
                new_last_character)
    else:
        new_unique_id = math.floor(random.random() * 9)
            
    return new_unique_id

def append_new_character_to_unique_id(unique_id, new_last_character):
    unique_id = str(unique_id)
    new_last_character = str(new_last_character)
    return unique_id.replace(unique_id[-1], new_last_character)
    
