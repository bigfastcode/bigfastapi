import os
from typing import List
from uuid import uuid4

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from bigfastapi.db.database import get_db
from bigfastapi.files import deleteFile, is_file_exist, upload_image
from bigfastapi.models import landing_page_models
from bigfastapi.schemas import landing_page_schemas
from bigfastapi.services import landing_page_services
from bigfastapi.services.auth_service import is_authenticated
from bigfastapi.utils.settings import LANDING_PAGE_FOLDER, LANDING_PAGE_FORM_PATH

app = APIRouter(tags=["Landing Page"])


templates = Jinja2Templates(directory=LANDING_PAGE_FOLDER)

request_fields = [
    "company_name",
    "body_h1",
    "body_h3",
    "body_h3_logo_one_name",
    "body_h3_logo_two_name",
    "body_h3_logo_three_name",
    "body_h3_logo_four_name",
    "body_paragraph",
    "body_h3_logo_one_paragraph",
    "body_h3_logo_two_paragraph",
    "body_h3_logo_three_paragraph",
    "body_h3_logo_four_paragraph",
    "section_three_paragraph",
    "section_three_sub_paragraph",
    "footer_h3",
    "footer_h3_paragraph",
    "footer_name_employee",
    "name_job_description",
    "footer_h2_text",
    "login_link",
    "signup_link",
    "home_link",
    "about_link",
    "faq_link",
    "contact_us_link",
    "footer_contact_address",
    "customer_care_email",
    "title",
]

request_files = [
    "favicon",
    "shape_one",
    "shape_two",
    "shape_three",
    "company_logo",
    "section_one_image_link",
    "body_h3_logo_one",
    "body_h3_logo_two",
    "body_h3_logo_three",
    "body_h3_logo_four",
    "section_three_image",
    "section_four_image",
]

# Endpoint to open index.html
@app.get("/landing-page/index.html")
async def landing_page_index(request: Request, session: Session = Depends(get_db)):
    """
    This endpont will return landing page index.html
    """
    # if current_user:

    return templates.TemplateResponse("index.html", {"request": request})
    # else:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Page not found")


# Endpoint to get landing page images and endpoints
@app.get("/files/{filetype}/{folder}/{image_name}", status_code=200)
def path(
    filetype: str,
    image_name: str,
    folder: str,
    request: Request,
):
    """
    This endpoint is used in the landing page html to fetch images
    """
    if filetype == "css":
        return image_fullpath("css", image_name)
    elif filetype == "js":
        return image_fullpath("js", image_name)
    else:
        return image_fullpath("image", f"{folder}/{image_name}")


# Endpoint to create landing page
@app.post(
    "/landing-page/create",
    status_code=201,
)
async def createlandingpage(
    background_tasks: BackgroundTasks,
    request: landing_page_schemas.landingPageCreate = Depends(
        landing_page_schemas.landingPageCreate.as_form
    ),
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
    shape_three: UploadFile = File(...),
):

    # get all the parameters of the current function in a dictionary
    params = locals()

    # checks if user is a superuser
    if current_user.is_superuser is not True:
        raise HTTPException(
            status_code=403, detail="You are not allowed to perform this action"
        )

    # generates bucket name
    bucket_name = uuid4().hex

    # check if landing page name already exist
    if (
        db.query(landing_page_models.LandingPage)
        .filter(
            landing_page_models.LandingPage.landing_page_name
            == request.landing_page_name
        )
        .first()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="landing_page_name already exist",
        )

    # check if all form fields are filled
    for key, value in vars(request).items():
        if key in request_fields and value == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Please fill all fields"
            )

    other_info = {}

    # check if any required image is missing and raise error else upload image (add to dictionary: other_info)
    for key, value in params.items():
        if key in request_files:
            if not value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Please upload image for {key}",
                )
            other_info[key] = await landing_page_services.upload_images(
                value, db=db, bucket_name=bucket_name
            )

    # map schema to landing page model
    d = await landing_page_services.create_landing_page(
        landing_page_name=request.landing_page_name,
        bucket_name=bucket_name,
        db=db,
        current_user=current_user.id,
    )
    if not d:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="could not be saved"
        )

    # after confirming all fields are available, add them to dictionary (other_info)
    for key, value in vars(request).items():
        if key in request_fields:
            other_info[key] = value

    background_tasks.add_task(
        landing_page_services.add_other_info,
        landing_page_instance=d,
        data=other_info,
        db=db,
    )
    return {"success": "Landing page created"}


