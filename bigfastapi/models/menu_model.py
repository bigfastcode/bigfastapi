
import json
import sqlalchemy.orm as _orm
from sqlalchemy.schema import Column
from sqlalchemy.types import String
from uuid import uuid4
from bigfastapi.db.database import Base
from bigfastapi.utils.utils import defaultManu


class Menu(Base):
    __tablename__ = "menus"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    orgaization_id = Column(String(255), index=True)
    active_menu = Column(String(2000), default="")
    menu_list = Column(String(2000), default="")


# --------------------------------------------------------------------------------------------------#
#                                    REPOSITORY LAYER
# --------------------------------------------------------------------------------------------------#


def getActiveMenu(businessType):
    menuList = defaultManu()
    return json.dumps(menuList[businessType])


def addDefaultMenuList(orgId: str, business_type: str, db: _orm.Session):
    menuConstruct = Menu(id=uuid4().hex, orgaization_id=orgId,
                         menu_list=json.dumps(defaultManu()),
                         active_menu=getActiveMenu(business_type))
    db.add(menuConstruct)
    db.commit()
    db.refresh(menuConstruct)
    return {"active_menu": menuConstruct.active_menu, "menu_list": menuConstruct.menu_list}


def getOrgMenu(orgId: str, db: _orm.Session):
    organizationMenu = db.query(Menu).filter(
        Menu.orgaization_id == orgId).first()
    if organizationMenu:
        return organizationMenu
    else:
        # Add Default Menu
        return addDefaultMenuList(orgId, 'retail', db)
