
from uuid import uuid4
import datetime as datetime
from sqlalchemy import ForeignKey
import bigfastapi.db.database as db
import sqlalchemy.orm as orm
from sqlalchemy.schema import Column, Table
from sqlalchemy.types import String, DateTime, JSON





class LPage(db.Base):
  __tablename__ = 'landing_page'
  id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
  user_id = Column(String(255), ForeignKey("users.id"))
  landing_page_name = Column(String(255), index=True, unique=True)
  content = Column('data', JSON)
  date_created = Column(DateTime, default=datetime.datetime.utcnow)
  last_updated = Column(DateTime, default=datetime.datetime.utcnow)


# class LPage(db.Base):
#   __tablename__ = 'landing_page'

#   id = Column(String(255), primary_key=True, index=True)
#   user_id = Column(String(255), ForeignKey('users.id'), nullable=False)
#   landing_page_name = Column(String(255), index=True, unique=True)
#   title = Column(String(255), default="landing page")
#   bucket_name = Column(String(255), index=True, unique=True)
#   company_name = Column(String(255), nullable=False) 
#   favicon = Column(String(255))
#   shape_one = Column(String(255))
#   shape_two = Column(String(255))
#   shape_three = Column(String(255))
#   login_link = Column(String(255))
#   signup_link = Column(String(255))
#   company_logo = Column(String(255)) 
#   home_link = Column(String(255))
#   about_link = Column(String(255)) 
#   faq_link = Column(String(255)) 
#   contact_us_link = Column(String(255)) 
#   body_h1 = Column(String(255)) 
#   body_paragraph = Column(String(255)) 
#   section_one_image_link = Column(String(255)) 
#   body_h3 = Column(String(255)) 
#   body_h3_logo_one = Column(String(255)) 
#   body_h3_logo_one_name = Column(String(255))
#   body_h3_logo_one_paragraph = Column(String(255))
#   body_h3_logo_two = Column(String(255))
#   body_h3_logo_two_name = Column(String(255))
#   body_h3_logo_two_paragraph = Column(String(255))
#   body_h3_logo_three = Column(String(255))
#   body_h3_logo_three_name = Column(String(255))
#   body_h3_logo_three_paragraph = Column(String(255))
#   body_h3_logo_four = Column(String(255))
#   body_h3_logo_four_name = Column(String(255))
#   body_h3_logo_four_paragraph = Column(String(255))
#   section_three_paragraph = Column(String(255))
#   section_three_sub_paragraph = Column(String(255))
#   section_three_image= Column(String(255))
#   footer_h3 = Column(String(255))
#   footer_h3_paragraph= Column(String(255))
#   footer_name_employee= Column(String(255))
#   name_job_description= Column(String(255))
#   section_four_image = Column(String(255))
#   footer_h2_text = Column(String(255))
#   footer_contact_address = Column(String(255))
#   customer_care_email = Column(String(255))