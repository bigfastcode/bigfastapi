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


# Endpoint to open index.html
@app.get("/landingpage")
async def landing_page_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint to get landing page images
@app.get("/landingpage/{filetype}/{folder}/{imageName}", status_code=200)
def path(filetype: str, imageName:str, folder:str, request: Request):
    fullpath = imageFullpath(folder + "/" +imageName)
    return fullpath



# Endpoint to create landing page
@app.post("/landingpage/create", status_code=201, response_model=Landing_page_schemas.landingPageResponse)
async def createlandingpage(request: Landing_page_schemas.landingPageCreate = Depends(Landing_page_schemas.landingPageCreate.as_form), db: Session = Depends(get_db),current_user = Depends(is_authenticated),
    company_logo: UploadFile = File(...), section_Three_image: UploadFile = File(...), Section_Four_image: UploadFile = File(...), section_One_image_link: UploadFile = File(...), Body_H3_logo_One: UploadFile = File(...), Body_H3_logo_Two: UploadFile = File(...),
    Body_H3_logo_Three: UploadFile = File(...), Body_H3_logo_Four: UploadFile = File(...),):

    # checks if user is a superuser 
    if current_user.is_superuser:

        # generates bucket name
        Bucket_name=uuid4().hex

        # check if landing pAGE name already exist
        if db.query(Landing_Page_models.LPage).filter(Landing_Page_models.LPage.landingPage_name == request.landingPage_name).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="landingPage_name already exist")
        
        # check if all form fields are filled
        if request.landingPage_name == "" or request.company_Name == "" or request.Body_H1 == "" or request.Body_paragraph == "" or request.Body_H3 == "" or request.Body_H3_logo_One_name == "" or request.Body_H3_logo_One_paragraph == "" or request.Body_H3_logo_Two_name == "" or request.Body_H3_logo_Two_paragraph == "" or request.Body_H3_logo_Three_name == "" or request.Body_H3_logo_Three_paragraph == "" or request.Body_H3_logo_Four_name == "" or request.Body_H3_logo_Four_paragraph == "" or request.section_Three_paragraph == "" or request.section_Three_sub_paragraph == "" or request.Footer_H3 == "" or request.Footer_H3_paragraph == "" or request.Footer_name_employee == "" or request.Name_job_description == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Home_link == "" or request.About_link == "" or request.faq_link == "" or request.contact_us_link == "" or request.login_link == "" or request.signup_link == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Footer_H2_text == "" or request.Footer_contact_address == "" or request.customer_care_email == "" or request.Home_link == "" or request.About_link == "" or request.faq_link == "":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please fill all fields")
            
        # check if company logo is uploaded else raise error
        if company_logo:
            company_logo = "/" +Bucket_name + "/" + await upload_image(company_logo, db=db, bucket_name = Bucket_name)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload company logo")

        # check if section three image is uploaded else raise error
        if section_Three_image:
            section_Three_image = "/" +Bucket_name + "/" + await upload_image(section_Three_image, db=db, bucket_name = Bucket_name)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload section_Three_image")

        # check if section four image is uploaded else raise error
        if Section_Four_image:
            Section_Four_image = "/" +Bucket_name + "/" + await upload_image(Section_Four_image, db=db, bucket_name = Bucket_name)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload Section_Four_image")

        # check if section one image link is uploaded else raise error
        if section_One_image_link:
            section_One_image_link = "/" +Bucket_name + "/" + await upload_image(section_One_image_link, db=db, bucket_name = Bucket_name)

        # check if body h3 logo one is uploaded else raise error
        if Body_H3_logo_One:
            Body_H3_logo_One = "/" +Bucket_name + "/" + await upload_image(Body_H3_logo_One, db=db, bucket_name = Bucket_name)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload Body_H3_logo_One")

        # check if body h3 logo two is uploaded else raise error
        if Body_H3_logo_Two:
            Body_H3_logo_Two = "/" +Bucket_name + "/" + await upload_image(Body_H3_logo_Two, db=db, bucket_name = Bucket_name)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload Body_H3_logo_Two")

        # check if body h3 logo three is uploaded else raise error
        if Body_H3_logo_Three:
            Body_H3_logo_Three =  "/" +Bucket_name + "/" + await upload_image(Body_H3_logo_Three, db=db, bucket_name = Bucket_name)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload Body_H3_logo_Three")

        # check if body h3 logo four is uploaded else raise error
        if Body_H3_logo_Four:
            Body_H3_logo_Four = "/" +Bucket_name + "/" + await upload_image(Body_H3_logo_Four, db=db, bucket_name = Bucket_name)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload Body_H3_logo_Four")

        # map schema to landing page model
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
        
        # Attempt to save the new landing page and return the result to the client. 
        try:
            # try to save data to database
            db.add(landingPage_data)
            db.commit()
            db.refresh(landingPage_data)
            # return query of landing page id from the database
            return landingPage_data

        #  Throw an error if the data cannot be saved
        except Exception as e:
            # if there is an error, return the error message
            print(e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error saving data")

    # User is not a superuser 
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to perform this action")



# Endpoint to get all landing pages and use the fetch_all_landing_pages function to get the data
@app.get("/landingpage/all", status_code=status.HTTP_200_OK, response_model=List[Landing_page_schemas.landingPageResponse])
async def get_all_landing_pages(db: Session = Depends(get_db), current_user = Depends(is_authenticated)):

    # check if user is a superuser
    if current_user.is_superuser:

        # attempt to get all landing pages from the database
        try:
            landingPages = db.query(Landing_Page_models.LPage).all()

            return  landingPages
        
        # return error if landing pages cannot be fetched
        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error fetching data")


# Endpoint to get a single landing page and use the fetch_landing_page function to get the data
@app.get("/landingpage/{landingPage_name}", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_landing_page(request:Request,landingPage_name: str, db: Session = Depends(get_db)):

    # query the database using the landing page name
    landingPage_data = db.query(Landing_Page_models.LPage).filter(Landing_Page_models.LPage.landingPage_name ==landingPage_name).first()


    # check if the data is returned and return the data
    image_path = getUrlFullPath(request, "image")
    # css_path = getUrlFullPath(request, "css")

    # check if landing page data is returned and extract the data
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
            # "css_file": css_path + "/css/landingpage.css",
            "signup_link":landingPage_data.signup_link,
        }
        return templates.TemplateResponse("landingpage.html", {"request": request, "h": h})
    
    # if no data is returned, throw an error
    else:
        raise HTTPException(status_code=404, detail="Landing page not found")



# Endpoint to update a single landing page and use the update_landing_page function to update the data
@app.put("/landingpage/{landingPage_Name}", status_code=status.HTTP_200_OK, response_model=Landing_page_schemas.landingPageResponse)
async def update_landing_page(landingPage_Name: str,request: Landing_page_schemas.landingPageCreate = Depends(Landing_page_schemas.landingPageCreate.as_form), db: Session = Depends(get_db), current_user = Depends(is_authenticated),
    company_logo: UploadFile = File(...), section_Three_image: UploadFile = File(...), Section_Four_image: UploadFile = File(...), section_One_image_link: UploadFile = File(...), Body_H3_logo_One: UploadFile = File(...), Body_H3_logo_Two: UploadFile = File(...),
    Body_H3_logo_Three: UploadFile = File(...), Body_H3_logo_Four: UploadFile = File(...),):

    # check if the user is superuser
    if current_user.is_superuser:

        # query the database using the landing page name
        update_landing_page_data= db.query(Landing_Page_models.LPage).filter(Landing_Page_models.LPage.landingPage_name == landingPage_Name).first()

        # check if update landing page does not exist, throw an error
        if update_landing_page_data == None:
            raise HTTPException(status_code=404, detail="Landing page does not exist")

        # check if the landing page name is not the same as the landing page name in the database, throw an error
        if update_landing_page_data.landingPage_name != request.landingPage_name:
            raise HTTPException(status_code=400, detail="Landing page name cannot be changed")

        #  check if landing page company name is not the same, update the landing page company name
        if update_landing_page_data.company_Name != request.company_Name:
            update_landing_page_data.company_Name = request.company_Name
        
        # check if landing page body H1 is not the same, update the landing page body H1
        if update_landing_page_data.Body_H1 != request.Body_H1:
            update_landing_page_data.Body_H1 = request.Body_H1
        
        # check if landing page body paragraph is not the same, update the landing page body paragraph
        if update_landing_page_data.Body_paragraph != request.Body_paragraph:
            update_landing_page_data.Body_paragraph = request.Body_paragraph

        # check if landing page body H3 logo one name is not the same, update the landing page body H3 logo one name
        if update_landing_page_data.Body_H3 != request.Body_H3:
            update_landing_page_data.Body_H3 = request.Body_H3
        
        # check if landing page body H3 logo one name is not the same, update the landing page body H3 logo one name
        if update_landing_page_data.Body_H3_logo_One_name != request.Body_H3_logo_One_name:
            update_landing_page_data.Body_H3_logo_One_name = request.Body_H3_logo_One_name
        
        # check if landing page body H3 logo one paragraph is not the same, update the landing page body H3 logo one paragraph
        if update_landing_page_data.Body_H3_logo_One_paragraph != request.Body_H3_logo_One_paragraph:
            update_landing_page_data.Body_H3_logo_One_paragraph = request.Body_H3_logo_One_paragraph
        
        # check if landing page body H3 logo two name is not the same, update the landing page body H3 logo two name
        if update_landing_page_data.Body_H3_logo_Two_name != request.Body_H3_logo_Two_name:
            update_landing_page_data.Body_H3_logo_Two_name = request.Body_H3_logo_Two_name
        
        # check if landing page body H3 logo two paragraph is not the same, update the landing page body H3 two paragraph
        if update_landing_page_data.Body_H3_logo_Two_paragraph != request.Body_H3_logo_Two_paragraph:
            update_landing_page_data.Body_H3_logo_Two_paragraph = request.Body_H3_logo_Two_paragraph
        
        # chcek if landing page body H3 logo three name is not the same, update the landing page body H3 logo three name
        if update_landing_page_data.Body_H3_logo_Three_name != request.Body_H3_logo_Three_name:
            update_landing_page_data.Body_H3_logo_Three_name = request.Body_H3_logo_Three_name
        
        # check if landing page body H3 logo three paragraph is not the same, update the landing page body H3 logo three paragraph
        if update_landing_page_data.Body_H3_logo_Three_paragraph != request.Body_H3_logo_Three_paragraph:
            update_landing_page_data.Body_H3_logo_Three_paragraph = request.Body_H3_logo_Three_paragraph
        
        # check if landing page body H3 logo four name is not the same, update the landing page body H3 logo four name
        if update_landing_page_data.Body_H3_logo_Four_name != request.Body_H3_logo_Four_name:
            update_landing_page_data.Body_H3_logo_Four_name = request.Body_H3_logo_Four_name
        
        # check if landing page body H3 logo four paragraph is not the same, update the landing page body H3 logo four paragraph
        if update_landing_page_data.Body_H3_logo_Four_paragraph != request.Body_H3_logo_Four_paragraph:
            update_landing_page_data.Body_H3_logo_Four_paragraph = request.Body_H3_logo_Four_paragraph
        
        # check if landing page section three paragraph is not the same, update the landing page section three paragraph
        if update_landing_page_data.section_Three_paragraph != request.section_Three_paragraph:
            update_landing_page_data.section_Three_paragraph = request.section_Three_paragraph
        
        # check if landing page section three sub paragraph is not the same, update the landing page section three sub paragraph
        if update_landing_page_data.section_Three_sub_paragraph != request.section_Three_sub_paragraph:
            update_landing_page_data.section_Three_sub_paragraph = request.section_Three_sub_paragraph

        # check if landing page footer H3 is not the same, update the landing page footer H3
        if update_landing_page_data.Footer_H3 != request.Footer_H3:
            update_landing_page_data.Footer_H3 = request.Footer_H3
        
        # check if landing page footer paragraph is not the same, update the landing page footer paragraph
        if update_landing_page_data.Footer_H3_paragraph != request.Footer_H3_paragraph:
            update_landing_page_data.Footer_H3_paragraph = request.Footer_H3_paragraph
        
        # check if landing page footer name employee is not the same, update the landing page footer name employee
        if update_landing_page_data.Footer_name_employee != request.Footer_name_employee:
            update_landing_page_data.Footer_name_employee = request.Footer_name_employee
        
        # check if landing page positon of emplaoyee is not the same, update the landing page positon of emplaoyee
        if update_landing_page_data.Name_job_description != request.Name_job_description:   
            update_landing_page_data.Name_job_description = request.Name_job_description
        
        # check if landing page footer H2 text is not the same, update the landing page footer H2 text
        if update_landing_page_data.Footer_H2_text != request.Footer_H2_text:
            update_landing_page_data.Footer_H2_text = request.Footer_H2_text
        
        # check if login link is not the same, update the login link
        if update_landing_page_data.login_link != request.login_link:
            update_landing_page_data.login_link = request.login_link
        
        # check if signup link is not the same, update the signup link
        if update_landing_page_data.signup_link != request.signup_link:
            update_landing_page_data.signup_link = request.signup_link
        
        # check if home link is not the same, update the home link
        if update_landing_page_data.Home_link != request.Home_link:
            update_landing_page_data.Home_link = request.Home_link
        
        # check if about link is not the same, update the about link
        if update_landing_page_data.About_link != request.About_link:
            update_landing_page_data.About_link = request.About_link
        
        # check if faq link is not the same, update the faq link
        if update_landing_page_data.faq_link != request.faq_link:
            update_landing_page_data.faq_link = request.faq_link
        
        # check if contact link is not the same, update the contact link
        if update_landing_page_data.contact_us_link != request.contact_us_link:
            update_landing_page_data.contact_us_link = request.contact_us_link
        
        # check if contact address is not the same, update the contact address
        if update_landing_page_data.Footer_contact_address != request.Footer_contact_address:
            update_landing_page_data.Footer_contact_address = request.Footer_contact_address

        #  check if customer care mail is not the same, update the customer care mail
        if update_landing_page_data.customer_care_email != request.customer_care_email:
            update_landing_page_data.customer_care_email = request.customer_care_email
        
        # check company logo is uploaded, update the company logo
        if isFileExist(company_logo) != True:
            company_logo1 = update_landing_page_data.company_logo
            if deleteFile(company_logo1):
                company_logo = await upload_image(company_logo, db=db, bucket_name = update_landing_page_data.Bucket_name)
                update_landing_page_data.company_logo ="/"+ update_landing_page_data.Bucket_name + "/" + company_logo
        
        # check if section one image is uploaded, update the section one image
        if isFileExist(section_One_image_link) != True:
            section_One_image_link1 = update_landing_page_data.section_One_image_link
            if deleteFile(section_One_image_link1):
                section_One_image_link = section_One_image_link
                section_One_image_link = await upload_image(section_One_image_link, db=db, bucket_name = update_landing_page_data.Bucket_name)
                update_landing_page_data.section_One_image_link ="/"+ update_landing_page_data.Bucket_name + "/" + section_One_image_link
        
        # check if body h3 logo one image is uploaded, update the body h3 logo one image
        if isFileExist(Body_H3_logo_One) != True:
            Body_H3_logo_One1 = update_landing_page_data.Body_H3_logo_One
            if deleteFile(Body_H3_logo_One1):
                Body_H3_logo_One = Body_H3_logo_One
                Body_H3_logo_One = await upload_image(Body_H3_logo_One, db=db, bucket_name = update_landing_page_data.Bucket_name)
                update_landing_page_data.Body_H3_logo_One ="/"+ update_landing_page_data.Bucket_name + "/" + Body_H3_logo_One
        
        # check if body h3 logo two image is uploaded, update the body h3 logo two image
        if isFileExist(Body_H3_logo_Two) != True:
            Body_H3_logo_Two1 = update_landing_page_data.Body_H3_logo_Two
            if deleteFile(Body_H3_logo_Two1):
                Body_H3_logo_Two = Body_H3_logo_Two
                Body_H3_logo_Two = await upload_image(Body_H3_logo_Two, db=db, bucket_name = update_landing_page_data.Bucket_name)
                update_landing_page_data.Body_H3_logo_Two ="/"+ update_landing_page_data.Bucket_name + "/" + Body_H3_logo_Two
        
        # check if body h3 logo three image is uploaded, update the body h3 logo three image
        if isFileExist(Body_H3_logo_Three) != True:
            Body_H3_logo_Three1 = update_landing_page_data.Body_H3_logo_Three
            if deleteFile(Body_H3_logo_Three1):
                Body_H3_logo_Three = Body_H3_logo_Three
                Body_H3_logo_Three = await upload_image(Body_H3_logo_Three, db=db, bucket_name = update_landing_page_data.Bucket_name)
                update_landing_page_data.Body_H3_logo_Three ="/"+ update_landing_page_data.Bucket_name + "/" + Body_H3_logo_Three
        
        # check if body h3 logo four image is uploaded, update the body h3 logo four image
        if isFileExist(Body_H3_logo_Four) != True:
            Body_H3_logo_Four1 = update_landing_page_data.Body_H3_logo_Four
            if deleteFile(Body_H3_logo_Four1):
                Body_H3_logo_Four = Body_H3_logo_Four
                Body_H3_logo_Four = await upload_image(Body_H3_logo_Four, db=db, bucket_name = update_landing_page_data.Bucket_name)
                update_landing_page_data.Body_H3_logo_Four ="/"+ update_landing_page_data.Bucket_name + "/" + Body_H3_logo_Four
        
        # check if section three image is uploaded, update the section three image
        if isFileExist(section_Three_image) != True:
            section_Three_image1 = update_landing_page_data.section_Three_image
            if deleteFile(section_Three_image1):
                section_Three_image = section_Three_image
                section_Three_image = await upload_image(section_Three_image, db=db, bucket_name = update_landing_page_data.Bucket_name)
                update_landing_page_data.section_Three_image ="/"+ update_landing_page_data.Bucket_name + "/" + section_Three_image
        
        # check if section four image is uploaded, update the section four image
        if isFileExist(Section_Four_image) != True:
            Section_Four_image1 = update_landing_page_data.section_Four_image
            if deleteFile(Section_Four_image1):
                Section_Four_image = Section_Four_image
                section_Four_image = await upload_image(Section_Four_image, db=db, bucket_name = update_landing_page_data.Bucket_name)
                update_landing_page_data.section_Four_image ="/"+ update_landing_page_data.Bucket_name + "/" + section_Four_image

        # attempt to update the landing page data
        try:
            db.commit()
            db.refresh(update_landing_page_data)
            return update_landing_page_data
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="An error occured while updating the landing page data")

    else:
        raise HTTPException(status_code=404, detail="Landing page not found")