# Endpoint to get all landing pages and use the fetch_all_landing_pages function to get the data
@app.get(
    "/landing-page/all",
    status_code=status.HTTP_200_OK,
    response_model=List[landing_page_schemas.landingPageResponse],
)
async def get_all_landing_pages(
    request: Request,
    db: Session = Depends(get_db),
):

    """
    This endpoint will return all landing pages
    """
    # check if user is a superuser
    # if current_user.is_superuser:

    # attempt to get all landing pages from the database
    try:
        landingpages = db.query(landing_page_models.LandingPage).all()
        css_path = getUrlFullPath(request, "css") + "/landing-page/styles.css"
        h = {"css_path": css_path, "landing_page": landingpages}

        # return landingpages
        return templates.TemplateResponse(
            "alllandingpage.html", {"request": request, "h": h}
        )

    # return error if landing pages cannot be fetched
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error fetching data"
        )


# Endpoint to get a single landing page and use the fetch_landing_page function to get the data
@app.get(
    "/landing-page/{landingpage_name}",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def get_landing_page(
    request: Request, landingpage_name: str, db: Session = Depends(get_db)
):
    """
    This endpoint will return a single landing page in html
    """
    # query the database using the landing page name
    landingpage_data = (
        db.query(landing_page_models.LandingPage)
        .filter(landing_page_models.LandingPage.landing_page_name == landingpage_name)
        .first()
    )

    # check if the data is returned and return the data
    image_path = getUrlFullPath(request, "image")
    css_path = getUrlFullPath(request, "css") + "/landing-page/styles.css"
    js_path = getUrlFullPath(request, "js") + "/landing-page/script.js"

    # check if landing page data is returned and extract the data
    if not landingpage_data:
        raise HTTPException(status_code=404, detail="Landing page not found")

    # declare a context dictionary that will be sent to the templating engine
    h = {}

    # update the context dictionary with the requested field info and image paths
    for field in request_fields:
        h[field] = getdicvalue(landingpage_data.id, db=db, key=field)
    for file in request_files:
        h[file] = image_path + getdicvalue(landingpage_data.id, db=db, key=file)

    # update the context dictionary with the landing page name and paths to the js and css
    h["landing_page_name"] = landingpage_data.landing_page_name
    h["css_file"] = css_path
    h["js_file"] = js_path
    h["LANDING_PAGE_FORM_PATH"] = LANDING_PAGE_FORM_PATH

    return templates.TemplateResponse("landingpage.html", {"request": request, "h": h})

    # if no data is returned, throw an error


# Endpoint to update a single landing page and use the update_landing_page function to update the data
@app.put(
    "/landing-page/{landingpage_name}",
    status_code=status.HTTP_200_OK,
    response_model=landing_page_schemas.landingPageResponse,
)
async def update_landing_page(
    landingpage_name: str,
    request: landing_page_schemas.landingPageCreate = Depends(
        landing_page_schemas.landingPageCreate.as_form
    ),
    db: Session = Depends(get_db),
    current_user=Depends(is_authenticated),
    company_logo: UploadFile = File(...),
    section_three_image: UploadFile = File(...),
    section_four_image: UploadFile = File(...),
    section_one_image_link: UploadFile = File(...),
    body_h3_logo_one: UploadFile = File(...),
    body_h3_logo_two: UploadFile = File(...),
    body_h3_logo_three: UploadFile = File(...),
    body_h3_logo_four: UploadFile = File(...),
    shape_one: UploadFile = File(...),
    shape_two: UploadFile = File(...),
    shape_three: UploadFile = File(...),
    favicon: UploadFile = File(...),
):
    """
    This endpoint will update a single landing page in the database with data from the request
    """

    # get all the parameters of the current function in a dictionary
    params = locals()

    # check if the user is superuser
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=404, detail="You are not allowed to perform this action"
        )

    # query the database using the landing page name
    update_landing_page_data = (
        db.query(landing_page_models.LandingPage)
        .filter(landing_page_models.LandingPage.landing_page_name == landingpage_name)
        .first()
    )

    # check if update landing page does not exist, throw an error
    if update_landing_page_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Landing page does not exist"
        )

    # check if the landing page name is not the same as the landing page name in the database, throw an error
    if update_landing_page_data.landing_page_name != request.landing_page_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Landing page name cannot be changed",
        )

    # query and update each of the text fields given in the http request
    for key, value in vars(request).items():
        if (
            key in request_fields
            and getdicvalue(update_landing_page_data.id, db=db, key=key) != value
        ):
            db.query(landing_page_models.LandingPageOtherInfo).filter(
                landing_page_models.LandingPageOtherInfo.value
                == getdicvalue(update_landing_page_data.id, db=db, key=key)
            ).update(
                {
                    landing_page_models.LandingPageOtherInfo.value: func.replace(
                        landing_page_models.LandingPageOtherInfo.value,
                        getdicvalue(update_landing_page_data.id, db=db, key=key),
                        value,
                    )
                },
                synchronize_session=False,
            )

    # query and update each of the file fields given in the http request
    for key, value in params.items():
        if key in request_files and not await is_file_exist(value.filename):
            query = getdicvalue(update_landing_page_data.id, db=db, key=key)
            if await deleteFile(query):
                upload = await upload_image(
                    params[key], db=db, bucket_name=update_landing_page_data.bucket_name
                )
                db.query(landing_page_models.LandingPageOtherInfo).filter(
                    landing_page_models.LandingPageOtherInfo.value == query
                ).update(
                    {
                        landing_page_models.LandingPageOtherInfo.value: func.replace(
                            landing_page_models.LandingPageOtherInfo.value,
                            query,
                            f"/{update_landing_page_data.bucket_name}/{upload}",
                        )
                    },
                    synchronize_session=False,
                )

    # attempt to update the landing page data
    try:
        db.commit()
        db.refresh(update_landing_page_data)
        return update_landing_page_data
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An error occured while updating the landing page data",
        )


