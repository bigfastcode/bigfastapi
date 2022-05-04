from uuid import uuid4
from typing import List
from sqlalchemy.orm import Session
from .auth_api import is_authenticated
from bigfastapi.db.database import get_db
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from bigfastapi.models import Landing_Page_models
from bigfastapi.schemas import Landing_page_schemas
from bigfastapi.files import upload_image, deleteFile, isFileExist
from fastapi import APIRouter, Depends, UploadFile, status, HTTPException, File, Request
from bigfastapi.utils.schema_form import as_form
import os
from fastapi.responses import FileResponse
from bigfastapi.utils.settings import TEMPLATE_FOLDER
from starlette.requests import Request

app = APIRouter(tags=["Landing Page"])


templates = Jinja2Templates(directory=TEMPLATE_FOLDER+"/landingpage")




@app.get("/landingpage/{filetype}/{folder}/{imageName}", status_code=200)
def s(filetype: str, imageName:str, folder:str, request: Request):
    s = imageFullpath(folder + "/" +imageName)
    return s




@app.post("/landingpage/create", status_code=201, response_model=Landing_page_schemas.landingPageResponse)
async def createlandingpage(request: Landing_page_schemas.landingPageCreate = Depends(Landing_page_schemas.landingPageCreate.as_form), db: Session = Depends(get_db),current_user = Depends(is_authenticated),
    company_logo: UploadFile = File(...), section_Three_image: UploadFile = File(...), Section_Four_image: UploadFile = File(...), section_One_image_link: UploadFile = File(...), Body_H3_logo_One: UploadFile = File(...), Body_H3_logo_Two: UploadFile = File(...),
    Body_H3_logo_Three: UploadFile = File(...), Body_H3_logo_Four: UploadFile = File(...),):
    if current_user.is_superuser:


        Bucket_name=uuid4().hex
        # check if landing pAGE name already exist
        if db.query(Landing_Page_models.LPage).filter(Landing_Page_models.LPage.landingPage_name == request.landingPage_name).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="landingPage_name already exist")
        
        if request.landingPage_name == "" or request.company_Name == "" or request.Body_H1 == "" or request.Body_paragraph == "" or request.Body_H3 == "" or request.Body_H3_logo_One_name == "" or request.Body_H3_logo_One_paragraph == "" or request.Body_H3_logo_Two_name == "" or request.Body_H3_logo_Two_paragraph == "" or request.Body_H3_logo_Three_name == "" or request.Body_H3_logo_Three_paragraph == "" or request.Body_H3_logo_Four_name == "" or request.Body_H3_logo_Four_paragraph == "" or request.section_Three_paragraph == "" or request.section_Three_sub_paragraph == "" or request.Footer_H3 == "" or request.Footer_H3_paragraph == "" or request.Footer_name_employee == "" or request.Name_job_description == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Home_link == "" or request.About_link == "" or request.faq_link == "" or request.contact_us_link == "" or request.login_link == "" or request.signup_link == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Home_link == "" or request.About_link == "" or request.faq_link == "":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please fill all fields")
            

        if company_logo:
            company_logo = "/" +Bucket_name + "/" + await upload_image(company_logo, db=db, bucket_name = Bucket_name)

        if section_Three_image:
            section_Three_image = "/" +Bucket_name + "/" + await upload_image(section_Three_image, db=db, bucket_name = Bucket_name)

        if Section_Four_image:
            Section_Four_image = "/" +Bucket_name + "/" + await upload_image(Section_Four_image, db=db, bucket_name = Bucket_name)

        if section_One_image_link:
            section_One_image_link = "/" +Bucket_name + "/" + await upload_image(section_One_image_link, db=db, bucket_name = Bucket_name)

        if Body_H3_logo_One:
            Body_H3_logo_One = "/" +Bucket_name + "/" + await upload_image(Body_H3_logo_One, db=db, bucket_name = Bucket_name)

        if Body_H3_logo_Two:
            Body_H3_logo_Two = "/" +Bucket_name + "/" + await upload_image(Body_H3_logo_Two, db=db, bucket_name = Bucket_name)

        if Body_H3_logo_Three:
            Body_H3_logo_Three =  "/" +Bucket_name + "/" + await upload_image(Body_H3_logo_Three, db=db, bucket_name = Bucket_name)
        if Body_H3_logo_Four:
            Body_H3_logo_Four = "/" +Bucket_name + "/" + await upload_image(Body_H3_logo_Four, db=db, bucket_name = Bucket_name)

        # create file path of images and add them to the data
        landingPage_data = Landing_Page_models.LPage(
            id = uuid4().hex,
            user_id =current_user.id,
            landingPage_name = request.landingPage_name,
            Bucket_name=Bucket_name,
            Body_H1=request.Body_H1,
            Body_paragraph=request.Body_paragraph,
            Body_H3=request.Body_H3,
            Body_H3_logo_One=Body_H3_logo_One,
            Body_H3_logo_One_name=request.Body_H3_logo_One_name,
            Body_H3_logo_One_paragraph=request.Body_H3_logo_One_paragraph,
            Body_H3_logo_Two=Body_H3_logo_Two,
            Body_H3_logo_Two_name=request.Body_H3_logo_Two_name,
            Body_H3_logo_Two_paragraph=request.Body_H3_logo_Two_paragraph,
            Body_H3_logo_Three=Body_H3_logo_Three,
            Body_H3_logo_Three_name=request.Body_H3_logo_Three_name,
            Body_H3_logo_Three_paragraph=request.Body_H3_logo_Three_paragraph,
            Body_H3_logo_Four=Body_H3_logo_Four,
            Body_H3_logo_Four_name=request.Body_H3_logo_Four_name,
            Body_H3_logo_Four_paragraph=request.Body_H3_logo_Four_paragraph,
            section_One_image_link=section_One_image_link,
            section_Three_paragraph=request.section_Three_paragraph,
            section_Three_sub_paragraph=request.section_Three_sub_paragraph,
            section_Three_image=section_Three_image,
            Footer_H3=request.Footer_H3,
            Footer_H3_paragraph=request.Footer_H3_paragraph,
            Footer_name_employee=request.Footer_name_employee,
            Name_job_description=request.Name_job_description,
            Footer_H2_text=request.Footer_H2_text,
            Footer_contact_address=request.Footer_contact_address,
            customer_care_email=request.customer_care_email,
            Home_link=request.Home_link,
            About_link=request.About_link,
            faq_link=request.faq_link,
            contact_us_link=request.contact_us_link,
            section_Four_image=Section_Four_image,  
            company_Name=request.company_Name,
            company_logo=company_logo,
            login_link=request.login_link,
            signup_link=request.signup_link,
  

        )
        db.add(landingPage_data)
        db.commit()
        db.refresh(landingPage_data)
        # return query of landing page id from the database
        return landingPage_data
        
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to perform this action")



