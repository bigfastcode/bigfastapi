

from sqlalchemy.schema import Column
from sqlalchemy.types import String
from uuid import uuid4
from bigfastapi.db.database import Base


class Menu(Base):
    __tablename__ = "menus"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    orgaization_id = Column(String(255), index=True)
    active_menu = Column(String(2000), default="")
    more = Column(String(2000), default="")
    menu_list = Column(String(2000), default="")