# Endpoint to delete landing page data
@app.delete("/landing-page/{landingpage_name}", status_code=200)
async def delete_landingPage(
    landingpage_name: str,
    current_user=Depends(is_authenticated),
    db: Session = Depends(get_db),
):
    """
    This endpoint is used to delete landing page data from the database and all images associated with the landing page data
    """
    # check if user is a super user
    if current_user.is_superuser is not True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "You are not authorized to perform this action."},
        )

    # check if the landing page exists, if not then raise error
    if not (
        landingpage_data := (
            db.query(landing_page_models.LandingPage)
            .filter(
                landing_page_models.LandingPage.landing_page_name == landingpage_name
            )
            .first()
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Data could not be found. Please try again."},
        )
    # delete the images from the bucket
    deleteimage = [
        getdicvalue(landingpage_data.id, db=db, key="body_h3_logo_one"),
        getdicvalue(landingpage_data.id, db=db, key="body_h3_logo_two"),
        getdicvalue(landingpage_data.id, db=db, key="body_h3_logo_three"),
        getdicvalue(landingpage_data.id, db=db, key="body_h3_logo_four"),
        getdicvalue(landingpage_data.id, db=db, key="section_one_image_link"),
        getdicvalue(landingpage_data.id, db=db, key="section_three_image"),
        getdicvalue(landingpage_data.id, db=db, key="section_four_image"),
        getdicvalue(landingpage_data.id, db=db, key="company_logo"),
        getdicvalue(landingpage_data.id, db=db, key="favicon"),
        getdicvalue(landingpage_data.id, db=db, key="shape_one"),
        getdicvalue(landingpage_data.id, db=db, key="shape_two"),
        getdicvalue(landingpage_data.id, db=db, key="shape_three"),
    ]

    other = (
        db.query(landing_page_models.LandingPageOtherInfo)
        .filter(
            landing_page_models.LandingPageOtherInfo.landing_page_id
            == landingpage_data.id
        )
        .delete()
    )

    for i in deleteimage:
        if await deleteFile(i):
            pass
    # delete the landing page data
    db.delete(landingpage_data)
    db.commit()
    return {"message": "Data deleted successfully."}


# returns value of a key
def getdicvalue(landing_id: str, key: str, db: Session = Depends(get_db)):
    other_info = (
        db.query(landing_page_models.LandingPageOtherInfo)
        .filter(
            landing_page_models.LandingPageOtherInfo.landing_page_id == landing_id,
            landing_page_models.LandingPageOtherInfo.key == key,
        )
        .first()
    )
    return other_info.value


# Function to retrieve landing page images
def image_fullpath(filetype, imagepath):
    if filetype == "image":
        root_location = os.path.abspath("filestorage/images")
        image_location = os.path.join(root_location, imagepath)
    else:
        root_location1 = os.path.abspath(LANDING_PAGE_FOLDER)
        image_location = os.path.join(root_location1, imagepath)
    return FileResponse(image_location)


# Function to get host path to landing page images
def getUrlFullPath(request: Request, filetype: str):
    hostname = request.headers.get("host")
    request = f"{request.url.scheme}://"
    if hostname == "127.0.0.1:7001":
        hostname = request + hostname
    else:
        hostname = f"https://{hostname}"

    return f"{hostname}/files/{filetype}"
