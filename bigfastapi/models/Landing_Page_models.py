
from sqlalchemy import ForeignKey, null
import bigfastapi.db.database as db
import sqlalchemy.orm as orm
from sqlalchemy.schema import Column
from sqlalchemy.types import String


class LPage(db.Base):
  __tablename__ = 'Landing_page'
  id = Column(String(255), primary_key=True, index=True)
  user_id = Column(String(255), ForeignKey('users.id'), nullable=False)
  landingPage_name = Column(String(255), index=True, unique=True)
  Bucket_name = Column(String(255), index=True, unique=True)
  company_Name = Column(String(255), nullable=False) # company_Name 
  login_link = Column(String(255))
  signup_link = Column(String(255))
  company_logo = Column(String(255)) # image url
  Home_link = Column(String(255)) # home link
  About_link = Column(String(255)) # about link
  faq_link = Column(String(255)) # faq link
  contact_us_link = Column(String(255)) # contact us link
  Body_H1 = Column(String(255)) # body title
  Body_paragraph = Column(String) # body content text
  section_One_image_link = Column(String(255)) # body content logo one
  Body_H3 = Column(String(255)) # body title subtext
  Body_H3_logo_One = Column(String(255)) # body title image
  Body_H3_logo_One_name = Column(String(255))
  Body_H3_logo_One_paragraph = Column(String(255))
  Body_H3_logo_Two = Column(String(255))
  Body_H3_logo_Two_name = Column(String(255))
  Body_H3_logo_Two_paragraph = Column(String(255))
  Body_H3_logo_Three = Column(String(255))
  Body_H3_logo_Three_name = Column(String(255))
  Body_H3_logo_Three_paragraph = Column(String(255))
  Body_H3_logo_Four = Column(String(255))
  Body_H3_logo_Four_name = Column(String(255))
  Body_H3_logo_Four_paragraph = Column(String(255))
  section_Three_paragraph = Column(String(255))
  section_Three_sub_paragraph = Column(String(255))
  section_Three_image= Column(String(255))
  Footer_H3 = Column(String(255))
  Footer_H3_paragraph= Column(String(255))
  Footer_name_employee= Column(String(255))
  Name_job_description= Column(String(255))
  section_Four_image = Column(String)
  Footer_H2_text = Column(String(255))
  Footer_contact_address = Column(String(255))
  customer_care_email = Column(String(255))


# find landing page by landing page name
def find_landing_page(landingPage_name: str, db: orm.Session):
  return db.query(LPage).filter((LPage.landingPage_name == landingPage_name)).first()




# delete landing page by landing page name
def delete_landing_page(landingPage_id: str, db: orm.Session):
  landing_page = find_landing_page(landingPage_id, db)
  if landing_page:
    db.delete(landing_page)
    db.commit()
    return True
  return False