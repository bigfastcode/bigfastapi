from pydantic import BaseModel
from typing import Optional
import datetime as _dt
from bigfastapi.utils.schema_form import as_form

@as_form
class landingPageCreate(BaseModel): 

    landingPage_name: str
    # header content
    company_Name: str 
    Home_link: str
    About_link: str
    faq_link: str
    contact_us_link: str

    # Body content
    Body_H1: str 
    Body_paragraph: str
    login_link: str 
    signup_link: str
    # Body content 2
    Body_H3: str
    Body_H3_logo_One_name: str
    Body_H3_logo_Two_name: str
    Body_H3_logo_Three_name: str
    Body_H3_logo_Four_name: str
    Body_H3_logo_One_paragraph: str
    Body_H3_logo_Two_paragraph: str
    Body_H3_logo_Three_paragraph: str
    Body_H3_logo_Four_paragraph: str
    # Body content 3
    section_Three_paragraph: str

    section_Three_sub_paragraph: str
    # Body content 4
    Footer_H3: str
    Footer_H3_paragraph: str
    Footer_name_employee: str
    Name_job_description: str
    # Body content 5
    Footer_H2_text: str
    # Footer content
    Footer_contact_address: str
    customer_care_email: str




    

class landingPagecompanylogo(landingPageCreate):
    company_logo: str

class landingPagesection_One_image_link(landingPagecompanylogo):
    section_One_image_link: str

class landingPageBody_H3_logo_One(landingPagesection_One_image_link):
    Body_H3_logo_One: str

class landingPageBody_H3_logo_Two(landingPageBody_H3_logo_One):
    Body_H3_logo_Two: str

class landingPageBody_H3_logo_Three(landingPageBody_H3_logo_Two):
    Body_H3_logo_Three: str

class landingPageBody_H3_logo_Four(landingPageBody_H3_logo_Three):
    Body_H3_logo_Four: str

class landingPagesection_Three_image(landingPageBody_H3_logo_Four):
    section_Three_image: str

class landingPagesection_Four_image(landingPagesection_Three_image):
    Section_Four_image: str

    class Config:
        orm_mode = True


class landingPageResponse(BaseModel): 
    landingPage_name: str
    company_Name: str 
    Home_link: str
    About_link: str
    faq_link: str
    contact_us_link: str
    Body_H1: str 
    Body_paragraph: str
    login_link: str 
    signup_link: str
    Body_H3: str
    Body_H3_logo_One_name: str
    Body_H3_logo_Two_name: str
    Body_H3_logo_Three_name: str
    Body_H3_logo_Four_name: str
    Body_H3_logo_One_paragraph: str
    Body_H3_logo_Two_paragraph: str
    Body_H3_logo_Three_paragraph: str
    Body_H3_logo_Four_paragraph: str
    section_Three_paragraph: str
    section_Three_sub_paragraph: str
    Footer_H3: str
    Footer_H3_paragraph: str
    Footer_name_employee: str
    Name_job_description: str
    Footer_H2_text: str
    Footer_contact_address: str
    customer_care_email: str

    company_logo: str
    section_One_image_link: str
    Body_H3_logo_One: str
    Body_H3_logo_Two: str
    Body_H3_logo_Three: str
    Body_H3_logo_Four: str
    section_Three_image: str
    section_Four_image: str
    
    class Config:
        orm_mode = True

