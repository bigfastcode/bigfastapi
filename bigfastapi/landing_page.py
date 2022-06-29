from uuid import uuid4
from typing import List
from sqlalchemy.orm import Session
from .auth_api import is_authenticated
from bigfastapi.db.database import get_db
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from bigfastapi.models import landing_page_models
from bigfastapi.schemas import landing_page_schemas
from bigfastapi.files import upload_image, deleteFile, isFileExist
from fastapi import APIRouter, Depends, UploadFile, status, HTTPException, File, Request
import os
from fastapi.responses import FileResponse
from bigfastapi.utils.settings import LANDING_PAGE_FOLDER, LANDING_PAGE_FORM_PATH
from starlette.requests import Request
import pkg_resources

app = APIRouter(tags=["Landing Page"])


templates = Jinja2Templates(directory=LANDING_PAGE_FOLDER)


# Endpoint to open index.html
@app.get("/landing-page/index.html")
async def landing_page_index(request: Request,  session: Session = Depends(get_db)):
    """
    This endpont will return landing page index.html
    """
    # if current_user:

    return templates.TemplateResponse("index.html", {"request": request})
    # else:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Page not found")




# Endpoint to get landing page images and endpoints
@app.get("/files/{filetype}/{folder}/{image_name}", status_code=200)
def path(filetype: str, image_name: str, folder: str, request: Request, ):
    """
    This endpoint is used in the landing page html to fetch images 
    """
    if filetype == "css":
        fullpath = image_fullpath("css", folder + "/" + image_name)
    elif filetype == "js":
        fullpath = image_fullpath("js", folder + "/" + image_name)
    else:
        fullpath = image_fullpath("image", folder + "/" + image_name)
    return fullpath


