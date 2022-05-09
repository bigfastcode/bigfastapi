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
    """
    This endpont will return landing page index.html
    """
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint to get landing page images
@app.get("/landingpage/{filetype}/{folder}/{image_name}", status_code=200)
def path(filetype: str, image_name:str, folder:str, request: Request):
    """
    This endpoint is used in the landing page html to fetch images 
    """
    fullpath = image_fullpath(folder + "/" +image_name)
    return fullpath



# Endpoint to create landing page
@app.post("/landingpage/create", status_code=201, response_model=Landing_page_schemas.landingPageResponse)
async def createlandingpage(request: Landing_page_schemas.landingPageCreate = Depends(Landing_page_schemas.landingPageCreate.as_form), db: Session = Depends(get_db),current_user = Depends(is_authenticated),
    company_logo: UploadFile = File(...), 
    section_three_image: UploadFile = File(...), 
    section_four_image: UploadFile = File(...), 
    section_one_image_link: UploadFile = File(...), 
    body_h3_logo_one: UploadFile = File(...), 
    body_h3_logo_two: UploadFile = File(...),
    body_h3_logo_three: UploadFile = File(...), 
    body_h3_logo_four: UploadFile = File(...),):
    """
    This endpoint is used to create a landing page
    It takes in the following parameters:
        landing_page_name: This is the name of the landing page and will be used to view the landing page html
        company_name: This is the name of the company
        Home_link: This is the link to the home page. This will be used to view the landing page html
        About_link: This is the link to the about page. This will be used to view the about page html
        Contact_link: This is the link to the contact page. This will be used to view the contact page html
        company_logo: This is the logo of the company. This will be used to to place  the company logo in the landing page html
        section_Three_image: This is the image of the section three. This will be used to to place  the section three image in the landing page html
        Section_Four_image: This is the image of the section four. This will be used to to place  the section four image in the landing page html
        section_One_image_link: This is the link to the section one image. This will be used to to place  the section one image in the landing page html
        Body_H3_logo_One: This is the image of the body h3 logo one. This will be used to to place  the body h3 logo one in the landing page html
        body_h3_logo_two: This is the image of the body h3 logo two. This will be used to to place  the body h3 logo two in the landing page html
        Body_H3_logo_Three: This is the image of the body h3 logo three. This will be used to to place  the body h3 logo three in the landing page html
        Body_H3_logo_Four: This is the image of the body h3 logo four. This will be used to to place  the body h3 logo four in the landing page html
        body_h1: This is the body h1 text. This will be used to to place  the body h1 text in the landing page html
        body_paragraph: This is the body paragraph text. This will be used to to place  the body paragraph text in the landing page html
        Body_H3: This is the body h3 text. This will be used to to place  the body h3 text in the landing page html
        body_h3_logo_one_name: This is the name of the body h3 logo one. This will be used to to place  the body h3 logo one name in the landing page html
        Body_H3_logo_One_paragraph: This is the body h3 logo one paragraph text. This will be used to to place  the body h3 logo one paragraph text in the landing page html
        body_h3_logo_two_name: This is the name of the body h3 logo two. This will be used to to place  the body h3 logo two name in the landing page html
        body_h3_logo_two_paragraph: This is the body h3 logo two paragraph text. This will be used to to place  the body h3 logo two paragraph text in the landing page html
        body_h3_logo_three_name: This is the name of the body h3 logo three. This will be used to to place  the body h3 logo three name in the landing page html
        Body_H3_logo_Three_paragraph: This is the body h3 logo three paragraph text. This will be used to to place  the body h3 logo three paragraph text in the landing page html
        Body_H3_logo_Four_name: This is the name of the body h3 logo four. This will be used to to place  the body h3 logo four name in the landing page html
        Body_H3_logo_Four_paragraph: This is the body h3 logo four paragraph text. This will be used to to place  the body h3 logo four paragraph text in the landing page html
        section_Three_paragraph: This is the section three paragraph text. This will be used to to place  the section three paragraph text in the landing page html
        section_Three_sub_paragraph: This is the section three sub paragraph text. This will be used to to place  the section three sub paragraph text in the landing page html
        Footer_H3: This is the footer h3 text. This will be used to to place  the footer h3 text in the landing page html
        Footer_H3_paragraph: This is the footer h3 paragraph text. This will be used to to place  the footer h3 paragraph text in the landing page html
        Footer_name_employee: This is the footer name employee text. This will be used to to place  the footer name employee text in the landing page html
        Name_job_description: This is the name job description text. This will be used to to place  the name job description text in the landing page html
        Footer_H2_text: This is the footer h2 text. This will be used to to place  the footer h2 text in the landing page html
        Footer_contact_address: This is the footer contact address text. This will be used to to place  the footer contact address text in the landing page html
        customer_care_email: This is the customer care email text. This will be used to to place  the customer care email text in the landing page html
        faq_link: This is the faq link text. This will be used to to place  the faq link text in the landing page html
        login_link: This is the login link text. This will be used to to place  the login link text in the landing page html
        signup_link: This is the signup link text. This will be used to to place  the signup link text in the landing page html
    """

    # checks if user is a superuser 
    if current_user.is_superuser:

        # generates bucket name
        bucket_name=uuid4().hex

        # check if landing pAGE name already exist
        if db.query(Landing_Page_models.LPage).filter(Landing_Page_models.LPage.landing_page_name == request.landing_page_name).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="landing_page_name already exist")
        
        # check if all form fields are filled
        if request.landing_page_name == "" or request.company_name == "" or request.body_h1 == "" or request.body_paragraph == "" or request.body_h3 == "" or request.body_h3_logo_one_name == "" or request.body_h3_logo_one_paragraph == "" or request.body_h3_logo_two_name == "" or request.body_h3_logo_two_paragraph == "" or request.body_h3_logo_three_name == "" or request.body_h3_logo_three_paragraph == "" or request.body_h3_logo_four_name == "" or request.body_h3_logo_four_paragraph == "" or request.section_three_paragraph == "" or request.section_three_sub_paragraph == "" or request.footer_h3 == "" or request.footer_h3_paragraph == "" or request.footer_name_employee == "" or request.name_job_description == "" or request.footer_contact_address == "" or request.home_link == "" or request.about_link == "" or request.faq_link == "" or request.contact_us_link == "" or request.login_link == "" or request.signup_link == "" or             request.footer_h2_text == "" or request.customer_care_email == "" or request.home_link == "" or request.about_link == "" or request.faq_link == "":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please fill all fields")
            
        # check if company logo is uploaded else raise error
        if company_logo:
            company_logo = "/" +bucket_name + "/" + await upload_image(company_logo, db=db, bucket_name = bucket_name)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload company logo")

        # check if section three image is uploaded else raise error
        if section_three_image:
            section_three_image = "/" +bucket_name + "/" + await upload_image(section_three_image, db=db, bucket_name = bucket_name)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload section_Three_image")

        # check if section four image is uploaded else raise error
        if section_four_image:
            section_four_image = "/" +bucket_name + "/" + await upload_image(section_four_image, db=db, bucket_name = bucket_name)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload Section_Four_image")

        # check if section one image link is uploaded else raise error
        if section_one_image_link:
            section_one_image_link = "/" +bucket_name + "/" + await upload_image(section_one_image_link, db=db, bucket_name = bucket_name)

        # check if body h3 logo one is uploaded else raise error
        if body_h3_logo_one:
            body_h3_logo_one = "/" +bucket_name + "/" + await upload_image(body_h3_logo_one, db=db, bucket_name = bucket_name)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload Body_H3_logo_One")

        # check if body h3 logo two is uploaded else raise error
        if body_h3_logo_two:
            body_h3_logo_two = "/" +bucket_name + "/" + await upload_image(body_h3_logo_two, db=db, bucket_name = bucket_name)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload body_h3_logo_two")

        # check if body h3 logo three is uploaded else raise error
        if body_h3_logo_three:
            body_h3_logo_three =  "/" +bucket_name + "/" + await upload_image(body_h3_logo_three, db=db, bucket_name = bucket_name)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload Body_H3_logo_Three")

        # check if body h3 logo four is uploaded else raise error
        if body_h3_logo_four:
            body_h3_logo_four = "/" +bucket_name + "/" + await upload_image(body_h3_logo_four, db=db, bucket_name = bucket_name)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload Body_H3_logo_Four")

        # map schema to landing page model
        landingpage_data = Landing_Page_models.LPage(
            id = uuid4().hex,
            user_id =current_user.id,
            landing_page_name = request.landing_page_name,
            bucket_name=bucket_name,
            body_h1=request.body_h1,
            body_paragraph=request.body_paragraph,
            body_h3=request.body_h3,
            body_h3_logo_one=body_h3_logo_one,
            body_h3_logo_one_name=request.body_h3_logo_one_name,
            body_h3_logo_one_paragraph=request.body_h3_logo_one_paragraph,
            body_h3_logo_two=body_h3_logo_two,
            body_h3_logo_two_name=request.body_h3_logo_two_name,
            body_h3_logo_two_paragraph=request.body_h3_logo_two_paragraph,
            body_h3_logo_three=body_h3_logo_three,
            body_h3_logo_three_name=request.body_h3_logo_three_name,
            body_h3_logo_three_paragraph=request.body_h3_logo_three_paragraph,
            body_h3_logo_four=body_h3_logo_four,
            body_h3_logo_four_name=request.body_h3_logo_four_name,
            body_h3_logo_four_paragraph=request.body_h3_logo_four_paragraph,
            section_one_image_link=section_one_image_link,
            section_three_paragraph=request.section_three_paragraph,
            section_three_sub_paragraph=request.section_three_sub_paragraph,
            section_three_image=section_three_image,
            footer_h3=request.footer_h3,
            footer_h3_paragraph=request.footer_h3_paragraph,
            footer_name_employee=request.footer_name_employee,
            name_job_description=request.name_job_description,
            footer_h2_text=request.footer_h2_text,
            footer_contact_address=request.footer_contact_address,
            customer_care_email=request.customer_care_email,
            home_link=request.home_link,
            about_link=request.about_link,
            faq_link=request.faq_link,
            contact_us_link=request.contact_us_link,
            section_four_image=section_four_image,  
            company_name=request.company_name,
            company_logo=company_logo,
            login_link=request.login_link,
            signup_link=request.signup_link,
  

        )
        
        # Attempt to save the new landing page and return the result to the client. 
        try:
            # try to save data to database
            db.add(landingpage_data)
            db.commit()
            db.refresh(landingpage_data)
            # return query of landing page id from the database
            return landingpage_data

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
    """
    This endpoint will return all landing pages
    """
    # check if user is a superuser
    if current_user.is_superuser:

        # attempt to get all landing pages from the database
        try:
            landingpages = db.query(Landing_Page_models.LPage).all()

            return  landingpages
        
        # return error if landing pages cannot be fetched
        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error fetching data")


