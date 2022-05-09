
from sqlalchemy import ForeignKey, null
import bigfastapi.db.database as db
import sqlalchemy.orm as orm
from sqlalchemy.schema import Column
from sqlalchemy.types import String


class LPage(db.Base):
  __tablename__ = 'landing_page'

  id = Column(String(255), primary_key=True, index=True)
  user_id = Column(String(255), ForeignKey('users.id'), nullable=False)
  landing_page_name = Column(String(255), index=True, unique=True)
  bucket_name = Column(String(255), index=True, unique=True)
  company_name = Column(String(255), nullable=False) # company_name 
  login_link = Column(String(255))
  signup_link = Column(String(255))
  company_logo = Column(String(255)) # image url
  home_link = Column(String(255)) # home link
  about_link = Column(String(255)) # about link
  faq_link = Column(String(255)) # faq link
  contact_us_link = Column(String(255)) # contact us link
  body_h1 = Column(String(255)) # body title
  body_paragraph = Column(String(255)) # body content text
  section_one_image_link = Column(String(255)) # body content logo one
  body_h3 = Column(String(255)) # body title subtext
  body_h3_logo_one = Column(String(255)) # body title image
  body_h3_logo_one_name = Column(String(255))
  body_h3_logo_one_paragraph = Column(String(255))
  body_h3_logo_two = Column(String(255))
  body_h3_logo_two_name = Column(String(255))
  body_h3_logo_two_paragraph = Column(String(255))
  body_h3_logo_three = Column(String(255))
  body_h3_logo_three_name = Column(String(255))
  body_h3_logo_three_paragraph = Column(String(255))
  body_h3_logo_four = Column(String(255))
  body_h3_logo_four_name = Column(String(255))
  body_h3_logo_four_paragraph = Column(String(255))
  section_three_paragraph = Column(String(255))
  section_three_sub_paragraph = Column(String(255))
  section_three_image= Column(String(255))
  footer_h3 = Column(String(255))
  footer_h3_paragraph= Column(String(255))
  footer_name_employee= Column(String(255))
  name_job_description= Column(String(255))
  section_four_image = Column(String(255))
  footer_h2_text = Column(String(255))
  footer_contact_address = Column(String(255))
  customer_care_email = Column(String(255))



