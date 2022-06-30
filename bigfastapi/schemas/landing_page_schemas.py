"""
    The @as_form_schema decorator is used to convert a class into a a form schema.
    To use it you need to import it from bigfastapi.utils.schema_form
"""

from pydantic import BaseModel
from bigfastapi.utils.schema_form import as_form

@as_form
class landingPageCreate(BaseModel): 

    landing_page_name: str
    title: str
    company_name: str 
    home_link: str
    about_link: str
    faq_link: str
    contact_us_link: str
    body_h1: str 
    body_paragraph: str
    login_link: str 
    signup_link: str
    body_h3: str
    body_h3_logo_one_name: str
    body_h3_logo_two_name: str
    body_h3_logo_three_name: str
    body_h3_logo_four_name: str
    body_h3_logo_one_paragraph: str
    body_h3_logo_two_paragraph: str
    body_h3_logo_three_paragraph: str
    body_h3_logo_four_paragraph: str
    section_three_paragraph: str

    section_three_sub_paragraph: str
    footer_h3: str
    footer_h3_paragraph: str
    footer_name_employee: str
    name_job_description: str
    footer_h2_text: str
    footer_contact_address: str
    customer_care_email: str
    class Config:
        orm_mode = True


class landingPageResponse(BaseModel): 
 
    id : str
    user_id : str
    landing_page_name : str
    class Config:
        orm_mode = True

