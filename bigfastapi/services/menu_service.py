

import json
from uuid import uuid4
from fastapi import HTTPException
import sqlalchemy.orm as orm
import pkg_resources
import json

from bigfastapi.models.menu_models import Menu


MENU_JSON_PATH = pkg_resources.resource_filename(
    'bigfastapi', 'data\menu.json')


#  ADD Default menu setting per organization
def add_default_menu_list(orgorganization_id: str, business_type: str, db: orm.Session):
    composit_menu_list = get_default_menu_object(False)
    dafult_more_list = composit_menu_list['more']
    active_menu_list = composit_menu_list[business_type]
    default_menu_list = composit_menu_list
    default_menu_list.pop('more')

# Create a default menu construct
    menu_construct = Menu(
        id=uuid4().hex, orgaization_id=orgorganization_id,
        active_menu=json.dumps(active_menu_list), more=json.dumps(dafult_more_list),
        menu_list=json.dumps(default_menu_list))

    db.add(menu_construct)
    db.commit()
    db.refresh(menu_construct)

    return {
        "active_menu": menu_construct.active_menu,
        "more_list":  menu_construct.more,
        "menu_list": menu_construct.menu_list
    }


#  GET organization menu
def get_organization_menu(org_id: str, db: orm.Session):
    org_menu = db.query(Menu).filter(Menu.orgaization_id == org_id).first()
    if org_menu:
        return org_menu
    else:
        return add_default_menu_list(org_id, 'retail', db)


#  MODIFY AND RESET Menu more list
def modify_menu_more_list(menu_item: str, is_adding: bool, db: orm.Session):
    # First retrieve the default menu setting from file
    menu_orj = get_default_menu_object(False)
    more_list = menu_orj['more']
    updated_more_list = []
    #  Add or remove menu item from menu list
    if is_adding:
        updated_more_list = more_list.append(menu_item)
    else:
        updated_more_list = more_list.remove(menu_item)

    db_update_response = persist_new_menu_more_list(updated_more_list, db)

    if db_update_response:
        menu_orj['more'] = updated_more_list
        # convert updated menu list to json
        update_menu_json_list = json.dumps(menu_orj)
        # Persist update menu list in json file
        menu_IOWrapper = open(MENU_JSON_PATH, 'w')
        menu_IOWrapper.write(update_menu_json_list)
        menu_IOWrapper.close
    else:
        raise HTTPException(status_code=500, detail=str(e))


# Update all more column in menus table
def persist_new_menu_more_list(updated_more_list: list[str], db: orm.Session):
    more_list_as_json = json.dumps(updated_more_list)
    try:
        org_menu = db.query(Menu).update({"more": more_list_as_json})
        db.Commit()
        return True
    except Exception as e:
        print("Menu Update Error = " + str(e))
        raise False


# GET default menu setup from json file
def get_default_menu_object(is_json: bool):
    # extract default menu from json file
    menu_IOWrapper = open(MENU_JSON_PATH, 'r')
    menu_as_json = menu_IOWrapper.read()
    menu_IOWrapper.close()
    # return json or object base on is_json flag
    return menu_as_json if is_json else json.loads(menu_as_json)
