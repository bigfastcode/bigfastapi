
from sqlalchemy import ForeignKey, null
import bigfastapi.db.database as db
import sqlalchemy.orm as orm
from sqlalchemy.schema import Column
from sqlalchemy.types import String


class LPage(db.Base):
  __tablename__ = 'Landing_page'

  id = Column(String(500), primary_key=True, index=True)
  user_id = Column(String(500), ForeignKey('users.id'), nullable=False)
  landingPage_name = Column(String(500), index=True, unique=True)
  Bucket_name = Column(String(500), index=True, unique=True)
  company_Name = Column(String(500), nullable=False) # company_Name 
  login_link = Column(String(500))
  signup_link = Column(String(500))
  company_logo = Column(String(500)) # image url
  Home_link = Column(String(500)) # home link
  About_link = Column(String(500)) # about link
  faq_link = Column(String(500)) # faq link
  contact_us_link = Column(String(500)) # contact us link
  Body_H1 = Column(String(500)) # body title
  Body_paragraph = Column(String(500)) # body content text
  section_One_image_link = Column(String(500)) # body content logo one
  Body_H3 = Column(String(500)) # body title subtext
  Body_H3_logo_One = Column(String(500)) # body title image
  Body_H3_logo_One_name = Column(String(500))
  Body_H3_logo_One_paragraph = Column(String(500))
  Body_H3_logo_Two = Column(String(500))
  Body_H3_logo_Two_name = Column(String(500))
  Body_H3_logo_Two_paragraph = Column(String(500))
  Body_H3_logo_Three = Column(String(500))
  Body_H3_logo_Three_name = Column(String(500))
  Body_H3_logo_Three_paragraph = Column(String(500))
  Body_H3_logo_Four = Column(String(500))
  Body_H3_logo_Four_name = Column(String(500))
  Body_H3_logo_Four_paragraph = Column(String(500))
  section_Three_paragraph = Column(String(500))
  section_Three_sub_paragraph = Column(String(500))
  section_Three_image= Column(String(500))
  Footer_H3 = Column(String(500))
  Footer_H3_paragraph= Column(String(500))
  Footer_name_employee= Column(String(500))
  Name_job_description= Column(String(500))
  section_Four_image = Column(String(500))
  Footer_H2_text = Column(String(500))
  Footer_contact_address = Column(String(500))
  customer_care_email = Column(String(500))



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