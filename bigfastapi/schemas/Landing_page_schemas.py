"""
    The @as_form_schema decorator is used to convert a class into a a form schema.
    To use it you need to import it from bigfastapi.utils.schema_form
"""

from pydantic import BaseModel
from typing import Optional
import datetime as _dt
from bigfastapi.utils.schema_form import as_form

@as_form
class landingPageCreate(BaseModel): 

    landing_page_name: str
    # header content
    company_name: str 
    home_link: str
    about_link: str
    faq_link: str
    contact_us_link: str

    # Body content
    body_h1: str 
    body_paragraph: str
    login_link: str 
    signup_link: str
    # body content 2
    body_h3: str
    body_h3_logo_one_name: str
    body_h3_logo_two_name: str
    body_h3_logo_three_name: str
    body_h3_logo_four_name: str
    body_h3_logo_one_paragraph: str
    body_h3_logo_two_paragraph: str
    body_h3_logo_three_paragraph: str
    body_h3_logo_four_paragraph: str
    # Body content 3
    section_three_paragraph: str

    section_three_sub_paragraph: str
    # Body content 4
    footer_h3: str
    footer_h3_paragraph: str
    footer_name_employee: str
    name_job_description: str
    # Body content 5
    footer_h2_text: str
    # Footer content
    footer_contact_address: str
    customer_care_email: str




    

class landingPagecompanylogo(landingPageCreate):
    company_logo: str

class landingPagesection_One_image_link(landingPagecompanylogo):
    section_one_image_link: str

class landingPageBody_H3_logo_One(landingPagesection_One_image_link):
    body_h3_logo_one: str

class landingPageBody_H3_logo_Two(landingPageBody_H3_logo_One):
    body_h3_logo_two: str

class landingPageBody_H3_logo_Three(landingPageBody_H3_logo_Two):
    body_h3_logo_three: str

class landingPageBody_H3_logo_Four(landingPageBody_H3_logo_Three):
    body_h3_logo_four: str

class landingPagesection_Three_image(landingPageBody_H3_logo_Four):
    section_three_image: str

class landingPagesection_Four_image(landingPagesection_Three_image):
    section_four_image: str

    class Config:
        orm_mode = True


class landingPageResponse(BaseModel): 
    landing_page_name: str
    # header content
    company_name: str 
    home_link: str
    about_link: str
    faq_link: str
    contact_us_link: str

    # Body content
    body_h1: str 
    body_paragraph: str
    login_link: str 
    signup_link: str
    # body content 2
    body_h3: str
    body_h3_logo_one_name: str
    body_h3_logo_two_name: str
    body_h3_logo_three_name: str
    body_h3_logo_four_name: str
    body_h3_logo_one_paragraph: str
    body_h3_logo_two_paragraph: str
    body_h3_logo_three_paragraph: str
    body_h3_logo_four_paragraph: str
    # Body content 3
    section_three_paragraph: str

    section_three_sub_paragraph: str
    # Body content 4
    footer_h3: str
    footer_h3_paragraph: str
    footer_name_employee: str
    name_job_description: str
    # Body content 5
    footer_h2_text: str
    # Footer content
    footer_contact_address: str
    customer_care_email: str
    company_logo: str
    section_one_image_link: str
    body_h3_logo_one: str
    body_h3_logo_two: str
    body_h3_logo_three: str
    body_h3_logo_four: str
    section_three_image: str
    section_four_image: str
    class Config:
        orm_mode = True