# Endpoint to get a single landing page and use the fetch_landing_page function to get the data
@app.get("/landingpage/{landingpage_name}", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_landing_page(request:Request,landingpage_name: str, db: Session = Depends(get_db)):
    """
    This endpoint will return a single landing page in html
    """
    # query the database using the landing page name
    landingpage_data = db.query(Landing_Page_models.LPage).filter(Landing_Page_models.LPage.landing_page_name ==landingpage_name).first()


    # check if the data is returned and return the data
    image_path = getUrlFullPath(request, "image")
    # css_path = getUrlFullPath(request, "css")

    # check if landing page data is returned and extract the data
    if landingpage_data:
        h = {
            "login_link":landingpage_data.login_link,
            "landing_page_name":landingpage_data.landing_page_name,
            "body_h1":landingpage_data.body_h1,
            "body_paragraph":landingpage_data.body_paragraph,
            "body_h3":landingpage_data.body_h3,
            "body_h3_logo_one":image_path + landingpage_data.body_h3_logo_one,
            "body_h3_logo_one_name": landingpage_data.body_h3_logo_one_name,
            "body_h3_logo_one_paragraph":landingpage_data.body_h3_logo_one_paragraph,
            "body_h3_logo_two":image_path +landingpage_data.body_h3_logo_two,
            "body_h3_logo_two_name":landingpage_data.body_h3_logo_two_name,
            "body_h3_logo_two_paragraph":landingpage_data.body_h3_logo_two_paragraph,
            "body_h3_logo_three":image_path +landingpage_data.body_h3_logo_three,
            "body_h3_logo_three_name":landingpage_data.body_h3_logo_three_name,
            "body_h3_logo_three_paragraph":landingpage_data.body_h3_logo_three_paragraph,
            "body_h3_logo_four":image_path +landingpage_data.body_h3_logo_four,
            "body_h3_logo_four_name":landingpage_data.body_h3_logo_four_name,
            "body_h3_logo_four_paragraph":landingpage_data.body_h3_logo_four_paragraph,
            "section_one_image_link":image_path + landingpage_data.section_one_image_link,
            "section_three_paragraph":landingpage_data.section_three_paragraph,
            "section_three_sub_paragraph":landingpage_data.section_three_sub_paragraph,
            "section_three_image":image_path + landingpage_data.section_three_image,
            "footer_h3":landingpage_data.footer_h3,
            "footer_h3_paragraph":landingpage_data.footer_h3_paragraph,
            "footer_name_employee":landingpage_data.footer_name_employee,
            "name_job_description":landingpage_data.name_job_description,
            "footer_h2_text":landingpage_data.footer_h2_text,
            "footer_contact_address":landingpage_data.footer_contact_address,
            "customer_care_email":landingpage_data.customer_care_email,
            "home_link":landingpage_data.home_link,
            "about_link":landingpage_data.about_link,
            "faq_link":landingpage_data.faq_link,
            "contact_us_link":landingpage_data.contact_us_link,
            "section_four_image":image_path + landingpage_data.section_four_image,
            "company_name":landingpage_data.company_name,
            "company_logo":image_path + landingpage_data.company_logo,
            # "css_file": css_path + "/css/landingpage.css",
            "signup_link":landingpage_data.signup_link,
        }
        return templates.TemplateResponse("landingpage.html", {"request": request, "h": h})
    
    # if no data is returned, throw an error
    else:
        raise HTTPException(status_code=404, detail="Landing page not found")



# Endpoint to update a single landing page and use the update_landing_page function to update the data
@app.put("/landingpage/{landingpage_name}", status_code=status.HTTP_200_OK, response_model=Landing_page_schemas.landingPageResponse)
async def update_landing_page(landingpage_name: str,request: Landing_page_schemas.landingPageCreate = Depends(Landing_page_schemas.landingPageCreate.as_form), db: Session = Depends(get_db), current_user = Depends(is_authenticated),
    company_logo: UploadFile = File(...), section_three_image: UploadFile = File(...), section_four_image: UploadFile = File(...), section_one_image_link: UploadFile = File(...), body_h3_logo_one: UploadFile = File(...), body_h3_logo_two: UploadFile = File(...),
    body_h3_logo_three: UploadFile = File(...), body_h3_logo_four: UploadFile = File(...),):
    """
    This endpoint will update a single landing page in the database with data from the request
    """
    # check if the user is superuser
    if current_user.is_superuser:

        # query the database using the landing page name
        update_landing_page_data= db.query(Landing_Page_models.LPage).filter(Landing_Page_models.LPage.landing_page_name == landingpage_name).first()

        # check if update landing page does not exist, throw an error
        if update_landing_page_data == None:
            raise HTTPException(status_code=404, detail="Landing page does not exist")

        # check if the landing page name is not the same as the landing page name in the database, throw an error
        if update_landing_page_data.landing_page_name != request.landing_page_name:
            raise HTTPException(status_code=400, detail="Landing page name cannot be changed")

        #  check if landing page company name is not the same, update the landing page company name
        if update_landing_page_data.company_name != request.company_name:
            update_landing_page_data.company_name = request.company_name
        
        # check if landing page body H1 is not the same, update the landing page body H1
        if update_landing_page_data.body_h1 != request.body_h1:
            update_landing_page_data.body_h1 = request.body_h1
        
        # check if landing page body paragraph is not the same, update the landing page body paragraph
        if update_landing_page_data.body_paragraph != request.body_paragraph:
            update_landing_page_data.body_paragraph = request.body_paragraph

        # check if landing page body H3 logo one name is not the same, update the landing page body H3 logo one name
        if update_landing_page_data.body_h3 != request.body_h3:
            update_landing_page_data.body_h3 = request.body_h3
        
        # check if landing page body h3 logo one name is not the same, update the landing page body h3 logo one name
        if update_landing_page_data.body_h3_logo_one_name != request.body_h3_logo_one_name:
            update_landing_page_data.body_h3_logo_one_name = request.body_h3_logo_one_name
        
        # check if landing page body h3 logo one paragraph is not the same, update the landing page body h3 logo one paragraph
        if update_landing_page_data.body_h3_logo_one_paragraph != request.body_h3_logo_one_paragraph:
            update_landing_page_data.body_h3_logo_one_paragraph = request.body_h3_logo_one_paragraph
        
        # check if landing page body h3 logo two name is not the same, update the landing page body h3 logo two name
        if update_landing_page_data.body_h3_logo_two_name != request.body_h3_logo_two_name:
            update_landing_page_data.body_h3_logo_two_name = request.body_h3_logo_two_name
        
        # check if landing page body h3 logo two paragraph is not the same, update the landing page body h3 two paragraph
        if update_landing_page_data.body_h3_logo_two_paragraph != request.body_h3_logo_two_paragraph:
            update_landing_page_data.body_h3_logo_two_paragraph = request.body_h3_logo_two_paragraph
        
        # chcek if landing page body h3 logo three name is not the same, update the landing page body h3 logo three name
        if update_landing_page_data.body_h3_logo_three_name != request.body_h3_logo_three_name:
            update_landing_page_data.body_h3_logo_three_name = request.body_h3_logo_three_name
        
        # check if landing page body h3 logo three paragraph is not the same, update the landing page body h3 logo three paragraph
        if update_landing_page_data.body_h3_logo_three_paragraph != request.body_h3_logo_three_paragraph:
            update_landing_page_data.body_h3_logo_three_paragraph = request.body_h3_logo_three_paragraph
        
        # check if landing page body h3 logo four name is not the same, update the landing page body h3 logo four name
        if update_landing_page_data.body_h3_logo_four_name != request.body_h3_logo_four_name:
            update_landing_page_data.body_h3_logo_four_name = request.body_h3_logo_four_name
        
        # check if landing page body h3 logo four paragraph is not the same, update the landing page body h3 logo four paragraph
        if update_landing_page_data.body_h3_logo_four_paragraph != request.body_h3_logo_four_paragraph:
            update_landing_page_data.body_h3_logo_four_paragraph = request.body_h3_logo_four_paragraph
        
        # check if landing page section three paragraph is not the same, update the landing page section three paragraph
        if update_landing_page_data.section_three_paragraph != request.section_three_paragraph:
            update_landing_page_data.section_three_paragraph = request.section_three_paragraph
        
        # check if landing page section three sub paragraph is not the same, update the landing page section three sub paragraph
        if update_landing_page_data.section_three_sub_paragraph != request.section_three_sub_paragraph:
            update_landing_page_data.section_three_sub_paragraph = request.section_three_sub_paragraph

        # check if landing page footer h3 is not the same, update the landing page footer h3
        if update_landing_page_data.footer_h3 != request.footer_h3:
            update_landing_page_data.footer_h3 = request.footer_h3
        
        # check if landing page footer paragraph is not the same, update the landing page footer paragraph
        if update_landing_page_data.footer_h3_paragraph != request.footer_h3_paragraph:
            update_landing_page_data.footer_h3_paragraph = request.footer_h3_paragraph
        
        # check if landing page footer name employee is not the same, update the landing page footer name employee
        if update_landing_page_data.footer_name_employee != request.footer_name_employee:
            update_landing_page_data.footer_name_employee = request.footer_name_employee
        
        # check if landing page positon of emplaoyee is not the same, update the landing page positon of emplaoyee
        if update_landing_page_data.name_job_description != request.name_job_description:   
            update_landing_page_data.name_job_description = request.name_job_description
        
        # check if landing page footer h2 text is not the same, update the landing page footer h2 text
        if update_landing_page_data.footer_h2_text != request.footer_h2_text:
            update_landing_page_data.footer_h2_text = request.footer_h2_text
        
        # check if login link is not the same, update the login link
        if update_landing_page_data.login_link != request.login_link:
            update_landing_page_data.login_link = request.login_link
        
        # check if signup link is not the same, update the signup link
        if update_landing_page_data.signup_link != request.signup_link:
            update_landing_page_data.signup_link = request.signup_link
        
        # check if home link is not the same, update the home link
        if update_landing_page_data.home_link != request.home_link:
            update_landing_page_data.home_link = request.home_link
        
        # check if about link is not the same, update the about link
        if update_landing_page_data.about_link != request.about_link:
            update_landing_page_data.about_link = request.about_link
        
        # check if faq link is not the same, update the faq link
        if update_landing_page_data.faq_link != request.faq_link:
            update_landing_page_data.faq_link = request.faq_link
        
        # check if contact link is not the same, update the contact link
        if update_landing_page_data.contact_us_link != request.contact_us_link:
            update_landing_page_data.contact_us_link = request.contact_us_link
        
        # check if contact address is not the same, update the contact address
        if update_landing_page_data.footer_contact_address != request.footer_contact_address:
            update_landing_page_data.footer_contact_address = request.footer_contact_address

        #  check if customer care mail is not the same, update the customer care mail
        if update_landing_page_data.customer_care_email != request.customer_care_email:
            update_landing_page_data.customer_care_email = request.customer_care_email
        
        # check company logo is uploaded, update the company logo
        if isFileExist(company_logo) != True:
            company_logo1 = update_landing_page_data.company_logo
            if deleteFile(company_logo1):
                company_logo = await upload_image(company_logo, db=db, bucket_name = update_landing_page_data.bucket_name)
                update_landing_page_data.company_logo ="/"+ update_landing_page_data.bucket_name + "/" + company_logo
        
        # check if section one image is uploaded, update the section one image
        if isFileExist(section_one_image_link) != True:
            section_one_image_link1 = update_landing_page_data.section_one_image_link
            if deleteFile(section_one_image_link1):
                section_one_image_link = section_one_image_link
                section_one_image_link = await upload_image(section_one_image_link, db=db, bucket_name = update_landing_page_data.bucket_name)
                update_landing_page_data.section_one_image_link ="/"+ update_landing_page_data.bucket_name + "/" + section_one_image_link
        
        # check if body h3 logo one image is uploaded, update the body h3 logo one image
        if isFileExist(body_h3_logo_one) != True:
            body_h3_logo_one1 = update_landing_page_data.body_h3_logo_one
            if deleteFile(body_h3_logo_one1):
                body_h3_logo_one = body_h3_logo_one
                body_h3_logo_one = await upload_image(body_h3_logo_one, db=db, bucket_name = update_landing_page_data.bucket_name)
                update_landing_page_data.body_h3_logo_one ="/"+ update_landing_page_data.bucket_name + "/" + body_h3_logo_one
        
        # check if body h3 logo two image is uploaded, update the body h3 logo two image
        if isFileExist(body_h3_logo_two) != True:
            body_h3_logo_two1 = update_landing_page_data.body_h3_logo_two
            if deleteFile(body_h3_logo_two1):
                body_h3_logo_two = body_h3_logo_two
                body_h3_logo_two = await upload_image(body_h3_logo_two, db=db, bucket_name = update_landing_page_data.bucket_name)
                update_landing_page_data.body_h3_logo_two ="/"+ update_landing_page_data.bucket_name + "/" + body_h3_logo_two
        
        # check if body h3 logo three image is uploaded, update the body h3 logo three image
        if isFileExist(body_h3_logo_three) != True:
            body_h3_logo_three1 = update_landing_page_data.body_h3_logo_three
            if deleteFile(body_h3_logo_three1):
                body_h3_logo_three = body_h3_logo_three
                body_h3_logo_three = await upload_image(body_h3_logo_three, db=db, bucket_name = update_landing_page_data.bucket_name)
                update_landing_page_data.Body_H3_logo_Three ="/"+ update_landing_page_data.bucket_name + "/" + body_h3_logo_three
        
        # check if body h3 logo four image is uploaded, update the body h3 logo four image
        if isFileExist(body_h3_logo_four) != True:
            body_h3_logo_four1 = update_landing_page_data.body_h3_logo_four
            if deleteFile(body_h3_logo_four1):
                body_h3_logo_four = body_h3_logo_four
                body_h3_logo_four = await upload_image(body_h3_logo_four, db=db, bucket_name = update_landing_page_data.bucket_name)
                update_landing_page_data.Body_H3_logo_Four ="/"+ update_landing_page_data.bucket_name + "/" + body_h3_logo_four
        
        # check if section three image is uploaded, update the section three image
        if isFileExist(section_three_image) != True:
            section_three_image1 = update_landing_page_data.section_three_image
            if deleteFile(section_three_image1):
                section_three_image = section_three_image
                section_three_image = await upload_image(section_three_image, db=db, bucket_name = update_landing_page_data.bucket_name)
                update_landing_page_data.section_Three_image ="/"+ update_landing_page_data.bucket_name + "/" + section_three_image
        
        # check if section four image is uploaded, update the section four image
        if isFileExist(section_four_image) != True:
            section_four_image1 = update_landing_page_data.section_four_image
            if deleteFile(section_four_image1):
                section_four_image = section_four_image
                section_four_image = await upload_image(section_four_image, db=db, bucket_name = update_landing_page_data.bucket_name)
                update_landing_page_data.section_Four_image ="/"+ update_landing_page_data.bucket_name + "/" + section_four_image

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
@app.delete("/landingpage/{landingpage_name}",status_code=200, tags=["landingPage"])
async def delete_landingPage(landingpage_name: str, current_user = Depends(is_authenticated), db: Session = Depends(get_db)):
    """
    This endpoint is used to delete landing page data from the database and all images associated with the landing page data
    """
    # check if user is a super user
    if current_user.is_superuser:
         # query for the landing page data
        landingpage_data = db.query(Landing_Page_models.LPage).filter(Landing_Page_models.LPage.landing_page_name == landingpage_name).first()

        # check if landing page data is found
        if landingpage_data:

            # delete the images from the bucket
            deleteimage=[landingpage_data.company_logo,landingpage_data.section_one_image_link,landingpage_data.body_h3_logo_one,landingpage_data.body_h3_logo_two,landingpage_data.body_h3_logo_three,landingpage_data.body_h3_logo_four,landingpage_data.section_three_image,landingpage_data.section_four_image]
            for i in deleteimage:
                if deleteFile(i):
                    pass
                else:
                    pass
            
            # delete the landing page data
            db.delete(landingpage_data)
            db.commit()
            return {"message": "Data deleted successfully."}

        # landing page data not found 
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': "Data could not be found. Please try again."})
    
    # user is not a super user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'error': "You are not authorized to perform this action."})




# Function to retrieve landing page images
def image_fullpath(imagepath):
    root_location = os.path.abspath("filestorage")
    image_location = os.path.join(root_location, imagepath)
    return FileResponse(image_location)


# Function to get host path to landing page images
def getUrlFullPath(request: Request, filetype: str):
    hostname = request.headers.get('host')
    image_path = request.url.scheme +"://" + hostname + f"/landingpage/{filetype}"
    return image_path