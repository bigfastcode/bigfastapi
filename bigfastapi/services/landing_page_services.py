import json
from uuid import uuid4
from typing import Dict, List
from sqlalchemy.orm import Session
from bigfastapi.auth_api import is_authenticated
from bigfastapi.db.database import get_db
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from bigfastapi.schemas import landing_page_schemas
import os
from fastapi.responses import FileResponse
from bigfastapi.utils.settings import LANDING_PAGE_FOLDER, LANDING_PAGE_FORM_PATH
from bigfastapi.files import upload_image, deleteFile, isFileExist
from starlette.requests import Request
import pkg_resources
from bigfastapi.models import landing_page_models
from fastapi import APIRouter, Depends, UploadFile, status, HTTPException, File, Request


async def create_landing_page(landing_page_name: str, bucket_name:str, db: Session=Depends(get_db), current_user = Depends(is_authenticated)):

  landing_page_data = landing_page_models.LandingPage(
    id = uuid4().hex,
    bucket_name=bucket_name,
    user_id= current_user,
    landing_page_name=landing_page_name, 
    )

  try:
      # try to save data to database
      db.add(landing_page_data)
      db.commit()
      db.refresh(landing_page_data)
      # return query of landing page id from the database
      return landing_page_data

  #  Throw an error if the data cannot be saved
  except Exception as e:
      # if there is an error, return the error message
      print(e)
      raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST, detail="Error saving data")



# populates data to the landing page other table
async def add_other_info(landing_page_instance: str, data:Dict, db: Session = Depends(get_db)):

  data = data.items()
  for other_info in data:
      other_info_instance = landing_page_models.OtherInfo(
        id=uuid4().hex,
        landing_page_id = landing_page_instance.id,
        key = other_info[0],
        value = other_info[1]
      )
      db.add(other_info_instance)
      db.commit()
      db.refresh(other_info_instance)
      setattr(landing_page_instance.other_info, 'other_info', [other_info_instance])
  return landing_page_instance