# get all landing pages and use the fetch_all_landing_pages function to get the data
@app.get("/landingpage", status_code=status.HTTP_200_OK, response_model=List[Landing_page_schemas.landingPageResponse])
async def get_all_landing_pages(db: Session = Depends(get_db), current_user = Depends(is_authenticated)):
    # check the type of data is returned and return the data
    return db.query(Landing_Page_models.LPage).all() 


# get a single landing page and use the fetch_landing_page function to get the data
@app.get("/landingpage/{landingPage_name}", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_landing_page(request:Request,landingPage_name: str, db: Session = Depends(get_db)):

    # query the database using the landing page name
    landingPage_data = db.query(Landing_Page_models.LPage).filter(Landing_Page_models.LPage.landingPage_name ==landingPage_name).first()


    # check if the data is returned and return the data
    image_path = getUrlFullPath(request, "image")
    css_path = getUrlFullPath(request, "css")
    if landingPage_data:
        h = {
            "login_link":landingPage_data.login_link,
            "landingPage_name":landingPage_data.landingPage_name,
            "Body_H1":landingPage_data.Body_H1,
            "Body_paragraph":landingPage_data.Body_paragraph,
            "Body_H3":landingPage_data.Body_H3,
            "Body_H3_logo_One":image_path + landingPage_data.Body_H3_logo_One,
            "Body_H3_logo_One_name": landingPage_data.Body_H3_logo_One_name,
            "Body_H3_logo_One_paragraph":landingPage_data.Body_H3_logo_One_paragraph,
            "Body_H3_logo_Two":image_path +landingPage_data.Body_H3_logo_Two,
            "Body_H3_logo_Two_name":landingPage_data.Body_H3_logo_Two_name,
            "Body_H3_logo_Two_paragraph":landingPage_data.Body_H3_logo_Two_paragraph,
            "Body_H3_logo_Three":image_path +landingPage_data.Body_H3_logo_Three,
            "Body_H3_logo_Three_name":landingPage_data.Body_H3_logo_Three_name,
            "Body_H3_logo_Three_paragraph":landingPage_data.Body_H3_logo_Three_paragraph,
            "Body_H3_logo_Four":image_path +landingPage_data.Body_H3_logo_Four,
            "Body_H3_logo_Four_name":landingPage_data.Body_H3_logo_Four_name,
            "Body_H3_logo_Four_paragraph":landingPage_data.Body_H3_logo_Four_paragraph,
            "section_One_image_link":image_path + landingPage_data.section_One_image_link,
            "section_Three_paragraph":landingPage_data.section_Three_paragraph,
            "section_Three_sub_paragraph":landingPage_data.section_Three_sub_paragraph,
            "section_Three_image":image_path + landingPage_data.section_Three_image,
            "Footer_H3":landingPage_data.Footer_H3,
            "Footer_H3_paragraph":landingPage_data.Footer_H3_paragraph,
            "Footer_name_employee":landingPage_data.Footer_name_employee,
            "Name_job_description":landingPage_data.Name_job_description,
            "Footer_H2_text":landingPage_data.Footer_H2_text,
            "Footer_contact_address":landingPage_data.Footer_contact_address,
            "customer_care_email":landingPage_data.customer_care_email,
            "Home_link":landingPage_data.Home_link,
            "About_link":landingPage_data.About_link,
            "faq_link":landingPage_data.faq_link,
            "contact_us_link":landingPage_data.contact_us_link,
            "section_Four_image":image_path + landingPage_data.section_Four_image,
            "company_Name":landingPage_data.company_Name,
            "company_logo":image_path + landingPage_data.company_logo,
            "css_file": css_path + "/css/landingpage.css",
            "signup_link":landingPage_data.signup_link,
        }
        return templates.TemplateResponse("landingpage.html", {"request": request, "h": h})
    else:
        raise HTTPException(status_code=404, detail="Landing page not found")



# update a single landing page and use the update_landing_page function to update the data
@app.put("/landingpage/{landingPage_Name}", status_code=status.HTTP_200_OK, response_model=Landing_page_schemas.landingPageResponse)
async def update_landing_page(landingPage_Name: str,request: Landing_page_schemas.landingPageCreate = Depends(Landing_page_schemas.landingPageCreate.as_form), db: Session = Depends(get_db), current_user = Depends(is_authenticated),
    company_logo: UploadFile = File(...), section_Three_image: UploadFile = File(...), Section_Four_image: UploadFile = File(...), section_One_image_link: UploadFile = File(...), Body_H3_logo_One: UploadFile = File(...), Body_H3_logo_Two: UploadFile = File(...),
    Body_H3_logo_Three: UploadFile = File(...), Body_H3_logo_Four: UploadFile = File(...),):


    update_landing_page_data= db.query(Landing_Page_models.LPage).filter(Landing_Page_models.LPage.landingPage_name == landingPage_Name).first()

    if current_user.is_superuser:

        if update_landing_page_data == None:
            raise HTTPException(status_code=404, detail="Landing page does not exist")

        if update_landing_page_data.landingPage_name != request.landingPage_name:
            raise HTTPException(status_code=400, detail="Landing page name cannot be changed")

        if update_landing_page_data.company_Name != request.company_Name:
            update_landing_page_data.company_Name = request.company_Name
        
        if update_landing_page_data.Body_H1 != request.Body_H1:
            update_landing_page_data.Body_H1 = request.Body_H1
        
        if update_landing_page_data.Body_paragraph != request.Body_paragraph:
            update_landing_page_data.Body_paragraph = request.Body_paragraph

        if update_landing_page_data.Body_H3 != request.Body_H3:
            update_landing_page_data.Body_H3 = request.Body_H3
        
        if update_landing_page_data.Body_H3_logo_One_name != request.Body_H3_logo_One_name:
            update_landing_page_data.Body_H3_logo_One_name = request.Body_H3_logo_One_name
        
        if update_landing_page_data.Body_H3_logo_One_paragraph != request.Body_H3_logo_One_paragraph:
            update_landing_page_data.Body_H3_logo_One_paragraph = request.Body_H3_logo_One_paragraph
        
        if update_landing_page_data.Body_H3_logo_Two_name != request.Body_H3_logo_Two_name:
            update_landing_page_data.Body_H3_logo_Two_name = request.Body_H3_logo_Two_name
        
        if update_landing_page_data.Body_H3_logo_Two_paragraph != request.Body_H3_logo_Two_paragraph:
            update_landing_page_data.Body_H3_logo_Two_paragraph = request.Body_H3_logo_Two_paragraph
        
        if update_landing_page_data.Body_H3_logo_Three_name != request.Body_H3_logo_Three_name:
            update_landing_page_data.Body_H3_logo_Three_name = request.Body_H3_logo_Three_name
        
        if update_landing_page_data.Body_H3_logo_Three_paragraph != request.Body_H3_logo_Three_paragraph:
            update_landing_page_data.Body_H3_logo_Three_paragraph = request.Body_H3_logo_Three_paragraph
        
        if update_landing_page_data.Body_H3_logo_Four_name != request.Body_H3_logo_Four_name:
            update_landing_page_data.Body_H3_logo_Four_name = request.Body_H3_logo_Four_name
        
        if update_landing_page_data.Body_H3_logo_Four_paragraph != request.Body_H3_logo_Four_paragraph:
            update_landing_page_data.Body_H3_logo_Four_paragraph = request.Body_H3_logo_Four_paragraph
        
        if update_landing_page_data.section_Three_paragraph != request.section_Three_paragraph:
            update_landing_page_data.section_Three_paragraph = request.section_Three_paragraph
        
        if update_landing_page_data.section_Three_sub_paragraph != request.section_Three_sub_paragraph:
            update_landing_page_data.section_Three_sub_paragraph = request.section_Three_sub_paragraph

        if update_landing_page_data.Footer_H3 != request.Footer_H3:
            update_landing_page_data.Footer_H3 = request.Footer_H3
        
        if update_landing_page_data.Footer_H3_paragraph != request.Footer_H3_paragraph:
            update_landing_page_data.Footer_H3_paragraph = request.Footer_H3_paragraph
        
        if update_landing_page_data.Footer_name_employee != request.Footer_name_employee:
            update_landing_page_data.Footer_name_employee = request.Footer_name_employee
        
        if update_landing_page_data.Name_job_description != request.Name_job_description:   
            update_landing_page_data.Name_job_description = request.Name_job_description
        
        if update_landing_page_data.Footer_H2_text != request.Footer_H2_text:
            update_landing_page_data.Footer_H2_text = request.Footer_H2_text
        
        if update_landing_page_data.login_link != request.login_link:
            update_landing_page_data.login_link = request.login_link
        
        if update_landing_page_data.signup_link != request.signup_link:
            update_landing_page_data.signup_link = request.signup_link
        
        if update_landing_page_data.Home_link != request.Home_link:
            update_landing_page_data.Home_link = request.Home_link
        
        if update_landing_page_data.About_link != request.About_link:
            update_landing_page_data.About_link = request.About_link
        
        
        if update_landing_page_data.faq_link != request.faq_link:
            update_landing_page_data.faq_link = request.faq_link
        
        if update_landing_page_data.contact_us_link != request.contact_us_link:
            update_landing_page_data.contact_us_link = request.contact_us_link
        
        if update_landing_page_data.Footer_contact_address != request.Footer_contact_address:
            update_landing_page_data.Footer_contact_address = request.Footer_contact_address

        if update_landing_page_data.customer_care_email != request.customer_care_email:
            update_landing_page_data.customer_care_email = request.customer_care_email
        
        
    if isFileExist(company_logo) != True:
        company_logo1 = update_landing_page_data.company_logo
        if deleteFile(company_logo1):
            company_logo = await upload_image(company_logo, db=db, bucket_name = update_landing_page_data.Bucket_name)
            update_landing_page_data.company_logo ="/"+ update_landing_page_data.Bucket_name + "/" + company_logo
    
    if isFileExist(section_One_image_link) != True:
        section_One_image_link1 = update_landing_page_data.section_One_image_link
        if deleteFile(section_One_image_link1):
            section_One_image_link = section_One_image_link
            section_One_image_link = await upload_image(section_One_image_link, db=db, bucket_name = update_landing_page_data.Bucket_name)
            update_landing_page_data.section_One_image_link ="/"+ update_landing_page_data.Bucket_name + "/" + section_One_image_link
    
    if isFileExist(Body_H3_logo_One) != True:
        Body_H3_logo_One1 = update_landing_page_data.Body_H3_logo_One
        if deleteFile(Body_H3_logo_One1):
            Body_H3_logo_One = Body_H3_logo_One
            Body_H3_logo_One = await upload_image(Body_H3_logo_One, db=db, bucket_name = update_landing_page_data.Bucket_name)
            update_landing_page_data.Body_H3_logo_One ="/"+ update_landing_page_data.Bucket_name + "/" + Body_H3_logo_One
    
    if isFileExist(Body_H3_logo_Two) != True:
        Body_H3_logo_Two1 = update_landing_page_data.Body_H3_logo_Two
        if deleteFile(Body_H3_logo_Two1):
            Body_H3_logo_Two = Body_H3_logo_Two
            Body_H3_logo_Two = await upload_image(Body_H3_logo_Two, db=db, bucket_name = update_landing_page_data.Bucket_name)
            update_landing_page_data.Body_H3_logo_Two ="/"+ update_landing_page_data.Bucket_name + "/" + Body_H3_logo_Two
    
    if isFileExist(Body_H3_logo_Three) != True:
        Body_H3_logo_Three1 = update_landing_page_data.Body_H3_logo_Three
        if deleteFile(Body_H3_logo_Three1):
            Body_H3_logo_Three = Body_H3_logo_Three
            Body_H3_logo_Three = await upload_image(Body_H3_logo_Three, db=db, bucket_name = update_landing_page_data.Bucket_name)
            update_landing_page_data.Body_H3_logo_Three ="/"+ update_landing_page_data.Bucket_name + "/" + Body_H3_logo_Three
    
    if isFileExist(Body_H3_logo_Four) != True:
        Body_H3_logo_Four1 = update_landing_page_data.Body_H3_logo_Four
        if deleteFile(Body_H3_logo_Four1):
            Body_H3_logo_Four = Body_H3_logo_Four
            Body_H3_logo_Four = await upload_image(Body_H3_logo_Four, db=db, bucket_name = update_landing_page_data.Bucket_name)
            update_landing_page_data.Body_H3_logo_Four ="/"+ update_landing_page_data.Bucket_name + "/" + Body_H3_logo_Four
    
    if isFileExist(section_Three_image) != True:
        section_Three_image1 = update_landing_page_data.section_Three_image
        if deleteFile(section_Three_image1):
            section_Three_image = section_Three_image
            section_Three_image = await upload_image(section_Three_image, db=db, bucket_name = update_landing_page_data.Bucket_name)
            update_landing_page_data.section_Three_image ="/"+ update_landing_page_data.Bucket_name + "/" + section_Three_image
    
    if isFileExist(Section_Four_image) != True:
        Section_Four_image1 = update_landing_page_data.section_Four_image
        if deleteFile(Section_Four_image1):
            Section_Four_image = Section_Four_image
            section_Four_image = await upload_image(Section_Four_image, db=db, bucket_name = update_landing_page_data.Bucket_name)
            update_landing_page_data.section_Four_image ="/"+ update_landing_page_data.Bucket_name + "/" + section_Four_image


    db.commit()
    db.refresh(update_landing_page_data)
    return update_landing_page_data


# delete landing page data
@app.delete("/landingpage/{landingPage_name}",status_code=200, tags=["landingPage"])
async def delete_landingPage(landingPage_name: str, current_user = Depends(is_authenticated), db: Session = Depends(get_db)):
    # query for the landing page data
    if current_user.is_superuser:
        # get the data from the database
        landingPage_data = db.query(Landing_Page_models.LPage).filter(Landing_Page_models.LPage.landingPage_name == landingPage_name).first()
        if landingPage_data:
            # delete the data from the database
            deleteimage=[landingPage_data.company_logo,landingPage_data.section_One_image_link,landingPage_data.Body_H3_logo_One,landingPage_data.Body_H3_logo_Two,landingPage_data.Body_H3_logo_Three,landingPage_data.Body_H3_logo_Four,landingPage_data.section_Three_image,landingPage_data.section_Four_image]
            for i in deleteimage:
                if deleteFile(i):
                    pass

            db.delete(landingPage_data)
            db.commit()
            return {"message": "Data deleted successfully."}
            
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': "Data could not be found. Please try again."})
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'error': "You are not authorized to perform this action."})




# Retrieve landing page images
def imageFullpath(imagepath):
    root_location = os.path.abspath("filestorage")
    image_location = os.path.join(root_location, imagepath)
    return FileResponse(image_location)


# get host part
def getUrlFullPath(request: Request, filetype: str):
    hostname = request.headers.get('host')
    image_path = request.url.scheme +"://" + hostname + f"/landingpage/{filetype}"
    return image_path