# Endpoint to create landing page
@app.post("/landing-page/create", status_code=201, response_model=landing_page_schemas.landingPageResponse)
async def createlandingpage(request: landing_page_schemas.landingPageCreate = Depends(landing_page_schemas.landingPageCreate.as_form), 
                            db: Session = Depends(get_db), 
                            current_user=Depends(is_authenticated),
                            company_logo: UploadFile = File(...),
                            favicon: UploadFile = File(...),
                            section_three_image: UploadFile = File(...),
                            section_four_image: UploadFile = File(...),
                            section_one_image_link: UploadFile = File(...),
                            body_h3_logo_one: UploadFile = File(...),
                            body_h3_logo_two: UploadFile = File(...),
                            body_h3_logo_three: UploadFile = File(...),
                            body_h3_logo_four: UploadFile = File(...),
                            shape_one: UploadFile = File(...),
                            shape_two: UploadFile = File(...),
                            shape_three: UploadFile = File(...),):

    # checks if user is a superuser
    if current_user.is_superuser is not True:
        raise HTTPException(status_code=403, detail="You are not allowed to perform this action")

    # generates bucket name
    bucket_name = uuid4().hex

    # check if landing pAGE name already exist
    if db.query(landing_page_models.LPage).filter(landing_page_models.LPage.landing_page_name == request.landing_page_name).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="landing_page_name already exist")

    # check if all form fields are filled
    if request.landing_page_name == "" or request.company_name == "" or request.body_h1 == "" or request.body_paragraph == "" or request.body_h3 == "" or request.body_h3_logo_one_name == "" or request.body_h3_logo_one_paragraph == "" or request.body_h3_logo_two_name == "" or request.body_h3_logo_two_paragraph == "" or request.body_h3_logo_three_name == "" or request.body_h3_logo_three_paragraph == "" or request.body_h3_logo_four_name == "" or request.body_h3_logo_four_paragraph == "" or request.section_three_paragraph == "" or request.section_three_sub_paragraph == "" or request.footer_h3 == "" or request.footer_h3_paragraph == "" or request.footer_name_employee == "" or request.name_job_description == "" or request.footer_contact_address == "" or request.home_link == "" or request.about_link == "" or request.faq_link == "" or request.contact_us_link == "" or request.login_link == "" or request.signup_link == "" or request.footer_h2_text == "" or request.customer_care_email == "" or request.home_link == "" or request.about_link == "" or request.faq_link == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Please fill all fields")

    # check if company logo is uploaded else raise error
    if not company_logo :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload company logo")
    company_logo = "/" + bucket_name + "/" + await upload_image(company_logo, db=db, bucket_name=bucket_name)

    
    if not favicon:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload favicon")
    favicon = "/" + bucket_name + "/" + await upload_image(favicon, db=db, bucket_name=bucket_name)
    
    if not shape_one:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload shape one")
    shape_one = "/" + bucket_name + "/" + await upload_image(shape_one, db=db, bucket_name=bucket_name)
    
    if not shape_two:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload shape two")
    shape_two = "/" + bucket_name + "/" + await upload_image(shape_two, db=db, bucket_name=bucket_name)
    
    if not shape_three:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload shape three")
    shape_three = "/" + bucket_name + "/" + await upload_image(shape_three, db=db, bucket_name=bucket_name)

    # check if section three image is uploaded else raise error
    if not section_three_image:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload section_Three_image")
    section_three_image = "/" + bucket_name + "/" + await upload_image(section_three_image, db=db, bucket_name=bucket_name)

    # check if section four image is uploaded else raise error
    if not section_four_image:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload Section_Four_image")
    section_four_image = "/" + bucket_name + "/" + await upload_image(section_four_image, db=db, bucket_name=bucket_name)

    # check if section one image link is uploaded else raise error
    if not section_one_image_link:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload image for section one")
    section_one_image_link = "/" + bucket_name + "/" + await upload_image(section_one_image_link, db=db, bucket_name=bucket_name)

    # check if body h3 logo one is uploaded else raise error
    if not body_h3_logo_one:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload Body_H3_logo_One")
    body_h3_logo_one = "/" + bucket_name + "/" + await upload_image(body_h3_logo_one, db=db, bucket_name=bucket_name)

    # check if body h3 logo two is uploaded else raise error
    if not body_h3_logo_two:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload body_h3_logo_two")
    body_h3_logo_two = "/" + bucket_name + "/" + await upload_image(body_h3_logo_two, db=db, bucket_name=bucket_name)

    # check if body h3 logo three is uploaded else raise error
    if not body_h3_logo_three:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload Body_H3_logo_Three")
    body_h3_logo_three = "/" + bucket_name + "/" + await upload_image(body_h3_logo_three, db=db, bucket_name=bucket_name)

    # check if body h3 logo four is uploaded else raise error
    if not body_h3_logo_four:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload Body_H3_logo_Four")
    body_h3_logo_four = "/" + bucket_name + "/" + await upload_image(body_h3_logo_four, db=db, bucket_name=bucket_name)


    # map schema to landing page model
    landingpage_data = landing_page_models.LPage(
        id = uuid4().hex,
        user_id=current_user.id,
        landing_page_name=request.landing_page_name,
        content = {
            "bucket_name": bucket_name,
            "body_h1":request.body_h1,
            "body_paragraph":request.body_paragraph,
            "body_h3":request.body_h3,
            "body_h3_logo_one":body_h3_logo_one,
            "body_h3_logo_one_name":request.body_h3_logo_one_name,
            "body_h3_logo_one_paragraph":request.body_h3_logo_one_paragraph,
            "body_h3_logo_two":body_h3_logo_two,
            "body_h3_logo_two_name":request.body_h3_logo_two_name,
            "body_h3_logo_two_paragraph":request.body_h3_logo_two_paragraph,
            "body_h3_logo_three":body_h3_logo_three,
            "body_h3_logo_three_name":request.body_h3_logo_three_name,
            "body_h3_logo_three_paragraph":request.body_h3_logo_three_paragraph,
            "body_h3_logo_four":body_h3_logo_four,
            "body_h3_logo_four_name":request.body_h3_logo_four_name,
            "body_h3_logo_four_paragraph":request.body_h3_logo_four_paragraph,
            "section_one_image_link":section_one_image_link,
            "section_three_paragraph":request.section_three_paragraph,
            "section_three_sub_paragraph":request.section_three_sub_paragraph,
            "section_three_image":section_three_image,
            "footer_h3":request.footer_h3,
            "footer_h3_paragraph":request.footer_h3_paragraph,
            "footer_name_employee":request.footer_name_employee,
            "name_job_description":request.name_job_description,
            "footer_h2_text":request.footer_h2_text,
            "footer_contact_address":request.footer_contact_address,
            "customer_care_email":request.customer_care_email,
            "home_link":request.home_link,
            "about_link":request.about_link,
            "faq_link":request.faq_link,
            "contact_us_link":request.contact_us_link,
            "section_four_image":section_four_image,
            "company_name":request.company_name,
            "company_logo":company_logo,
            "login_link":request.login_link,
            "signup_link":request.signup_link,
            "title" : request.title,
            "favicon" : favicon,
            "shape_one" : shape_one,
            "shape_two" : shape_two,
            "shape_three" : shape_three,
            }
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error saving data")



# Endpoint to get all landing pages and use the fetch_all_landing_pages function to get the data
@app.get("/landing-page/all", status_code=status.HTTP_200_OK, response_model=List[landing_page_schemas.landingPageResponse])
async def get_all_landing_pages(request: Request, db: Session = Depends(get_db),):

    """
    This endpoint will return all landing pages
    """
    # check if user is a superuser
    # if current_user.is_superuser:

    # attempt to get all landing pages from the database
    try:
        landingpages = db.query(landing_page_models.LPage).all()
        css_path = getUrlFullPath(request, "css") + "/landing-page/styles.css"
        h = {
            "css_path": css_path,
            "landing_page": landingpages
        }

        # return landingpages
        return templates.TemplateResponse("alllandingpage.html", {"request": request, "h": h})

    # return error if landing pages cannot be fetched
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error fetching data")


# Endpoint to get a single landing page and use the fetch_landing_page function to get the data
@app.get("/landing-page/{landingpage_name}", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_landing_page(request: Request, landingpage_name: str, db: Session = Depends(get_db)):
    """
    This endpoint will return a single landing page in html
    """
    # query the database using the landing page name
    landingpage_data = db.query(landing_page_models.LPage).filter(
        landing_page_models.LPage.landing_page_name == landingpage_name).first()
    
    # check if the data is returned and return the data
    image_path = getUrlFullPath(request, "image")
    css_path = getUrlFullPath(request, "css") + "/landing-page/styles.css"
    js_path = getUrlFullPath(request, "js") + "/landing-page/script.js"

    # check if landing page data is returned and extract the data
    if not landingpage_data:
        raise HTTPException(status_code=404, detail="Landing page not found")        
    h = {
        "login_link": landingpage_data.content["login_link"],
        "landing_page_name": landingpage_data.landing_page_name,
        "body_h1": landingpage_data.content["body_h1"],
        "body_paragraph": landingpage_data.content["body_paragraph"],
        "body_h3": landingpage_data.content["body_h3"],
        "body_h3_logo_one": image_path + landingpage_data.content["body_h3_logo_one"],
        "body_h3_logo_one_name": landingpage_data.content["body_h3_logo_one_name"],
        "body_h3_logo_one_paragraph": landingpage_data.content["body_h3_logo_one_paragraph"],
        "body_h3_logo_two": image_path + landingpage_data.content["body_h3_logo_two"],
        "body_h3_logo_two_name": landingpage_data.content["body_h3_logo_two_name"],
        "body_h3_logo_two_paragraph": landingpage_data.content["body_h3_logo_two_paragraph"],
        "body_h3_logo_three": image_path + landingpage_data.content["body_h3_logo_three"],
        "body_h3_logo_three_name": landingpage_data.content["body_h3_logo_three_name"],
        "body_h3_logo_three_paragraph": landingpage_data.content["body_h3_logo_three_paragraph"],
        "body_h3_logo_four": image_path + landingpage_data.content["body_h3_logo_four"],
        "body_h3_logo_four_name": landingpage_data.content["body_h3_logo_four_name"],
        "body_h3_logo_four_paragraph": landingpage_data.content["body_h3_logo_four_paragraph"],
        "section_one_image_link": image_path + landingpage_data.content["section_one_image_link"],
        "section_three_paragraph": landingpage_data.content["section_three_paragraph"],
        "section_three_sub_paragraph": landingpage_data.content["section_three_sub_paragraph"],
        "section_three_image": image_path + landingpage_data.content["section_three_image"],
        "footer_h3": landingpage_data.content["footer_h3"],
        "footer_h3_paragraph": landingpage_data.content["footer_h3_paragraph"],
        "footer_name_employee": landingpage_data.content["footer_name_employee"],
        "name_job_description": landingpage_data.content["name_job_description"],
        "footer_h2_text": landingpage_data.content["footer_h2_text"],
        "footer_contact_address": landingpage_data.content["footer_contact_address"],
        "customer_care_email": landingpage_data.content["customer_care_email"],
        "home_link": landingpage_data.content["home_link"],
        "about_link": landingpage_data.content["about_link"],
        "faq_link": landingpage_data.content["faq_link"],
        "contact_us_link": landingpage_data.content["contact_us_link"],
        "section_four_image": image_path + landingpage_data.content["section_four_image"],
        "company_name": landingpage_data.content["company_name"],
        "company_logo": image_path + landingpage_data.content["company_logo"],
        "css_file": css_path,
        "js_file": js_path,
        "signup_link": landingpage_data.content["signup_link"],
        "title": landingpage_data.content["title"],
        "favicon": image_path + landingpage_data.content["favicon"],
        "shape_one": image_path + landingpage_data.content["shape_one"],
        "shape_two": image_path + landingpage_data.content["shape_two"],
        "shape_three": image_path + landingpage_data.content["shape_three"],
        "LANDING_PAGE_FORM_PATH": LANDING_PAGE_FORM_PATH
    }
    return templates.TemplateResponse("landingpage.html", {"request": request, "h": h})

    # if no data is returned, throw an error


# Endpoint to update a single landing page and use the update_landing_page function to update the data
@app.put("/landing-page/{landingpage_name}", status_code=status.HTTP_200_OK, response_model=landing_page_schemas.landingPageResponse)
async def update_landing_page(landingpage_name: str, request: landing_page_schemas.landingPageCreate = Depends(landing_page_schemas.landingPageCreate.as_form), db: Session = Depends(get_db), current_user=Depends(is_authenticated),
                              company_logo: UploadFile = File(...), section_three_image: UploadFile = File(...), section_four_image: UploadFile = File(...), section_one_image_link: UploadFile = File(...), body_h3_logo_one: UploadFile = File(...), body_h3_logo_two: UploadFile = File(...),
                              body_h3_logo_three: UploadFile = File(...), body_h3_logo_four: UploadFile = File(...),
                              shape_one: UploadFile = File(...), shape_two: UploadFile = File(...), shape_three: UploadFile = File(...), favicon: UploadFile = File(...),):
    """
    This endpoint will update a single landing page in the database with data from the request
    """
    # check if the user is superuser
    if current_user.is_superuser:

        # query the database using the landing page name
        update_landing_page_data = db.query(landing_page_models.LPage).filter(
            landing_page_models.LPage.landing_page_name == landingpage_name).first()

        # check if update landing page does not exist, throw an error
        if update_landing_page_data == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Landing page does not exist")

        # check if the landing page name is not the same as the landing page name in the database, throw an error
        if update_landing_page_data.landing_page_name != request.landing_page_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Landing page name cannot be changed")

        #  check if landing page company name is not the same, update the landing page company name
        if update_landing_page_data.content["company_name"] != request.company_name:
            update_landing_page_data.content["company_name"] = request.company_name

        # check if landing page body H1 is not the same, update the landing page body H1
        if update_landing_page_data.content["body_h1"] != request.body_h1:
            update_landing_page_data.content["body_h1"] = request.body_h1

        # check if landing page body paragraph is not the same, update the landing page body paragraph
        if update_landing_page_data.content["body_paragraph"] != request.body_paragraph:
            update_landing_page_data.content["body_paragraph"] = request.body_paragraph

        # check if landing page body H3 logo one name is not the same, update the landing page body H3 logo one name
        if update_landing_page_data.content["body_h3"] != request.body_h3:
            update_landing_page_data.content["body_h3"] = request.body_h3

        # check if landing page body h3 logo one name is not the same, update the landing page body h3 logo one name
        if update_landing_page_data.content["body_h3_logo_one_name"] != request.body_h3_logo_one_name:
            update_landing_page_data.content["body_h3_logo_one_name"] = request.body_h3_logo_one_name

        # check if landing page body h3 logo one paragraph is not the same, update the landing page body h3 logo one paragraph
        if update_landing_page_data.content["body_h3_logo_one_paragraph"] != request.body_h3_logo_one_paragraph:
            update_landing_page_data.content["body_h3_logo_one_paragraph"] = request.body_h3_logo_one_paragraph

        # check if landing page body h3 logo two name is not the same, update the landing page body h3 logo two name
        if update_landing_page_data.content["body_h3_logo_two_name"] != request.body_h3_logo_two_name:
            update_landing_page_data.content["body_h3_logo_two_name"] = request.body_h3_logo_two_name

        # check if landing page body h3 logo two paragraph is not the same, update the landing page body h3 two paragraph
        if update_landing_page_data.content["body_h3_logo_two_paragraph"] != request.body_h3_logo_two_paragraph:
            update_landing_page_data.content["body_h3_logo_two_paragraph"] = request.body_h3_logo_two_paragraph

        # chcek if landing page body h3 logo three name is not the same, update the landing page body h3 logo three name
        if update_landing_page_data.content["body_h3_logo_three_name"] != request.body_h3_logo_three_name:
            update_landing_page_data.content["body_h3_logo_three_name"] = request.body_h3_logo_three_name

        # check if landing page body h3 logo three paragraph is not the same, update the landing page body h3 logo three paragraph
        if update_landing_page_data.content["body_h3_logo_three_paragraph"] != request.body_h3_logo_three_paragraph:
            update_landing_page_data.content["body_h3_logo_three_paragraph"] = request.body_h3_logo_three_paragraph

        # check if landing page body h3 logo four name is not the same, update the landing page body h3 logo four name
        if update_landing_page_data.content["body_h3_logo_four_name"] != request.body_h3_logo_four_name:
            update_landing_page_data.content["body_h3_logo_four_name"] = request.body_h3_logo_four_name

        # check if landing page body h3 logo four paragraph is not the same, update the landing page body h3 logo four paragraph
        if update_landing_page_data.content["body_h3_logo_four_paragraph"] != request.body_h3_logo_four_paragraph:
            update_landing_page_data.content["body_h3_logo_four_paragraph"] = request.body_h3_logo_four_paragraph

        # check if landing page section three paragraph is not the same, update the landing page section three paragraph
        if update_landing_page_data.content["section_three_paragraph"] != request.section_three_paragraph:
            update_landing_page_data.content["section_three_paragraph"] = request.section_three_paragraph

        # check if landing page section three sub paragraph is not the same, update the landing page section three sub paragraph
        if update_landing_page_data.content["section_three_sub_paragraph"] != request.section_three_sub_paragraph:
            update_landing_page_data.content["section_three_sub_paragraph"] = request.section_three_sub_paragraph

        # check if landing page footer h3 is not the same, update the landing page footer h3
        if update_landing_page_data.content["footer_h3"] != request.footer_h3:
            update_landing_page_data.content["footer_h3"] = request.footer_h3

        # check if landing page footer paragraph is not the same, update the landing page footer paragraph
        if update_landing_page_data.content["footer_h3_paragraph"] != request.footer_h3_paragraph:
            update_landing_page_data.content["footer_h3_paragraph"] = request.footer_h3_paragraph

        # check if landing page footer name employee is not the same, update the landing page footer name employee
        if update_landing_page_data.content["footer_name_employee"] != request.footer_name_employee:
            update_landing_page_data.content["footer_name_employee"] = request.footer_name_employee

        # check if landing page positon of emplaoyee is not the same, update the landing page positon of emplaoyee
        if update_landing_page_data.content["name_job_description"] != request.name_job_description:
            update_landing_page_data.content["name_job_description"] = request.name_job_description

        # check if landing page footer h2 text is not the same, update the landing page footer h2 text
        if update_landing_page_data.content["footer_h2_text"] != request.footer_h2_text:
            update_landing_page_data.content["footer_h2_text"] = request.footer_h2_text

        # check if login link is not the same, update the login link
        if update_landing_page_data.content["login_link"] != request.login_link:
            update_landing_page_data.content["login_link"] = request.login_link

        # check if signup link is not the same, update the signup link
        if update_landing_page_data.content["signup_link"] != request.signup_link:
            update_landing_page_data.content["signup_link"] = request.signup_link

        # check if home link is not the same, update the home link
        if update_landing_page_data.content["home_link"] != request.home_link:
            update_landing_page_data.content["home_link"] = request.home_link

        # check if about link is not the same, update the about link
        if update_landing_page_data.content["about_link"] != request.about_link:
            update_landing_page_data.content["about_link"] = request.about_link

        # check if faq link is not the same, update the faq link
        if update_landing_page_data.content["faq_link"] != request.faq_link:
            update_landing_page_data.content["faq_link"] = request.faq_link

        # check if contact link is not the same, update the contact link
        if update_landing_page_data.content["contact_us_link"] != request.contact_us_link:
            update_landing_page_data.content["contact_us_link"] = request.contact_us_link

        # check if contact address is not the same, update the contact address
        if update_landing_page_data.content["footer_contact_address"] != request.footer_contact_address:
            update_landing_page_data.content["footer_contact_address"] = request.footer_contact_address

        #  check if customer care mail is not the same, update the customer care mail
        if update_landing_page_data.content["customer_care_email"] != request.customer_care_email:
            update_landing_page_data.content["customer_care_email"] = request.customer_care_email
        
        if update_landing_page_data.content["title"]!= request.title:
            update_landing_page_data.content["title"] = request.title

        if isFileExist(favicon) != True:
            favicon1 =update_landing_page_data.content["favicon"]
            if deleteFile(favicon1):
                favicon = await upload_image(favicon, db=db, bucket_name=update_landing_page_data.content["bucket_name"])
                update_landing_page_data.content["favicon"] = "/" + update_landing_page_data.content["bucket_name"] + "/" + favicon
        
        if isFileExist(shape_one) != True:
            shape_one1 =update_landing_page_data.content["shape_one"]
            if deleteFile(shape_one1):
                shape_one = await upload_image(shape_one, db=db, bucket_name=update_landing_page_data.content["bucket_name"])
                update_landing_page_data.content["shape_one"] = "/" + update_landing_page_data.content["bucket_name"] + "/" + shape_one
        
        if isFileExist(shape_two) != True:
            shape_two1 =update_landing_page_data.content["shape_two"]
            if deleteFile(shape_two1):
                shape_two = await upload_image(shape_two, db=db, bucket_name=update_landing_page_data.content["bucket_name"])
                update_landing_page_data.content["shape_two"] = "/" + update_landing_page_data.content["bucket_name"] + "/" + shape_two
        
        if isFileExist(shape_three) != True:
            shape_three1 =update_landing_page_data.content["shape_three"]
            if deleteFile(shape_three1):
                shape_three = await upload_image(shape_three, db=db, bucket_name=update_landing_page_data.content["bucket_name"])
                update_landing_page_data.content["shape_three"] = "/" + update_landing_page_data.content["bucket_name"] + "/" + shape_three

        # check company logo is uploaded, update the company logo
        if isFileExist(company_logo) != True:
            company_logo1 = update_landing_page_data.content["company_logo"]
            if deleteFile(company_logo1):
                company_logo = await upload_image(company_logo, db=db, bucket_name=update_landing_page_data.content["bucket_name"])
                update_landing_page_data.content["company_logo"] = "/" + \
                    update_landing_page_data.content["bucket_name"] + "/" + company_logo

        # check if section one image is uploaded, update the section one image
        if isFileExist(section_one_image_link) != True:
            section_one_image_link1 = update_landing_page_data.content["section_one_image_link"]
            if deleteFile(section_one_image_link1):
                section_one_image_link = section_one_image_link
                section_one_image_link = await upload_image(section_one_image_link, db=db, bucket_name=update_landing_page_data.content["bucket_name"])
                update_landing_page_data.content["section_one_image_link"] = "/" + \
                    update_landing_page_data.content["bucket_name"] + "/" + section_one_image_link

        # check if body h3 logo one image is uploaded, update the body h3 logo one image
        if isFileExist(body_h3_logo_one) != True:
            body_h3_logo_one1 = update_landing_page_data.content["body_h3_logo_one"]
            if deleteFile(body_h3_logo_one1):
                body_h3_logo_one = body_h3_logo_one
                body_h3_logo_one = await upload_image(body_h3_logo_one, db=db, bucket_name=update_landing_page_data.content["bucket_name"])
                update_landing_page_data.content["body_h3_logo_one"] = "/" + \
                    update_landing_page_data.content["bucket_name"] + "/" + body_h3_logo_one

        # check if body h3 logo two image is uploaded, update the body h3 logo two image
        if isFileExist(body_h3_logo_two) != True:
            body_h3_logo_two1 = update_landing_page_data.content["body_h3_logo_two"]
            if deleteFile(body_h3_logo_two1):
                body_h3_logo_two = body_h3_logo_two
                body_h3_logo_two = await upload_image(body_h3_logo_two, db=db, bucket_name=update_landing_page_data.content["bucket_name"])
                update_landing_page_data.content["body_h3_logo_two"] = "/" + \
                    update_landing_page_data.content["bucket_name"] + "/" + body_h3_logo_two

        # check if body h3 logo three image is uploaded, update the body h3 logo three image
        if isFileExist(body_h3_logo_three) != True:
            body_h3_logo_three1 = update_landing_page_data.content["body_h3_logo_three"]
            if deleteFile(body_h3_logo_three1):
                body_h3_logo_three = body_h3_logo_three
                body_h3_logo_three = await upload_image(body_h3_logo_three, db=db, bucket_name=update_landing_page_data.content["bucket_name"])
                update_landing_page_data.content["body_h3_logo_three"] = "/" + \
                    update_landing_page_data.content["bucket_name"] + "/" + body_h3_logo_three

        # check if body h3 logo four image is uploaded, update the body h3 logo four image
        if isFileExist(body_h3_logo_four) != True:
            body_h3_logo_four1 = update_landing_page_data.content["body_h3_logo_four"]
            if deleteFile(body_h3_logo_four1):
                body_h3_logo_four = body_h3_logo_four
                body_h3_logo_four = await upload_image(body_h3_logo_four, db=db, bucket_name=update_landing_page_data.content["bucket_name"])
                update_landing_page_data.content["body_h3_logo_four"] = "/" + \
                    update_landing_page_data.content["bucket_name"] + "/" + body_h3_logo_four

        # check if section three image is uploaded, update the section three image
        if isFileExist(section_three_image) != True:
            section_three_image1 = update_landing_page_data.content["section_three_image"]
            if deleteFile(section_three_image1):
                section_three_image = section_three_image
                section_three_image = await upload_image(section_three_image, db=db, bucket_name=update_landing_page_data.content["bucket_name"])
                update_landing_page_data.content["section_three_image"] = "/" + \
                    update_landing_page_data.content["bucket_name"] + "/" + section_three_image

        # check if section four image is uploaded, update the section four image
        if isFileExist(section_four_image) != True:
            section_four_image1 = update_landing_page_data.content["section_four_image"]
            if deleteFile(section_four_image1):
                section_four_image = section_four_image
                section_four_image = await upload_image(section_four_image, db=db, bucket_name=update_landing_page_data.content["bucket_name"])
                update_landing_page_data.content["section_four_image"] = "/" + \
                    update_landing_page_data.content["bucket_name"] + "/" + section_four_image

        # attempt to update the landing page data
        try:
            db.commit()
            db.refresh(update_landing_page_data)
            return update_landing_page_data
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="An error occured while updating the landing page data")

    else:
        raise HTTPException(status_code=404, detail="Landing page not found")


# Endpoint to delete landing page data
@app.delete("/landing-page/{landingpage_name}", status_code=200, tags=["landingPage"])
async def delete_landingPage(landingpage_name: str, current_user=Depends(is_authenticated), db: Session = Depends(get_db)):
    """
    This endpoint is used to delete landing page data from the database and all images associated with the landing page data
    """
    # check if user is a super user
    if current_user.is_superuser:
        # query for the landing page data
        landingpage_data = db.query(landing_page_models.LPage).filter(
            landing_page_models.LPage.landing_page_name == landingpage_name).first()

        # check if landing page data is found
        if landingpage_data:

            # delete the images from the bucket
            deleteimage = [landingpage_data.content["company_logo"], landingpage_data.content["section_one_image_link"], 
                            landingpage_data.content["body_h3_logo_one"], landingpage_data.content["body_h3_logo_two"],
                            landingpage_data.content["body_h3_logo_three"], landingpage_data.content["body_h3_logo_four"], 
                            landingpage_data.content["section_three_image"], landingpage_data.content["section_four_image"],
                            landingpage_data.content["favicon"], landingpage_data.content["shape_one"], 
                            landingpage_data.content["shape_two"], landingpage_data.content["shape_three"],]
                            
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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
                                'error': "Data could not be found. Please try again."})

    # user is not a super user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={
                            'error': "You are not authorized to perform this action."})




# Function to retrieve landing page images
def image_fullpath(filetype, imagepath):
    if filetype == "image":
        root_location = os.path.abspath("filestorage")
        image_location = os.path.join(root_location, imagepath)
    else:
        root_location1 = pkg_resources.resource_filename(
            "bigfastapi", "/templates/")
        image_location = os.path.join(root_location1, imagepath)
    return FileResponse(image_location)


# Function to get host path to landing page images
def getUrlFullPath(request: Request, filetype: str):
    hostname = request.headers.get('host')
    request = request.url.scheme + "://"
    if hostname == "127.0.0.1:7001":
        hostname = request + hostname
        if filetype == "js":
            image_path = hostname + f"/files/{filetype}"
        elif filetype == "css":
            image_path = hostname + f"/files/{filetype}"

        else:
            image_path = hostname + f"/files/{filetype}"
        return image_path
    else:
        hostname = "https://" + hostname

        if filetype == "js":
            image_path = hostname + f"/files/{filetype}"
        elif filetype == "css":
            image_path = hostname + f"/files/{filetype}"
        else:
            image_path = hostname + f"/files/{filetype}"
        return image_path

