

import json
import sqlalchemy.orm as orm
import pkg_resources
import json


MENU_JSON_PATH = pkg_resources.resource_filename(
    'bigfastapi', 'data\menu.json')


def update_json_more_menu(menu_item: str, is_adding: bool):
    # First retrieve the default menu setting from file
    menu_file = open(MENU_JSON_PATH,  'r')
    menu_as_json = menu_file.read()
    menu_file.close()
    # convert json to dict
    menu_orj = json.loads(menu_as_json)
    more_list = menu_orj['more']

    if is_adding:
        updated_more_list = more_list.append(menu_item)
    else:
        updated_more_list = more_list.remove(menu_item)

    menu_orj['more'] = updated_more_list
    # convert updated menu list to json
    update_menu_json_list = json.dumps(menu_orj)


def add_new_menu_item(menu_item: str, db: orm.Session):
    # First retrieve the default menu setting from file
    menu_file = open(MENU_JSON_PATH 'r')
    menu_as_json = menu_file.read()
    # convert json to dict
    menu_orj = json.loads(menu_as_json)