# Endpoint to delete landing page data
@app.delete("/landingpage/{landingPage_name}",status_code=200, tags=["landingPage"])
async def delete_landingPage(landingPage_name: str, current_user = Depends(is_authenticated), db: Session = Depends(get_db)):
   
    # check if user is a super user
    if current_user.is_superuser:
         # query for the landing page data
        landingPage_data = db.query(Landing_Page_models.LPage).filter(Landing_Page_models.LPage.landingPage_name == landingPage_name).first()

        # check if landing page data is found
        if landingPage_data:

            # delete the images from the bucket
            deleteimage=[landingPage_data.company_logo,landingPage_data.section_One_image_link,landingPage_data.Body_H3_logo_One,landingPage_data.Body_H3_logo_Two,landingPage_data.Body_H3_logo_Three,landingPage_data.Body_H3_logo_Four,landingPage_data.section_Three_image,landingPage_data.section_Four_image]
            for i in deleteimage:
                if deleteFile(i):
                    pass
                else:
                    pass
            
            # delete the landing page data
            db.delete(landingPage_data)
            db.commit()
            return {"message": "Data deleted successfully."}

        # landing page data not found 
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': "Data could not be found. Please try again."})
    
    # user is not a super user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'error': "You are not authorized to perform this action."})




# Function to retrieve landing page images
def imageFullpath(imagepath):
    root_location = os.path.abspath("filestorage")
    image_location = os.path.join(root_location, imagepath)
    return FileResponse(image_location)


# Function to get host path to landing page images
def getUrlFullPath(request: Request, filetype: str):
    hostname = request.headers.get('host')
    image_path = request.url.scheme +"://" + hostname + f"/landingpage/{filetype}"
    return image_path